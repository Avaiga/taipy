# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import contextlib
import logging
import os
import pathlib
import re
import sys
import time
import typing as t
import webbrowser
from importlib import util
from random import choices, randint

from flask import Blueprint, Flask, json, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from gitignore_parser import parse_gitignore
from kthread import KThread
from werkzeug.serving import is_running_from_reloader

import __main__
from taipy.common.logger._taipy_logger import _TaipyLogger

from ._renderers.json import _TaipyJsonProvider
from .config import ServerConfig
from .custom._page import _ExternalResourceHandlerManager
from .utils import _is_in_notebook, _is_port_open, _RuntimeManager
from .utils._css import get_style

if t.TYPE_CHECKING:
    from .gui import Gui


class _Server:
    __RE_OPENING_CURLY = re.compile(r"([^\"])(\{)")
    __RE_CLOSING_CURLY = re.compile(r"(\})([^\"])")
    __OPENING_CURLY = r"\1&#x7B;"
    __CLOSING_CURLY = r"&#x7D;\2"
    _RESOURCE_HANDLER_ARG = "tprh"

    def __init__(
        self,
        gui: Gui,
        flask: t.Optional[Flask] = None,
        path_mapping: t.Optional[dict] = None,
        async_mode: t.Optional[str] = None,
        allow_upgrades: bool = True,
        server_config: t.Optional[ServerConfig] = None,
    ):
        self._gui = gui
        server_config = server_config or {}
        self._flask = flask
        if self._flask is None:
            flask_config: t.Dict[str, t.Any] = {"import_name": "Taipy"}
            if "flask" in server_config and isinstance(server_config["flask"], dict):
                flask_config.update(server_config["flask"])
            self._flask = Flask(**flask_config)
        if "SECRET_KEY" not in self._flask.config or not self._flask.config["SECRET_KEY"]:
            self._flask.config["SECRET_KEY"] = "TaIpY"

        # setup cors
        if "cors" not in server_config or (
            "cors" in server_config and (isinstance(server_config["cors"], dict) or server_config["cors"] is True)
        ):
            cors_config = (
                server_config["cors"] if "cors" in server_config and isinstance(server_config["cors"], dict) else {}
            )
            CORS(self._flask, **cors_config)

        # setup socketio
        socketio_config: t.Dict[str, t.Any] = {
            "cors_allowed_origins": "*",
            "ping_timeout": 10,
            "ping_interval": 5,
            "json": json,
            "async_mode": async_mode,
            "allow_upgrades": allow_upgrades,
        }
        if "socketio" in server_config and isinstance(server_config["socketio"], dict):
            socketio_config.update(server_config["socketio"])
        self._ws = SocketIO(self._flask, **socketio_config)

        self._apply_patch()

        # set json encoder (for Taipy specific types)
        self._flask.json_provider_class = _TaipyJsonProvider
        self._flask.json = self._flask.json_provider_class(self._flask)  # type: ignore

        self.__path_mapping = path_mapping or {}
        self.__ssl_context = server_config.get("ssl_context", None)
        self._is_running = False

        # Websocket (handle json message)
        # adding args for the one call with a server ack request
        @self._ws.on("message")
        def handle_message(message, *args) -> None:
            if "status" in message:
                _TaipyLogger._get_logger().info(message["status"])
            elif "type" in message:
                gui._manage_message(message["type"], message)

        @self._ws.on("connect")
        def handle_connect():
            gui._handle_connect()

        @self._ws.on("disconnect")
        def handle_disconnect():
            gui._handle_disconnect()

    def __is_ignored(self, file_path: str) -> bool:
        if not hasattr(self, "_ignore_matches"):
            __IGNORE_FILE = ".taipyignore"
            ignore_file = (
                (pathlib.Path(__main__.__file__).parent / __IGNORE_FILE) if hasattr(__main__, "__file__") else None
            )
            if not ignore_file or not ignore_file.is_file():
                ignore_file = pathlib.Path(self._gui._root_dir) / __IGNORE_FILE
            self._ignore_matches = (
                parse_gitignore(ignore_file) if ignore_file.is_file() and os.access(ignore_file, os.R_OK) else None
            )

        if callable(self._ignore_matches):
            return self._ignore_matches(file_path)
        return False

    def _get_default_blueprint(
        self,
        static_folder: str,
        template_folder: str,
        title: str,
        favicon: str,
        root_margin: str,
        scripts: t.List[str],
        styles: t.List[str],
        version: str,
        client_config: t.Dict[str, t.Any],
        watermark: t.Optional[str],
        css_vars: str,
        base_url: str,
    ) -> Blueprint:
        taipy_bp = Blueprint("Taipy", __name__, static_folder=static_folder, template_folder=template_folder)
        # Serve static react build

        @taipy_bp.route("/", defaults={"path": ""})
        @taipy_bp.route("/<path:path>")
        def my_index(path):
            resource_handler_id = request.cookies.get(_Server._RESOURCE_HANDLER_ARG, None)
            if resource_handler_id is not None:
                resource_handler = _ExternalResourceHandlerManager().get(resource_handler_id)
                if resource_handler is None:
                    return (f"Invalid value for query {_Server._RESOURCE_HANDLER_ARG}", 404)
                try:
                    return resource_handler.get_resources(path, static_folder, base_url)
                except Exception as e:
                    raise RuntimeError("Can't get resources from custom resource handler") from e
            if path == "" or path == "index.html" or "." not in path:
                try:
                    return render_template(
                        "index.html",
                        title=title,
                        favicon=f"{favicon}?version={version}",
                        root_margin=root_margin,
                        watermark=watermark,
                        config=client_config,
                        scripts=scripts,
                        styles=styles,
                        version=version,
                        css_vars=css_vars,
                        base_url=base_url,
                    )
                except Exception:
                    raise RuntimeError(
                        "Something is wrong with the taipy-gui front-end installation. Check that the js bundle has been properly built (is Node.js installed?)."  # noqa: E501
                    ) from None

            if path == "taipy.status.json":
                return self._direct_render_json(self._gui._serve_status(pathlib.Path(template_folder) / path))
            if (file_path := str(os.path.normpath((base_path := static_folder + os.path.sep) + path))).startswith(
                base_path
            ) and os.path.isfile(file_path):
                return send_from_directory(base_path, path)
            # use the path mapping to detect and find resources
            for k, v in self.__path_mapping.items():
                if (
                    path.startswith(f"{k}/")
                    and (
                        file_path := str(os.path.normpath((base_path := v + os.path.sep) + path[len(k) + 1 :]))
                    ).startswith(base_path)
                    and os.path.isfile(file_path)
                ):
                    return send_from_directory(base_path, path[len(k) + 1 :])
            if (
                hasattr(__main__, "__file__")
                and (
                    file_path := str(
                        os.path.normpath((base_path := os.path.dirname(__main__.__file__) + os.path.sep) + path)
                    )
                ).startswith(base_path)
                and os.path.isfile(file_path)
                and not self.__is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            if (
                (
                    file_path := str(os.path.normpath((base_path := self._gui._root_dir + os.path.sep) + path))
                ).startswith(base_path)
                and os.path.isfile(file_path)
                and not self.__is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            return ("", 404)

        return taipy_bp

    # Update to render as JSX
    def _render(self, html_fragment, style, head, context):
        template_str = _Server.__RE_OPENING_CURLY.sub(_Server.__OPENING_CURLY, html_fragment)
        template_str = _Server.__RE_CLOSING_CURLY.sub(_Server.__CLOSING_CURLY, template_str)
        template_str = template_str.replace('"{!', "{")
        template_str = template_str.replace('!}"', "}")
        style = get_style(style)
        return self._direct_render_json(
            {
                "jsx": template_str,
                "style": (style + os.linesep) if style else "",
                "head": head or [],
                "context": context or self._gui._get_default_module_name(),
            }
        )

    def _direct_render_json(self, data):
        return jsonify(data)

    def get_flask(self):
        return self._flask

    def get_port(self):
        return self._port

    def test_client(self):
        return t.cast(Flask, self._flask).test_client()

    def _run_notebook(self):
        self._is_running = True
        self._ws.run(self._flask, host=self._host, port=self._port, debug=False, use_reloader=False)

    def _get_async_mode(self) -> str:
        return self._ws.async_mode  # type: ignore[reportAttributeAccessIssue]

    def _apply_patch(self):
        if self._get_async_mode() == "gevent" and util.find_spec("gevent"):
            from gevent import get_hub, monkey

            get_hub().NOT_ERROR += (KeyboardInterrupt,)
            if not monkey.is_module_patched("time"):
                monkey.patch_time()
        if self._get_async_mode() == "eventlet" and util.find_spec("eventlet"):
            from eventlet import monkey_patch, patcher  # type: ignore[reportMissingImport]

            if not patcher.is_monkey_patched("time"):
                monkey_patch(time=True)

    def _get_random_port(
        self, port_auto_ranges: t.Optional[t.List[t.Union[int, t.Tuple[int, int]]]] = None
    ):  # pragma: no cover
        port_auto_ranges = port_auto_ranges or [(49152, 65535)]
        random_weights = [1 if isinstance(r, int) else abs(r[1] - r[0]) + 1 for r in port_auto_ranges]
        while True:
            random_choices = [
                r if isinstance(r, int) else randint(min(r[0], r[1]), max(r[0], r[1])) for r in port_auto_ranges
            ]
            port = choices(random_choices, weights=random_weights)[0]
            if port not in _RuntimeManager().get_used_port() and not _is_port_open(self._host, port):
                return port

    def run(
        self,
        host,
        port,
        client_url,
        debug,
        use_reloader,
        flask_log,
        run_in_thread,
        allow_unsafe_werkzeug,
        notebook_proxy,
        port_auto_ranges,
    ):
        host_value = host if host != "0.0.0.0" else "localhost"
        self._host = host
        if port == "auto":
            port = self._get_random_port(port_auto_ranges)
        self._port = port
        client_url = client_url.format(port=port)
        if _is_in_notebook() and notebook_proxy:  # pragma: no cover
            from .utils.proxy import NotebookProxy

            # Start proxy if not already started
            self._proxy = NotebookProxy(gui=self._gui, listening_port=port)
            self._proxy.run()
            self._port = self._get_random_port()
        if _is_in_notebook() or run_in_thread:
            runtime_manager = _RuntimeManager()
            runtime_manager.add_gui(self._gui, port)
        if debug and not is_running_from_reloader() and _is_port_open(host_value, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host} because another application is running on the same port.\nPlease pick another port number and rerun with the 'port=<new_port>' setting.\nYou can also let Taipy choose a port number for you by running with the 'port=\"auto\"' setting."  # noqa: E501
            )
        if not flask_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
            if not is_running_from_reloader():
                _TaipyLogger._get_logger().info(f" * Server starting on http://{host_value}:{port}")
            else:
                _TaipyLogger._get_logger().info(f" * Server reloaded on http://{host_value}:{port}")
            _TaipyLogger._get_logger().info(f" * Application is accessible at {client_url}")
        if not is_running_from_reloader() and self._gui._get_config("run_browser", False):
            webbrowser.open(client_url, new=2)
        if _is_in_notebook() or run_in_thread:
            self._thread = KThread(target=self._run_notebook)
            self._thread.start()
            return
        self._is_running = True
        run_config = {
            "app": self._flask,
            "host": host,
            "port": port,
            "debug": debug,
            "use_reloader": use_reloader,
        }
        if self.__ssl_context is not None:
            run_config["ssl_context"] = self.__ssl_context
        # flask-socketio specific conditions for 'allow_unsafe_werkzeug' parameters to be popped out of kwargs
        if self._get_async_mode() == "threading" and (not sys.stdin or not sys.stdin.isatty()):
            run_config = {**run_config, "allow_unsafe_werkzeug": allow_unsafe_werkzeug}
        try:
            self._ws.run(**run_config)
        except KeyboardInterrupt:
            pass

    def stop_thread(self):
        if hasattr(self, "_thread") and self._thread.is_alive() and self._is_running:
            self._is_running = False
            with contextlib.suppress(Exception):
                if self._get_async_mode() == "gevent":
                    if self._ws.wsgi_server is not None:  # type: ignore[reportAttributeAccessIssue]
                        self._ws.wsgi_server.stop()  # type: ignore[reportAttributeAccessIssue]
                    else:
                        self._thread.kill()
                else:
                    self._thread.kill()
            while _is_port_open(self._host, self._port):
                time.sleep(0.1)

    def stop_proxy(self):
        if hasattr(self, "_proxy"):
            self._proxy.stop()
