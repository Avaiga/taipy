import pathlib
import datetime
import inspect
import os
import re
import typing as t
from operator import attrgetter
from types import SimpleNamespace

import pandas as pd
from flask import jsonify, request
from markdown import Markdown

from .config import GuiConfig
from ._default_config import default_config
from ._md_ext import *
from .Page import Page
from .server import Server
from .utils import (
    ISOToDate,
    _MapDictionary,
    Singleton,
    attrsetter,
    dateToISO,
    get_client_var_name,
    get_date_col_str_name,
)


class Gui(object, metaclass=Singleton):
    """The class that handles the Graphical User Interface."""

    __root_page_name = "TaiPy_root_page"

    def __init__(
        self,
        import_name: str,
        markdown: t.Optional[str] = None,
        markdown_file: t.Optional[str] = None,
        pages: t.Optional[dict] = None,
        path_mapping: t.Optional[dict] = {},
    ):
        _absolute_path = str(pathlib.Path(__file__).parent.resolve())
        self._server = Server(
            self,
            import_name=import_name,
            static_folder=f"{_absolute_path}{os.path.sep}webapp",
            template_folder=f"{_absolute_path}{os.path.sep}webapp",
            path_mapping=path_mapping,
        )
        self._config = GuiConfig()
        # Load default config
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
        self._control_ids: t.Dict[str, int] = {}
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
        if markdown:
            self.add_page(name=Gui.__root_page_name, markdown=markdown)
        if markdown_file:
            if markdown:
                raise Exception(
                    "Cannot specify a markdown_file and a mrkdown string at the same time. Consider using the pages parameter."
                )
            self.add_page(name=Gui.__root_page_name, markdown_file=markdown_file)
        if pages:
            for k, v in pages.items():
                if k == "/":
                    k = Gui.__root_page_name
                self.add_page(name=k, markdown=str(v))

    @staticmethod
    def _get_instance():
        return Gui._instances[Gui]

    def _parse_markdown(self, text: str) -> str:
        return self._markdown.convert(text)

    def _render_page(self) -> t.Any:
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
        # Render template (for redundancy, not necessary 'cause it has already
        # been rendered in self.run function)
        if not page.index_html:
            if page.md_template:
                page.index_html = self._parse_markdown(page.md_template)
            elif page.md_template_file:
                with open(page.md_template_file, "r") as f:
                    page.index_html = self._parse_markdown(f.read())
        # Return jsx page
        if page.index_html:
            return self._server.render(
                page.index_html,
                page.style,
                self._config.get_timezone(),
                self._config.app_config["dark_mode"],
            )
        else:
            return "No page template"

    def __render_route(self):
        # Generate router
        routes = self._config.routes
        locations = {}
        router = '<Router key="Router"><Switch>'
        for route in routes:
            router += (
                '<Route path="/'
                + (route if route != Gui.__root_page_name else "")
                + '" exact key="'
                + route
                + '" ><TaipyRendered/></Route>'
            )
            locations["/" + (route if route != Gui.__root_page_name else "")] = (
                "/" + route
            )
        if Gui.__root_page_name not in routes:
            router += (
                '<Route path="/" exact key="'
                + Gui.__root_page_name
                + '" ><TaipyRendered/></Route>'
            )
            locations["/"] = "/" + routes[0]

        router += '<Route path="/404" exact key="404" ><NotFound404 /></Route>'
        router += '<Redirect to="/' + routes[0] + '" key="Redirect" />'
        router += "</Switch></Router>"

        return self._server._direct_render_json(
            {"router": router, "locations": locations}
        )

    def add_page(
        self,
        name: str,
        markdown: t.Optional[str] = None,
        markdown_file: t.Optional[str] = None,
        style: t.Optional[str] = "",
    ) -> None:
        # Validate name
        if name is None:
            raise Exception("name is required for add_page function!")
        if not re.match(r"^[\w-]+$", name):
            raise SyntaxError(
                f'page name "{name}" is not valid! Can only contain letters, digits, dashes (-) and underscores (_).'
            )
        if name in self._config.routes:
            raise Exception(
                'page name "'
                + (name if name != Gui.__root_page_name else "/")
                + '" is already defined'
            )
        # Init a new page
        new_page = Page()
        new_page.route = name
        new_page.md_template = markdown
        new_page.md_template_file = markdown_file
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
            setattr(
                Gui,
                name,
                _MapDictionary(value, lambda s, v: self._update_var(name + "." + s, v)),
            )
            setattr(self._values, name, _MapDictionary(value))
        else:
            prop = property(
                lambda s: getattr(s._values, name),  # Getter
                lambda s, v: s._update_var(name, v),  # Setter
            )
            setattr(Gui, name, prop)
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
        currentvalue = attrgetter(var_name)(self._values)
        if isinstance(value, str):
            if isinstance(currentvalue, datetime.datetime):
                value = ISOToDate(value)
            elif isinstance(currentvalue, int):
                value = int(value)
            elif isinstance(currentvalue, float):
                value = float(value)
            elif isinstance(currentvalue, complex):
                value = complex(value)
            elif isinstance(currentvalue, bool):
                value = bool(value)
            elif isinstance(currentvalue, pd.DataFrame):
                print("Error: cannot update value for dataframe: " + var_name)
                return
        # Use custom attrsetter fuction to allow value binding for MapDictionary
        attrsetter(self._values, var_name, value)
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if self._update_function:
            self._update_function(self, var_name, value)
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
            keys = payload.keys()
            ret_payload["pagekey"] = (
                payload["pagekey"] if "pagekey" in keys else "unknown page"
            )
            if isinstance(payload["start"], int):
                start = int(payload["start"])
            else:
                try:
                    start = int(str(payload["start"]), base=10)
                except Exception as e:
                    print(e)
                    start = 0
            if isinstance(payload["end"], int):
                end = int(payload["end"])
            else:
                try:
                    end = int(str(payload["end"]), base=10)
                except Exception:
                    end = -1
            rowcount = len(newvalue)
            if start < 0 or start >= rowcount:
                start = 0
            if end < 0 or end >= rowcount:
                end = rowcount - 1
            datecols = newvalue.dtypes[
                newvalue.dtypes.astype("string").str.startswith("datetime")
            ].index.tolist()
            if len(datecols) != 0:
                # copy the df so that we don't "mess" with the user's data
                newvalue = newvalue.copy()
                for col in datecols:
                    newcol = get_date_col_str_name(newvalue, col)
                    newvalue[newcol] = (
                        newvalue[col]
                        .dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        .astype("string")
                    )
            if (
                "orderby" in keys
                and isinstance(payload["orderby"], str)
                and len(payload["orderby"])
            ):
                new_indexes = newvalue[payload["orderby"]].values.argsort(axis=0)
                if "sort" in keys and payload["sort"] == "desc":
                    # reverse order
                    new_indexes = new_indexes[::-1]
                new_indexes = new_indexes[slice(start, end)]
            else:
                new_indexes = slice(start, end)
            # here we'll deal with start and end values from payload if present
            newvalue = newvalue.iloc[new_indexes]  # returns a view
            if len(datecols) != 0:
                # remove the date columns from the list of columnss
                cols = list(set(newvalue.columns.tolist()) - set(datecols))
                newvalue = newvalue.loc[:, cols]  # view without the date columns
            dictret = {"data": newvalue.to_dict(orient="records"), "rowcount": rowcount}
            newvalue = dictret
            pass
        # TODO: What if value == newvalue?
        ret_payload["value"] = newvalue
        self._send_ws_update(var_name, ret_payload)

    def _send_ws_update(self, var_name, payload) -> None:
        try:
            self._server._ws.send(
                {"type": "U", "name": get_client_var_name(var_name), "payload": payload}
            )
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
            except Exception:
                pass
        if self._action_function:
            self._action_function(self, id, action)

    def load_config(self, app_config={}, style_config={}):
        self._config.load_config(app_config=app_config, style_config=style_config)

    def run(self, host=None, port=None, debug=None, load_dotenv=True):
        # Check with default config, override only if parameter
        # is not passed directly into the run function
        if host is None and self._config.app_config["host"] is not None:
            host = self._config.app_config["host"]
        if port is None and self._config.app_config["port"] is not None:
            port = self._config.app_config["port"]
        if debug is None and self._config.app_config["debug"] is not None:
            debug = self._config.app_config["debug"]
        # Save all local variables of the parent frame (usually __main__)
        self._dict_bind_locals = inspect.currentframe().f_back.f_locals
        # Run parse markdown to force variables binding at runtime
        # (save rendered html to page.index_html for optimization)
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
        # define a root page if needed

        # server URL Rule for flask rendered react-router
        self._server.add_url_rule("/react-router/", view_func=self.__render_route)

        # Start Flask Server
        self._server.runWithWS(
            host=host, port=port, debug=debug, load_dotenv=load_dotenv
        )
