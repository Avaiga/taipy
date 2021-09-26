import os
import typing as t

from flask import (
    Flask,
    jsonify,
    render_template,
    render_template_string,
    request,
    send_from_directory,
)
from flask_cors import CORS
from flask_socketio import SocketIO


class Server(Flask):
    def __init__(
        self,
        app,
        import_name: str,
        static_folder: t.Optional[str] = "",
        template_folder: str = "",
        path_mapping: t.Optional[dict] = {},
    ):
        super().__init__(
            import_name=import_name,
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

        # Serve static react build
        @self.route("/", defaults={"path": ""})
        @self.route("/<path:path>")
        def my_index(path):
            if path == "" or "." not in path:
                return render_template(
                    "index.html",
                    flask_url=request.url_root,
                    title=self._app.title
                    if hasattr(self._app, "title")
                    else "Taipy App",
                )
            else:
                # TODO use the path mapping to detect and find resources
                return send_from_directory(self.static_folder + os.path.sep, path)

        # Websocket (handle json message)
        @self._ws.on("message")
        def handle_message(message) -> None:
            try:
                if "status" in message:
                    print(message["status"])
                elif message["type"] == "U":
                    self._app._update_var(message["name"], message["payload"])
                elif message["type"] == "A":
                    self._app._on_action(message["name"], message["payload"])
                elif message["type"] == "T":
                    self._app._request_var(message["name"], message["payload"])
            except TypeError as te:
                print("Decoding Message has failed: " + str(message) + "\n " + str(te))
            except KeyError as ke:
                print("Can't access: " + message + "\n" + str(ke))

    # Update to render as JSX
    def render(self, html_fragment, style, timezone, dark_mode):
        template_str = render_template_string(html_fragment)
        template_str = template_str.replace('"{!', "{")
        template_str = template_str.replace('!}"', "}")
        return self._direct_render_json(
            {
                "jsx": template_str,
                "style": ((style + os.linesep) if style else ""),
                "darkMode": dark_mode,
                "timezone": timezone,
            }
        )

    def _direct_render_json(self, data):
        return jsonify(data)

    def runWithWS(self, host=None, port=None, debug=None, load_dotenv=True):
        self._ws.run(self, host=host, port=port, debug=debug)
