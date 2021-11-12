import os
import typing as t

import __main__
from flask import Flask, abort, jsonify, render_template, render_template_string, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO


class Server(Flask):
    def __init__(
        self,
        app,
        css_file: str,
        static_folder: t.Optional[str] = "",
        template_folder: str = "",
        path_mapping: t.Optional[dict] = {},
    ):
        super().__init__(
            import_name="Taipy",
            static_url_path=None,
            static_folder=static_folder,
            static_host=None,
            host_matching=False,
            subdomain_matching=False,
            template_folder=template_folder,
            instance_path=None,
            instance_relative_config=False,
            root_path=None,
        )
        self._app = app
        self.config["SECRET_KEY"] = "TaIpY"
        # Add cors for frontend access
        self._ws = SocketIO(self, async_mode=None, cors_allowed_origins="*")
        CORS(self)

        self.__path_mapping = path_mapping

        # Serve static react build
        @self.route("/", defaults={"path": ""})
        @self.route("/<path:path>")
        def my_index(path):
            if path == "" or "." not in path:
                return render_template(
                    "index.html",
                    flask_url=self._client_url,
                    app_css="/" + css_file + ".css",
                    title=self._app.title if hasattr(self._app, "title") else "Taipy App",
                )
            if os.path.isfile(self.static_folder + os.path.sep + path):
                return send_from_directory(self.static_folder + os.path.sep, path)
            # use the path mapping to detect and find resources
            for k, v in self.__path_mapping.items():
                if path.startswith(k + "/") and os.path.isfile(v + os.path.sep + path[len(k) + 1 :]):
                    return send_from_directory(v + os.path.sep, path[len(k) + 1 :])
            if hasattr(__main__, "__file__") and os.path.isfile(
                os.path.dirname(__main__.__file__) + os.path.sep + path
            ):
                return send_from_directory(os.path.dirname(__main__.__file__) + os.path.sep, path)
            return ("", 404)

        @self.errorhandler(404)
        def page_not_found(e):
            return "{}, {}".format(e.message, e.description)

        # Websocket (handle json message)
        @self._ws.on("message")
        def handle_message(message) -> None:
            if "status" in message:
                print(message["status"])
            elif "type" in message.keys():
                self._app._manage_message(message["type"], message)

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

    def _set_client_url(self, client_url=None):
        self._client_url = client_url

    def runWithWS(self, host=None, port=None, debug=None):
        self._ws.run(self, host=host, port=port, debug=debug)
