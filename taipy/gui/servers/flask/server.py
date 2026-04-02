# Copyright 2021-2025 Avaiga Private Limited
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
import sys
import time
import typing as t
import webbrowser
from contextlib import contextmanager
from importlib import util

from flask import (
    Blueprint,
    Flask,
    has_app_context,
    json,
    jsonify,
    render_template,
    send_file,
    send_from_directory,
)
from flask.json.provider import DefaultJSONProvider  # type: ignore[reportMissingImports]
from flask_cors import CORS
from flask_socketio import SocketIO
from kthread import KThread
from werkzeug.serving import is_running_from_reloader

import __main__
from taipy.common.logger._taipy_logger import _TaipyLogger

from ..._hook import _Hooks
from ..._renderers.json import _TaipyJsonAdapter
from ...config import ServerConfig
from ...utils import _is_in_notebook, _is_port_open, _RuntimeManager
from ..server import _Server
from .request import _RequestAccessorFlask

if t.TYPE_CHECKING:
    from ...gui import Gui


class _TaipyJsonProvider(DefaultJSONProvider):
    default = staticmethod(_TaipyJsonAdapter().to_jsonable)
    sort_keys = False


class _FlaskServer(_Server):
    type = "flask"
    server_base_class = Flask

    def __init__(
        self,
        gui: "Gui",
        server: t.Optional[Flask] = None,
        path_mapping: t.Optional[dict] = None,
        async_mode: t.Optional[str] = None,
        allow_upgrades: bool = True,
        server_config: t.Optional[ServerConfig] = None,
    ):
        self.request = _RequestAccessorFlask()
        self._gui = gui
        server_config = server_config or {}
        if server is None:
            flask_config: dict[str, t.Any] = {"import_name": "Taipy"}
            if "flask" in server_config and isinstance(server_config["flask"], dict):
                flask_config.update(server_config["flask"])
            self._server = Flask(**flask_config)
        else:
            self._server = server
        if "SECRET_KEY" not in self._server.config or not self._server.config["SECRET_KEY"]:
            self._server.config["SECRET_KEY"] = "TaIpY"

        # setup cors
        if "cors" not in server_config or (
            "cors" in server_config and (isinstance(server_config["cors"], dict) or server_config["cors"] is True)
        ):
            cors_config = (
                server_config["cors"] if "cors" in server_config and isinstance(server_config["cors"], dict) else {}
            )
            CORS(self._server, **cors_config)

        # setup socketio
        socketio_config: dict[str, t.Any] = {
            "cors_allowed_origins": "*",
            "ping_timeout": 10,
            "ping_interval": 5,
            "json": json,
            "async_mode": async_mode,
            "allow_upgrades": allow_upgrades,
        }
        if "socketio" in server_config and isinstance(server_config["socketio"], dict):
            socketio_config.update(server_config["socketio"])
        self._ws = SocketIO(self._server, **socketio_config)

        self._apply_patch()

        # set json encoder (for Taipy specific types)
        self._server.json_provider_class = _TaipyJsonProvider
        self._server.json = self._server.json_provider_class(self.get_server_instance())

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
                gui._manage_ws_message(message["type"], message)  # type: ignore[attr-defined]

        @self._ws.on("connect")
        def handle_connect():
            gui._handle_connect()  # type: ignore[attr-defined]

        @self._ws.on("disconnect")
        def handle_disconnect():
            gui._handle_disconnect()  # type: ignore[attr-defined]

    def _get_default_handler(
        self,
        static_folder: str,
        template_folder: str,
        title: str,
        favicon: str,
        root_margin: str,
        scripts: list[str],
        styles: list[str],
        version: str,
        client_config: dict[str, t.Any],
        watermark: t.Optional[str],
        css_vars: str,
        base_url: str,
    ) -> Blueprint:
        taipy_bp = Blueprint("Taipy", __name__, static_folder=static_folder, template_folder=template_folder)
        # Serve static react build

        @taipy_bp.route("/", defaults={"path": ""})
        @taipy_bp.route("/<path:path>")
        def my_index(path):
            from ..._hook import _Hooks

            custom_page_resource = _Hooks()._resolve_custom_page_resource_handler(
                path, base_url, static_folder, client_config, css_vars, scripts, styles
            )
            if custom_page_resource is not None:
                return custom_page_resource
            if path == "" or path == "index.html" or "." not in path:
                try:
                    return render_template(
                        "index.html",
                        title=title,
                        favicon=f"{favicon}?version={version}",
                        config=client_config,
                        scripts=scripts,
                        styles=styles,
                        base_url=base_url,
                    )
                except Exception:
                    raise RuntimeError(
                        "Something is wrong with the taipy-gui front-end installation. Check that the js bundle has been properly built (is Node.js installed?)."  # noqa: E501
                    ) from None

            if path == "taipy.status.json":
                return self.direct_render_json(self._gui._serve_status(pathlib.Path(template_folder) / path))  # type: ignore[attr-defined]
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
                and not self._is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            if (
                (
                    file_path := str(os.path.normpath((base_path := self._gui._root_dir + os.path.sep) + path))  # type: ignore[attr-defined]
                ).startswith(base_path)
                and os.path.isfile(file_path)
                and not self._is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            return ("", 404)

        return taipy_bp

    def direct_render_json(self, data):
        return jsonify(data)

    def get_server_instance(self):
        return self._server

    def get_app_context(self):
        return self._server.app_context()

    def get_port(self):
        return self._port

    def test_client(self):
        return t.cast(Flask, self._server).test_client()

    @contextmanager
    def test_request_context(self, path, data=None):
        if not isinstance(self._server, Flask):
            raise RuntimeError("Flask server is not initialized")
        with self._server.test_request_context(path, data=data):
            yield

    def _run_notebook(self):
        self._is_running = True
        self._ws.run(self._server, host=self._host, port=self._port, debug=False, use_reloader=False)

    def _get_async_mode(self) -> str:
        return self._ws.async_mode  # type: ignore[attr-defined]

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

    def send_ws_message(self, *args, **kwargs):
        self._ws.emit("message", *args, **kwargs)

    def save_uploaded_file(self, file, path):
        file.save(path)

    def send_file(self, *args, **kwargs):
        return send_file(*args, **kwargs)

    def send_from_directory(self, *args, **kwargs):
        return send_from_directory(*args, **kwargs)

    def has_server_context(self):
        return has_app_context()

    def is_running_from_reloader(self):
        return is_running_from_reloader()

    def create_http_response(self, message, status_code=200, headers=None):
        if headers is None:
            headers = {}
        return (message, status_code, headers)

    def register_routes(self, styles: list[str], scripts: list[str]):
        from ...gui import Gui

        gui = self._gui
        flask_blueprint: list[Blueprint] = []

        pages_bp = Blueprint("taipy_pages", __name__)
        # Run parse markdown to force variables binding at runtime
        pages_bp.add_url_rule(f"/{Gui._JSX_URL}/<path:page_name>", view_func=gui._render_page)  # pyright: ignore[reportAttributeAccessIssue]
        # server URL Rule for flask rendered react-router
        pages_bp.add_url_rule(f"/{Gui._INIT_URL}", view_func=gui._init_route)  # pyright: ignore[reportAttributeAccessIssue]
        flask_blueprint.append(pages_bp)

        # server URL Rule for taipy images
        images_bp = Blueprint("taipy_images", __name__)
        images_bp.add_url_rule(f"/{Gui._CONTENT_ROOT}/<path:path>", view_func=gui._serve_content)  # pyright: ignore[reportAttributeAccessIssue]
        flask_blueprint.append(images_bp)

        # server URL for uploaded files
        upload_bp = Blueprint("taipy_upload", __name__)
        upload_bp.add_url_rule(f"/{Gui._UPLOAD_URL}", view_func=gui._upload_files, methods=["POST"])  # pyright: ignore[reportAttributeAccessIssue]
        flask_blueprint.append(upload_bp)

        # server URL for user content
        user_content_bp = Blueprint("taipy_user_content", __name__)
        user_content_bp.add_url_rule(f"/{Gui._USER_CONTENT_URL}/<path:path>", view_func=gui._serve_user_content)  # pyright: ignore[reportAttributeAccessIssue]
        flask_blueprint.append(user_content_bp)

        # server URL for extension resources
        extension_bp = Blueprint("taipy_extensions", __name__)
        extension_bp.add_url_rule(f"/{Gui._EXTENSION_ROOT}/<path:path>", view_func=gui._serve_extension)  # pyright: ignore[reportAttributeAccessIssue]
        flask_blueprint.append(extension_bp)

        flask_blueprint.append(
            self._get_default_handler(
                static_folder=gui._get_webapp_path(),  # pyright: ignore[reportAttributeAccessIssue]
                template_folder=gui._get_webapp_path(),  # pyright: ignore[reportAttributeAccessIssue]
                title=gui._get_config("title", "Taipy App"),  # pyright: ignore[reportAttributeAccessIssue]
                favicon=gui._get_config("favicon", Gui._DEFAULT_FAVICON_URL),  # pyright: ignore[reportAttributeAccessIssue]
                root_margin=gui._get_config("margin", None),  # pyright: ignore[reportAttributeAccessIssue]
                scripts=scripts,
                styles=styles,
                version=gui._get_version(),  # pyright: ignore[reportAttributeAccessIssue]
                client_config=gui._get_client_config(),  # pyright: ignore[reportAttributeAccessIssue]
                watermark=gui._get_config("watermark", None),  # pyright: ignore[reportAttributeAccessIssue]
                css_vars=gui._get_css_vars(),  # pyright: ignore[reportAttributeAccessIssue]
                base_url=gui._get_config("base_url", "/"),  # pyright: ignore[reportAttributeAccessIssue]
            )
        )

        _Hooks()._add_external_routes(gui, type=self.type, routers=flask_blueprint)

        # Register Flask Blueprint if available
        for bp in flask_blueprint:
            self._server.register_blueprint(bp)

    def run(
        self,
        host,
        port,
        client_url,
        debug,
        use_reloader,
        server_log,
        run_in_thread,
        allow_unsafe_werkzeug,
        notebook_proxy,
        port_auto_ranges,
    ):
        host_value = host
        message_details = ""
        if host == "0.0.0.0":
            host_value = "localhost"
            message_details = " (listening on all addresses)"
        self._host = host
        if port == "auto":
            port = self._get_random_port(port_auto_ranges)
        server_url = f"http://{host_value}:{port}"
        self._port = port
        if _is_in_notebook() and notebook_proxy:  # pragma: no cover
            from ...utils.proxy import NotebookProxy

            # Start proxy if not already started
            self._proxy = NotebookProxy(gui=self._gui, listening_port=port)
            self._proxy.run()
            self._port = self._get_random_port()
        if _is_in_notebook() or run_in_thread:
            runtime_manager = _RuntimeManager()
            runtime_manager.add_gui(self._gui, port)
        if debug and not self.is_running_from_reloader() and _is_port_open(host_value, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host} because another application is running on the same port.\nPlease pick another port number and rerun with the 'port=<new_port>' setting.\nYou can also let Taipy choose a port number for you by running with the 'port=\"auto\"' setting."  # noqa: E501
            )
        if not server_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
            operation = "reloaded" if self.is_running_from_reloader() else "starting"
            _TaipyLogger._get_logger().info(" * Server %s on %s%s", operation, server_url, message_details)
            if client_url is not None:
                client_url = client_url.format(port=port)
                _TaipyLogger._get_logger().info(" * Application is accessible at %s", client_url)
        if not self.is_running_from_reloader() and self._gui._get_config("run_browser", False):  # type: ignore[attr-defined]
            webbrowser.open(client_url or server_url, new=2)
        if _is_in_notebook() or run_in_thread:
            self._thread = KThread(target=self._run_notebook)
            self._thread.start()
            return
        self._is_running = True
        run_config = {
            "app": self._server,
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

    def is_running(self):
        return self._is_running

    def stop_thread(self):
        if hasattr(self, "_thread") and self._thread.is_alive() and self._is_running:
            self._is_running = False
            with contextlib.suppress(Exception):
                if self._get_async_mode() == "gevent":
                    if self._ws.wsgi_server is not None:  # type: ignore[attr-defined]
                        self._ws.wsgi_server.stop()  # type: ignore[attr-defined]
                    else:
                        self._thread.kill()
                else:
                    self._thread.kill()
            while _is_port_open(self._host, self._port):
                time.sleep(0.1)

    def stop_proxy(self):
        if hasattr(self, "_proxy"):
            self._proxy.stop()
