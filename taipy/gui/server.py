from __future__ import annotations

import logging
import os
import re
import typing as t

import __main__
from flask import Blueprint, Flask, jsonify, render_template, render_template_string, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

from .utils import KillableThread, _is_in_notebook

if t.TYPE_CHECKING:
    from .gui import Gui


class Server:

    __RE_JSX_RENDER_ROUTE = re.compile(r"/taipy-jsx/(.*)/")

    def __init__(
        self,
        gui: Gui,
        flask: t.Optional[Flask] = None,
        css_file: str = "",
        path_mapping: t.Optional[dict] = {},
        root_page_name: str = "",
    ):
        self._gui = gui
        self._root_page_name = root_page_name
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
                gui._manage_message(message["type"], message)

        @self._ws.on("connect")
        def ws_connect():
            # gui._scopes.create_scope()
            pass

        @self._ws.on("disconnect")
        def ws_disconnect():
            # gui._scopes.delete_scope()
            pass

    def _get_default_blueprint(
        self,
        static_folder: t.Optional[str] = "",
        template_folder: str = "",
        client_url: str = "",
        title: str = "",
        favicon: str = "",
        themes: t.Optional[t.Dict[str, t.Any]] = None,
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
    def _render(self, html_fragment, style, head):
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

    def _render_page(self) -> t.Any:
        page = None
        render_path_name = Server.__RE_JSX_RENDER_ROUTE.match(request.path).group(1)  # type: ignore
        # Get page instance
        for page_i in self._gui._config.pages:
            if page_i.route == render_path_name:
                page = page_i
        # try partials
        if page is None:
            for partial in self._gui._config.partials:
                if partial.route == render_path_name:
                    page = partial
        # Make sure that there is a page instance found
        if page is None:
            return (jsonify({"error": "Page doesn't exist!"}), 400, {"Content-Type": "application/json; charset=utf-8"})
        # TODO: assign global scopes to current scope if the page has been rendered
        page.render()
        if (
            render_path_name == self._root_page_name
            and page.rendered_jsx is not None
            and "<PageContent" not in page.rendered_jsx
        ):
            page.rendered_jsx += "<PageContent />"
        # Return jsx page
        if page.rendered_jsx is not None:
            return self._render(page.rendered_jsx, page.style if hasattr(page, "style") else "", page.head)
        else:
            return ("No page template", 404)

    def _render_route(self) -> t.Any:
        # Generate router
        routes = self._gui._config.routes
        locations = {}
        router = '<Routes key="routes">'
        router += (
            '<Route path="/" key="'
            + self._root_page_name
            + '" element={<MainPage key="tr'
            + self._root_page_name
            + '" path="/'
            + self._root_page_name
            + '"'
        )
        route = next((r for r in routes if r != self._root_page_name), None)
        router += (' route="/' + route + '"') if route else ""
        router += " />} >"
        locations["/"] = "/" + self._root_page_name
        for route in routes:
            if route != self._root_page_name:
                router += (
                    '<Route path="'
                    + route
                    + '" key="'
                    + route
                    + '" element={<TaipyRendered key="tr'
                    + route
                    + '"/>} />'
                )
                locations["/" + route] = "/" + route
        router += '<Route path="*" key="NotFound" element={<NotFound404 />} />'
        router += "</Route>"
        router += "</Routes>"

        return self._direct_render_json(
            {
                "router": router,
                "locations": locations,
                "timeZone": self._gui._config.get_time_zone(),
                "darkMode": self._gui._get_app_config("dark_mode", True),
                "blockUI": self._gui._is_ui_blocked(),
            }
        )

    def get_flask(self):
        return self._flask

    def test_client(self):
        return self._flask.test_client()

    def _run_notebook(self):
        self._ws.run(self._flask, host=self._host, port=self._port, debug=False, use_reloader=False)

    def runWithWS(self, host=None, port=None, debug=None, use_reloader=None, flask_log=True):
        if not flask_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
            self._flask.logger.disabled = True
            # os.environ['WERKZEUG_RUN_MAIN'] = 'true'
            print(f" * Server starting on http://{host}:{port}")
        if _is_in_notebook():
            self._host = host
            self._port = port
            self._thread = KillableThread(target=self._run_notebook)
            self._thread.start()
            return
        self._ws.run(self._flask, host=host, port=port, debug=debug, use_reloader=use_reloader)
