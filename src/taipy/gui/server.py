# Copyright 2023 Avaiga Private Limited
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
import socket
import sys
import time
import typing as t
import webbrowser
from importlib import util

import __main__
from flask import Blueprint, Flask, json, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from gitignore_parser import parse_gitignore
from kthread import KThread
from werkzeug.serving import is_running_from_reloader

from taipy.logger._taipy_logger import _TaipyLogger

from .renderers.json import _TaipyJsonProvider
from .utils import _is_in_notebook, _RuntimeManager

if t.TYPE_CHECKING:
    from .gui import Gui


class _Server:

    __RE_OPENING_CURLY = re.compile(r"([^\"])(\{)")
    __RE_CLOSING_CURLY = re.compile(r"(\})([^\"])")
    __OPENING_CURLY = r"\1&#x7B;"
    __CLOSING_CURLY = r"&#x7D;\2"

    def __init__(
        self,
        gui: Gui,
        flask: t.Optional[Flask] = None,
        css_file: str = "",
        path_mapping: t.Optional[dict] = {},
        async_mode: t.Optional[str] = None,
    ):
        self._gui = gui
        self._flask = Flask("Taipy") if flask is None else flask
        self.css_file = css_file
        if "SECRET_KEY" not in self._flask.config or not self._flask.config["SECRET_KEY"]:
            self._flask.config["SECRET_KEY"] = "TaIpY"
        # set json encoder (for Taipy specific types)
        self._flask.json_provider_class = _TaipyJsonProvider
        self._flask.json = self._flask.json_provider_class(self._flask)
        # Add cors for frontend access
        self._ws = SocketIO(
            self._flask, cors_allowed_origins="*", ping_timeout=10, ping_interval=5, json=json, async_mode=async_mode
        )

        self._apply_patch()

        CORS(self._flask)

        self.__path_mapping = path_mapping
        self._is_running = False

        # Websocket (handle json message)
        @self._ws.on("message")
        def handle_message(message) -> None:
            if "status" in message:
                _TaipyLogger._get_logger().info(message["status"])
            elif "type" in message:
                gui._manage_message(message["type"], message)

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
    ) -> Blueprint:
        taipy_bp = Blueprint("Taipy", __name__, static_folder=static_folder, template_folder=template_folder)
        # Serve static react build

        @taipy_bp.route("/", defaults={"path": ""})
        @taipy_bp.route("/<path:path>")
        def my_index(path):
            if path == "" or path == "index.html" or "." not in path:
                return render_template(
                    "index.html",
                    app_css=f"/{self.css_file}.css",
                    title=title,
                    favicon=favicon,
                    root_margin=root_margin,
                    watermark=watermark,
                    config=client_config,
                    scripts=scripts,
                    styles=styles,
                    version=version,
                )
            if path == "taipy.status.json":
                return self._direct_render_json(self._gui._serve_status(pathlib.Path(template_folder) / path))
            if str(os.path.normpath(file_path := ((base_path := static_folder + os.path.sep) + path))).startswith(
                base_path
            ) and os.path.isfile(file_path):
                return send_from_directory(base_path, path)
            # use the path mapping to detect and find resources
            for k, v in self.__path_mapping.items():
                if (
                    path.startswith(f"{k}/")
                    and str(
                        os.path.normpath(file_path := ((base_path := v + os.path.sep) + path[len(k) + 1 :]))
                    ).startswith(base_path)
                    and os.path.isfile(file_path)
                ):
                    return send_from_directory(base_path, path[len(k) + 1 :])
            if (
                hasattr(__main__, "__file__")
                and str(
                    os.path.normpath(
                        file_path := ((base_path := os.path.dirname(__main__.__file__) + os.path.sep) + path)
                    )
                ).startswith(base_path)
                and os.path.isfile(file_path)
                and not self.__is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            if (
                str(os.path.normpath(file_path := (base_path := self._gui._root_dir + os.path.sep) + path)).startswith(
                    base_path
                )
                and os.path.isfile(file_path)
                and not self.__is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)
            return ("", 404)

        @taipy_bp.errorhandler(404)
        def page_not_found(e):
            return f"{e.message}, {e.description}"

        return taipy_bp

    # Update to render as JSX
    def _render(self, html_fragment, style, head, context):
        template_str = _Server.__RE_OPENING_CURLY.sub(_Server.__OPENING_CURLY, html_fragment)
        template_str = _Server.__RE_CLOSING_CURLY.sub(_Server.__CLOSING_CURLY, template_str)
        template_str = template_str.replace('"{!', "{")
        template_str = template_str.replace('!}"', "}")
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

    def test_client(self):
        return self._flask.test_client()

    def _run_notebook(self):
        self._is_running = True
        self._ws.run(self._flask, host=self._host, port=self._port, debug=False, use_reloader=False)

    def _get_async_mode(self) -> str:
        return self._ws.async_mode

    def _is_port_open(self, host, port) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0

    def _apply_patch(self):
        if self._get_async_mode() == "gevent" and util.find_spec("gevent"):
            from gevent import monkey

            if not monkey.is_module_patched("time"):
                monkey.patch_time()
        if self._get_async_mode() == "eventlet" and util.find_spec("eventlet"):
            from eventlet import monkey_patch, patcher

            if not patcher.is_monkey_patched("time"):
                monkey_patch(time=True)

    def run(self, host, port, debug, use_reloader, flask_log, run_in_thread, allow_unsafe_werkzeug):
        host_value = host if host != "0.0.0.0" else "localhost"
        if _is_in_notebook() or run_in_thread:
            runtime_manager = _RuntimeManager()
            runtime_manager.add_gui(self._gui, port)
        if debug and not is_running_from_reloader() and self._is_port_open(host_value, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host_value}. You have another server application running on the same port."
            )
        if not flask_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
            if not is_running_from_reloader():
                _TaipyLogger._get_logger().info(f" * Server starting on http://{host_value}:{port}")
            else:
                _TaipyLogger._get_logger().info(f" * Server reloaded on http://{host_value}:{port}")
        if not is_running_from_reloader() and self._gui._get_config("run_browser", False):
            webbrowser.open(f"http://{host_value}{f':{port}' if port else ''}", new=2)
        if _is_in_notebook() or run_in_thread:
            self._host = host
            self._port = port
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
        # flask-socketio specific conditions for 'allow_unsafe_werkzeug' parameters to be popped out of kwargs
        if self._get_async_mode() == "threading" and (not sys.stdin or not sys.stdin.isatty()):
            run_config = {**run_config, "allow_unsafe_werkzeug": allow_unsafe_werkzeug}
        self._ws.run(**run_config)

    def stop_thread(self):
        if hasattr(self, "_thread") and self._thread.is_alive() and self._is_running:
            self._is_running = False
            with contextlib.suppress(Exception):
                if self._get_async_mode() == "gevent":
                    if self._ws.wsgi_server is not None:
                        self._ws.wsgi_server.stop()
                    else:
                        self._thread.kill()
                else:
                    self._thread.kill()
            while self._is_port_open(self._host, self._port):
                time.sleep(0.1)
