import datetime
import re
import typing as t
from operator import attrgetter
from types import SimpleNamespace

import pandas as pd
from flask import jsonify, request
from markdown import Markdown

from .AppConfig import AppConfig
from .config import default_config
from .md_ext import *
from .Page import Page
from .server import Server
from .utils import ISOToDate, MapDictionary, Singleton, attrsetter, dateToISO, get_client_var_name


class App(object, metaclass=Singleton):
    """The class that handles the Graphical User Interface."""

    def __init__(
        self,
        import_name: str,
        static_url_path: t.Optional[str] = None,
        static_folder: t.Optional[str] = "taipy_webapp",
        static_host: t.Optional[str] = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: t.Optional[str] = "taipy_webapp",
        instance_path: t.Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: t.Optional[str] = None,
    ):
        self._server = Server(
            self,
            import_name=import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
        )
        self._config = AppConfig()
        # Load deafult config
        self._config.load_config(
            default_config["app_config"], default_config["style_config"]
        )
        self._values = SimpleNamespace()
        self._update_function = None
        self._action_function = None
        # Control identifiers:
        #   Key = variable name
        #   Value = next id (starting at 0)
        # This is filled when creating the controls, using add_control()
        self._control_ids = {}
        self._markdown = Markdown(
            extensions=[
                "taipy.gui",
                "fenced_code",
                "meta",
                "admonition",
                "sane_lists",
                "tables",
                "attr_list",
            ]
        )

    @staticmethod
    def _get_instance():
        return App._instances[App]

    def _parse_markdown(self, text: str) -> str:
        return self._markdown.convert(text)

    def _render_page(self) -> None:
        page = None
        # Get page instance
        for page_i in self._config.pages:
            if page_i.route in request.path:
                page = page_i
        # Make sure that there is a page instace found
        if page is None:
            return (
                jsonify({"error": "Page doesn't exist!"}),
                400,
                {"Content-Type": "application/json; charset=utf-8"},
            )
        # Render template (for redundancy, not necessary 'cause it has already been rendered in self.run function)
        if not page.index_html:
            if page.md_template:
                page.index_html = self._parse_markdown(page.md_template)
            elif page.md_template_file:
                with open(page.md_template_file, "r") as f:
                    page.index_html = self._parse_markdown(f.read())
        # Return jsx page
        if page.index_html:
            return self._server.render(
                page.index_html, page.style, self._config.app_config["dark_mode"]
            )
        else:
            return "No page template"

    def _render_route(self) -> None:
        return self._server.render_react_route(self._config.routes)

    def add_page(
        self,
        name: str,
        markdown_template: t.Optional[str] = None,
        markdown_template_file: t.Optional[str] = None,
        style: t.Optional[str] = "",
    ) -> None:
        # Validate page_route
        if name is None:
            raise Exception("page_route is required for add_page function!")
        if not re.match(r"^[\w-]+$", name):
            raise SyntaxError(
                f"Page route '{name}' is not valid! Can only contain alphabet letters, numbers, dash (-), and underscore (_)"
            )
        # Init a new page
        new_page = Page()
        new_page.route = name
        new_page.md_template = markdown_template
        new_page.md_template_file = markdown_template_file
        new_page.style = style
        # Append page to _config
        self._config.pages.append(new_page)
        self._config.routes.append(name)

    # TODO: Check name value to avoid conflicting with Flask,
    # or, simply, compose with Flask instead of inherit from it.
    def bind(self, name, value):
        if hasattr(self, name):
            raise ValueError(f"Variable '{name}' is already bound")
        if not re.match("^[a-zA-Z][a-zA-Z_$0-9]*$", name):
            raise ValueError(f"Variable name '{name}' is invalid")
        if isinstance(value, dict):
            prop = MapDictionary(self._server._ws, value)
            setattr(App, name, prop)
            setattr(self._values, name, prop)
        else:
            prop = property(
                lambda s: getattr(s._values, name),  # Getter
                lambda s, v: self._update_var(name, v),  # Setter
            )
            setattr(App, name, prop)
            setattr(self._values, name, value)

    # Main binding method (bind in markdown declaration)
    def bind_var(self, var_name):
        if not hasattr(self, var_name) and var_name in self._dict_bind_locals:
            self.bind(var_name, self._dict_bind_locals[var_name])

    # Backup Binding Method
    def _bind_all(self):
        exclusion_list = [
            "__name__",
            "__doc__",
            "__package__",
            "__loader__",
            "__spec__",
            "__annotations__",
            "__builtins__",
            "__file__",
        ]
        for k, v in self._dict_bind_locals.items():
            if k not in exclusion_list and type(v) in (int, float, bool, str, dict):
                self.bind(k, v)

    def _add_control(self, variable_name) -> int:
        id = 0
        if variable_name in self._control_ids:
            id = self._control_ids[variable_name]
        self._control_ids[variable_name] = id + 1
        return id

    def _update_var(self, var_name, value) -> None:
        # Check if Variable is type datetime
        if isinstance(attrgetter(var_name)(self._values), datetime.datetime):
            value = ISOToDate(value)
        # Use custom attrsetter fuction to allow value binding for MapDictionary
        attrsetter(self._values, var_name, value)
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if self._update_function:
            self._update_function(var_name, value)
        newvalue = attrgetter(var_name)(self._values)
        if isinstance(newvalue, datetime.datetime):
            newvalue = dateToISO(newvalue)
        # TODO: What if value == newvalue?
        self._send_ws_update(var_name, {"value": newvalue})

    def _request_var(self, var_name, payload) -> None:
        ret_payload = {}
        # Use custom attrgetter fuction to allow value binding for MapDictionary
        newvalue = attrgetter(var_name)(self._values)
        if isinstance(newvalue, datetime.datetime):
            newvalue = dateToISO(newvalue)
        elif isinstance(newvalue, pd.DataFrame):
            ret_payload["pagekey"] = payload["pagekey"]
            start = int(payload["start"]) if payload["start"] else 0
            end = int(payload["end"]) if payload["end"] else len(newvalue)
            if start ==  -1:
                start = - end - 1
                end = None
            elif start >= len(newvalue):
                start = -end + start
                end = None
            if end and end >= len(newvalue):
                end = len(newvalue) - 1
            newvalue = newvalue.iloc[slice(start, end)]
            newvalue = newvalue.to_dict(orient="index")
            # here we'll deal with start and end values from payload if present
            pass
        # TODO: What if value == newvalue?
        ret_payload["value"] = newvalue
        self._send_ws_update(var_name, ret_payload)

    def _send_ws_update(self, var_name, payload) -> None:
        try:
            self._server._ws.send({"type": "U", "name": get_client_var_name(var_name), "payload": payload})
        except Exception as e:
            print(e)

    def on_update(self, f):
        self._update_function = f

    def on_action(self, f):
        self._action_function = f

    def _on_action(self, id, action):
        if action:
            try:
                action_function = getattr(self, action)
                action_function(self, id)
                return
            except:
                pass
        if self._action_function:
            self._action_function(self, id, action)

    def load_config(self, app_config={}, style_config={}):
        self._config.load_config(app_config=app_config, style_config=style_config)

    def run(self, host=None, port=None, debug=None, load_dotenv=True, bind_locals=None):
        # Check with default config, overide only if parameter is not passed directly into the run function
        if host is None and self._config.app_config["host"] is not None:
            host = self._config.app_config["host"]
        if port is None and self._config.app_config["port"] is not None:
            port = self._config.app_config["port"]
        if debug is None and self._config.app_config["debug"] is not None:
            debug = self._config.app_config["debug"]
        # Save all availbale variables in locals
        self._dict_bind_locals = bind_locals
        # Run parse markdown to force variables binding at runtime (save rendered html to page.index_html for optimization)
        for page_i in self._config.pages:
            if page_i.md_template:
                page_i.index_html = self._parse_markdown(page_i.md_template)
            elif page_i.md_template_file:
                with open(page_i.md_template_file, "r") as f:
                    page_i.index_html = self._parse_markdown(f.read())
            # Server URL Rule for each page jsx
            self._server.add_url_rule(
                f"/flask-jsx/{page_i.route}/", view_func=self._render_page
            )
        # server URL Rule for flask rendered react-router
        self._server.add_url_rule("/react-router/", view_func=self._render_route)

        # Start Flask Server
        self._server.runWithWS(
            host=host, port=port, debug=debug, load_dotenv=load_dotenv
        )
