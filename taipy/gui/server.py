# Copyright 2022 Avaiga Private Limited
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

import logging
import os
import re
import socket
import typing as t
import webbrowser

import __main__
from flask import Blueprint, Flask, json, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_talisman import Talisman
from werkzeug.serving import is_running_from_reloader

from .renderers.jsonencoder import _TaipyJsonEncoder
from .utils import _is_in_notebook, _KillableThread

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
        content_security_policy: t.Optional[dict] = None,
        force_https: bool = False,
        async_mode: t.Optional[str] = None,
    ):
        self._gui = gui
        self._flask = Flask("Taipy") if flask is None else flask
        self.css_file = css_file
        if "SECRET_KEY" not in self._flask.config or not self._flask.config["SECRET_KEY"]:
            self._flask.config["SECRET_KEY"] = "TaIpY"
        # set json encoder (for Taipy specific types)
        self._flask.json_encoder = _TaipyJsonEncoder
        # Add cors for frontend access
        self._ws = SocketIO(
            self._flask, cors_allowed_origins="*", ping_timeout=10, ping_interval=5, json=json, async_mode=async_mode
        )

        CORS(self._flask)

        if force_https or content_security_policy:
            Talisman(self._flask, content_security_policy=content_security_policy, force_https=force_https)

        self.__path_mapping = path_mapping

        # Websocket (handle json message)
        @self._ws.on("message")
        def handle_message(message) -> None:
            if "status" in message:
                print(message["status"])
            elif "type" in message:
                gui._manage_message(message["type"], message)

    def __get_client_config(self) -> t.Dict[str, t.Any]:
        config = {
            "timeZone": self._gui._config.get_time_zone(),
            "darkMode": self._gui._get_config("dark_mode", True),
        }
        if themes := self._gui._get_themes():
            config["themes"] = themes
        return config

    def _get_default_blueprint(
        self,
        static_folder: t.Optional[str] = "",
        template_folder: str = "",
        title: str = "",
        favicon: str = "",
        root_margin: t.Optional[str] = None,
    ) -> Blueprint:
        taipy_bp = Blueprint("Taipy", __name__, static_folder=static_folder, template_folder=template_folder)
        # Serve static react build

        @taipy_bp.route("/", defaults={"path": ""})
        @taipy_bp.route("/<path:path>")
        def my_index(path):
            if path == "" or "." not in path:
                return render_template(
                    "index.html",
                    app_css=f"/{self.css_file}.css",
                    title=title,
                    favicon=favicon,
                    root_margin=root_margin,
                    watermark=self._gui._get_config("watermark", None),
                    config=self.__get_client_config(),
                )
            if os.path.isfile(static_folder + os.path.sep + path):
                return send_from_directory(static_folder + os.path.sep, path)
            # use the path mapping to detect and find resources
            for k, v in self.__path_mapping.items():
                if path.startswith(f"{k}/") and os.path.isfile(v + os.path.sep + path[len(k) + 1 :]):
                    return send_from_directory(v + os.path.sep, path[len(k) + 1 :])
            if (
                hasattr(__main__, "__file__")
                and str(
                    os.path.normpath(
                        file_path := ((base_path := os.path.dirname(__main__.__file__) + os.path.sep) + path)
                    )
                ).startswith(base_path)
                and os.path.isfile(file_path)
            ):
                return send_from_directory(base_path, path)
            if str(os.path.normpath(file_path := (base_path := self._gui._root_dir + os.path.sep) + path)).startswith(
                base_path
            ) and os.path.isfile(file_path):
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
        self._ws.run(self._flask, host=self._host, port=self._port, debug=False, use_reloader=False)

    def _get_async_mode(self) -> str:
        return self._ws.async_mode

    def runWithWS(self, host, port, debug, use_reloader, flask_log, run_in_thread, ssl_context):
        host_value = host if host != "0.0.0.0" else "localhost"
        if debug and not is_running_from_reloader():
            # Check that the port is not already opened
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host_value, port))
            sock.close()
            if result == 0:
                raise ConnectionError(
                    f"Port {port} is already opened on {host_value}. You have another server application running on the same port."
                )
        if not flask_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
            print(f" * Server starting on http://{host_value}:{port}")
        if (
            not is_running_from_reloader()
            and self._gui._get_config("run_browser", False)
            and self._gui._get_config("debug", False)
        ):
            webbrowser.open(f"http://{host_value}{f':{port}' if port else ''}", new=2)
        if _is_in_notebook() or run_in_thread:
            self._host = host
            self._port = port
            self._thread = _KillableThread(target=self._run_notebook)
            self._thread.start()
            return
        if self._get_async_mode() != "threading":
            use_reloader = False
        self._ws.run(self._flask, host=host, port=port, debug=debug, use_reloader=use_reloader)

    def stop_thread(self):
        if hasattr(self, "_thread"):
            if self._get_async_mode() != "threading":
                self._ws.stop()
            self._thread.kill()
            self._thread.join()
