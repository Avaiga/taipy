from __future__ import annotations

import os
import typing as t

import __main__
from flask import Flask, Blueprint, jsonify, render_template, render_template_string, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

if t.TYPE_CHECKING:
    from .gui import Gui


class Server:
    def __init__(
        self,
        app: Gui,
        flask: Flask,
        css_file: str,
        path_mapping: t.Optional[dict] = {},
    ):
        self._flask = Flask("Taipy") if flask is None else flask
        self.css_file = css_file
        if "SECRET_KEY" not in self._flask.config or not self._flask.config["SECRET_KEY"]:
            self._flask.config["SECRET_KEY"] = "TaIpY"
        # Add cors for frontend access
        self._ws = SocketIO(self._flask, async_mode=None, cors_allowed_origins="*", ping_timeout=10, ping_interval=5)
        CORS(self._flask)

        self.__path_mapping = path_mapping

        # Websocket (handle json message)
        @self._ws.on("message")
        def handle_message(message) -> None:
            if "status" in message:
                print(message["status"])
            elif "type" in message.keys():
                app._manage_message(message["type"], message)

        @self._ws.on("connect")
        def ws_connect():
            app._data_scopes.create_scope()

        @self._ws.on("disconnect")
        def ws_disconnect():
            app._data_scopes.delete_scope()

    def _get_default_blueprint(
        self,
        static_folder: t.Optional[str] = "",
        template_folder: str = "",
        client_url: str = "",
        title: str = "",
        favicon: str = "",
        themes: t.Dict[str, t.Any] = {},
    ) -> Blueprint:
        taipy_bp = Blueprint("Taipy", __name__, static_folder=static_folder, template_folder=template_folder)
        # Serve static react build
        @taipy_bp.route("/", defaults={"path": ""})
        @taipy_bp.route("/<path:path>")
        def my_index(path):
            if path == "" or "." not in path:
                return render_template(
                    "index.html",
                    flask_url=client_url,
                    app_css="/" + self.css_file + ".css",
                    title=title,
                    favicon=favicon,
                    themes=themes,
                )
            if os.path.isfile(static_folder + os.path.sep + path):
                return send_from_directory(static_folder + os.path.sep, path)
            # use the path mapping to detect and find resources
            for k, v in self.__path_mapping.items():
                if path.startswith(k + "/") and os.path.isfile(v + os.path.sep + path[len(k) + 1 :]):
                    return send_from_directory(v + os.path.sep, path[len(k) + 1 :])
            if hasattr(__main__, "__file__") and os.path.isfile(
                os.path.dirname(__main__.__file__) + os.path.sep + path
            ):
                return send_from_directory(os.path.dirname(__main__.__file__) + os.path.sep, path)
            return ("", 404)

        @taipy_bp.errorhandler(404)
        def page_not_found(e):
            return "{}, {}".format(e.message, e.description)

        return taipy_bp

    # Update to render as JSX
    def render(self, html_fragment, style, head):
        template_str = render_template_string(html_fragment)
        template_str = template_str.replace('"{!', "{")
        template_str = template_str.replace('!}"', "}")
        return self._direct_render_json(
            {
                "jsx": template_str,
                "style": (style + os.linesep) if style else "",
                "head": head or "",
            }
        )

    def _direct_render_json(self, data):
        return jsonify(data)

    def get_flask(self):
        return self._flask

    def test_client(self):
        return self._flask.test_client():

    def runWithWS(self, host=None, port=None, debug=None):
        self._ws.run(self._flask, host=host, port=port, debug=debug)
