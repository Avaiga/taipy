import datetime
import inspect
import os
import pathlib
import re
import typing as t
import hashlib
import ast
import warnings
from operator import attrgetter
from types import FunctionType, SimpleNamespace

import __main__
import pandas as pd
from flask import jsonify, request
from markdown import Markdown

from .Partial import Partial
from ._default_config import default_config
from ._md_ext import *
from .config import GuiConfig
from .Page import Page
from .server import Server
from .wstype import WsType
from .utils import (
    ISOToDate,
    Singleton,
    _MapDictionary,
    attrsetter,
    dateToISO,
    get_client_var_name,
    get_date_col_str_name,
)


class Gui(object, metaclass=Singleton):
    """The class that handles the Graphical User Interface."""

    __root_page_name = "TaiPy_root_page"
    # Regex to separate content from inside curly braces when evaluating f string expressions
    __EXPR_RE = re.compile(r"\{(.*?)\}")
    __EXPR_IS_EXPR = re.compile(r"[^\\][{}]")
    __EXPR_IS_EDGE_CASE = re.compile(r"^\s*?\{(.*?)\}\s*?$")
    __EXPR_VALID_VAR_EDGE_CASE = re.compile(r"^([a-zA-Z\.\_]*)$")

    def __init__(
        self,
        css_file: t.Optional[str] = os.path.splitext(os.path.basename(__main__.__file__))[0]
        if hasattr(__main__, "__file__")
        else "Taipy",
        markdown: t.Optional[str] = None,
        markdown_file: t.Optional[str] = None,
        pages: t.Optional[dict] = None,
        path_mapping: t.Optional[dict] = {},
    ):
        _absolute_path = str(pathlib.Path(__file__).parent.resolve())
        self._server = Server(
            self,
            css_file=css_file,
            static_folder=f"{_absolute_path}{os.path.sep}webapp",
            template_folder=f"{_absolute_path}{os.path.sep}webapp",
            path_mapping=path_mapping,
        )
        self._config = GuiConfig()
        # Load default config
        self._config.load_config(default_config["app_config"], default_config["style_config"])
        self._values = SimpleNamespace()
        self._update_function = None
        self._action_function = None
        # key = expression, value = hashed value of the expression
        self._expr_to_hash = {}
        # key = hashed value of the expression, value = expression
        self._hash_to_expr = {}
        # key = variable name of the expression, key = list of related expressions
        # ex: {x + y}
        # "x": ["{x + y}"],
        # "y": ["{x + y}"],
        self._var_to_expr_list = {}
        # key = expression, value = list of related variables
        # "{x + y}": ["x", "y"]
        self._expr_to_var_list = {}
        self._markdown = Markdown(
            extensions=["taipy.gui", "fenced_code", "meta", "admonition", "sane_lists", "tables", "attr_list"]
        )
        if markdown:
            self.add_page(name=Gui.__root_page_name, markdown=markdown)
        if markdown_file:
            if markdown:
                raise Exception(
                    "Cannot specify both markdown and markdown_file parameters. Consider using the pages parameter."
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
        # try partials
        if page is None:
            for partial in self._config.partials:
                if partial.route in request.path:
                    page = partial
        # Make sure that there is a page instance found
        if page is None:
            return (jsonify({"error": "Page doesn't exist!"}), 400, {"Content-Type": "application/json; charset=utf-8"})
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
                page.style if hasattr(page, "style") else "",
            )
        else:
            return "No page template"

    def _render_route(self):
        # Generate router
        routes = self._config.routes
        locations = {}
        router = '<Router key="router"><Switch key="switch">'
        for route in routes:
            router += (
                '<Route path="/'
                + (route if route != Gui.__root_page_name else "")
                + '" exact key="'
                + route
                + '" ><TaipyRendered key="tr'
                + route
                + '"/></Route>'
            )
            locations["/" + (route if route != Gui.__root_page_name else "")] = "/" + route
        if Gui.__root_page_name not in routes:
            router += (
                '<Route path="/" exact key="'
                + Gui.__root_page_name
                + '" ><TaipyRendered key="tr'
                + Gui.__root_page_name
                + '"/></Route>'
            )
            locations["/"] = "/" + routes[0]

        router += '<Route path="/404" exact key="404" ><NotFound404 key="tr404" /></Route>'
        router += '<Redirect to="/' + routes[0] + '" key="Redirect" />'
        router += "</Switch></Router>"

        return self._server._direct_render_json(
            {
                "router": router,
                "locations": locations,
                "timeZone": self._config.get_time_zone(),
                "darkMode": self._config.app_config["dark_mode"],
            }
        )

    # TODO: Check name value to avoid conflicting with Flask,
    # or, simply, compose with Flask instead of inherit from it.
    def _bind(self, name: str, value: t.Any) -> None:
        if hasattr(self, name):
            raise ValueError(f"Variable '{name}' is already bound")
        if not name.isidentifier():
            raise ValueError(f"Variable name '{name}' is invalid")
        if isinstance(value, dict):
            setattr(Gui, name, _MapDictionary(value, lambda s, v: self._update_var(name + "." + s, v)))
            setattr(self._values, name, _MapDictionary(value))
        else:
            prop = property(
                lambda s: getattr(s._values, name),  # Getter
                lambda s, v: s._update_var(name, v),  # Setter
            )
            setattr(Gui, name, prop)
            setattr(self._values, name, value)

    def _update_var(self, var_name: str, value, propagate=True) -> None:
        # Check if Variable is type datetime
        expr = var_name
        hash_expr = var_name = self._expr_to_hash[var_name]
        currentvalue = attrgetter(var_name)(self._values)
        if isinstance(value, str):
            if isinstance(currentvalue, datetime.datetime):
                value = ISOToDate(value)
            elif isinstance(currentvalue, int):
                value = int(value) if value else 0
            elif isinstance(currentvalue, float):
                value = float(value) if value else 0.0
            elif isinstance(currentvalue, complex):
                value = complex(value) if value else 0
            elif isinstance(currentvalue, bool):
                value = bool(value)
            elif isinstance(currentvalue, pd.DataFrame):
                warnings.warn("Error: cannot update value for dataframe: " + var_name)
                return
        modified_vars = [var_name]
        # Use custom attrsetter function to allow value binding for MapDictionary
        if propagate:
            attrsetter(self._values, var_name, value)
            # In case expression == hash (which is when there is only a single variable in expression)
            if expr == hash_expr:
                modified_vars.extend(self._re_evaluate_expr(expr))
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if self._update_function:
            self._update_function(self, expr, value)
        ws_dict = {}
        for _var in modified_vars:
            newvalue = attrgetter(_var)(self._values)
            if isinstance(newvalue, datetime.datetime):
                newvalue = dateToISO(newvalue)
            if isinstance(newvalue, pd.DataFrame):
                ws_dict[_var + ".refresh"] = True
            else:
                ws_dict[_var] = newvalue
        # TODO: What if value == newvalue?
        self._send_ws_update_with_dict(ws_dict)

    def _request_var(self, var_name, payload) -> None:
        ret_payload = {}
        # Use custom attrgetter function to allow value binding for MapDictionary
        var_name = self._expr_to_hash[var_name]
        newvalue = attrgetter(var_name)(self._values)
        if isinstance(newvalue, datetime.datetime):
            newvalue = dateToISO(newvalue)
        elif isinstance(newvalue, pd.DataFrame):
            keys = payload.keys()
            ret_payload["pagekey"] = payload["pagekey"] if "pagekey" in keys else "unknown page"
            if "infinite" in keys:
                ret_payload["infinite"] = payload["infinite"]
            if isinstance(payload["start"], int):
                start = int(payload["start"])
            else:
                try:
                    start = int(str(payload["start"]), base=10)
                except Exception as e:
                    warnings.warn(f'start should be an int value {payload["start"]}')
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
            datecols = newvalue.dtypes[newvalue.dtypes.astype("string").str.startswith("datetime")].index.tolist()
            if len(datecols) != 0:
                # copy the df so that we don't "mess" with the user's data
                newvalue = newvalue.copy()
                for col in datecols:
                    newcol = get_date_col_str_name(newvalue, col)
                    newvalue[newcol] = newvalue[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ").astype("string")
            if "orderby" in keys and isinstance(payload["orderby"], str) and len(payload["orderby"]):
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
                # remove the date columns from the list of columns
                cols = list(set(newvalue.columns.tolist()) - set(datecols))
                newvalue = newvalue.loc[:, cols]  # view without the date columns
            dictret = {"data": newvalue.to_dict(orient="records"), "rowcount": rowcount, "start": start}
            newvalue = dictret
        # TODO: What if value == newvalue?
        ret_payload["value"] = newvalue
        self._send_ws_update_with_dict({var_name: ret_payload, var_name + ".refresh": False})

    def _send_ws_update(self, var_name: str, payload: dict) -> None:
        try:
            self._server._ws.send(
                {"type": WsType.UPDATE.value, "name": get_client_var_name(var_name), "payload": payload}
            )
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _send_ws_update_with_dict(self, modified_values: dict) -> None:
        payload = [
            {"name": get_client_var_name(k), "payload": (v if isinstance(v, dict) else {"value": v})}
            for k, v in modified_values.items()
        ]
        try:
            self._server._ws.send({"type": WsType.MULTIPLE_UPDATE.value, "payload": payload})
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _on_action(self, id, action):
        if action:
            try:
                action_function = getattr(self, action)
                argcount = action_function.__code__.co_argcount
                if argcount == 0:
                    action_function()
                elif argcount == 1:
                    action_function(self)
                elif argcount == 2:
                    action_function(self, id)
                return
            except Exception as e:
                warnings.warn(f"on action exception: {e}")
                pass
        if self._action_function:
            self._action_function(self, id, action)

    def _re_evaluate_expr(self, var_name: str) -> t.List:
        """
        This function will execute when the _update_var function is handling
        an expression with only a single variable
        """
        modified_vars = []
        if var_name not in self._var_to_expr_list.keys():
            return modified_vars
        for expr in self._var_to_expr_list[var_name]:
            if expr == var_name or not self._is_expression(expr):
                continue
            hash_expr = self._expr_to_hash[expr]
            expr_var_list = self._expr_to_var_list[expr]  # ["x", "y"]
            eval_dict = {v: attrgetter(v)(self._values) for v in expr_var_list}
            expr_string = 'f"' + expr.replace('"', '\\"') + '"'
            if hash_expr == expr:
                expr_string = expr
            expr_evaluated = eval(expr_string, {}, eval_dict)
            attrsetter(self._values, hash_expr, expr_evaluated)
            self._send_ws_update(hash_expr, {"value": expr_evaluated})
            modified_vars.append(var_name)
        return modified_vars

    def _is_expression(self, expr: str) -> bool:
        return len(Gui.__EXPR_IS_EXPR.findall(expr)) != 0

    def _fetch_expression_list(self, expr: str) -> t.List:
        return Gui.__EXPR_RE.findall(expr)

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
                f'Page name "{name}" is invalid. It must contain only letters, digits, dash (-) and underscore (_) characters.'
            )
        if name in self._config.routes:
            raise Exception(f'Page name "{name if name != Gui.__root_page_name else "/"}" is already defined')
        # Init a new page
        new_page = Page()
        new_page.route = name
        new_page.md_template = markdown
        new_page.md_template_file = markdown_file
        new_page.style = style
        # Append page to _config
        self._config.pages.append(new_page)
        self._config.routes.append(name)

    def add_partial(
        self,
        markdown: t.Optional[str] = None,
        markdown_file: t.Optional[str] = None,
    ) -> Partial:
        # Init a new partial
        new_partial = Partial(markdown=markdown, markdown_file=markdown_file)
        # Validate name
        if new_partial.route in self._config.partial_routes or new_partial.route in self._config.routes:
            warnings.warn(f'Partial name "{new_partial.route}" is already defined')
        # Append partial to _config
        self._config.partials.append(new_partial)
        self._config.partial_routes.append(new_partial.route)
        return new_partial

    # Main binding method (bind in markdown declaration)
    def bind_var(self, var_name: str) -> bool:
        if not hasattr(self, var_name) and var_name in self._locals_bind:
            self._bind(var_name, self._locals_bind[var_name])
            return True
        return False

    def bind_var_val(self, var_name: str, value: t.Any) -> bool:
        if not hasattr(self, var_name):
            self._bind(var_name, value)
            return True
        return False

    def bind_func(self, func_name: str) -> bool:
        if (
            isinstance(func_name, str)
            and not hasattr(self, func_name)
            and func_name in (bind_locals := self._get_instance()._locals_bind)
            and isinstance((func := bind_locals[func_name]), FunctionType)
        ):
            setattr(self, func_name, func)
            return True
        return False

    def evaluate_expr(self, expr: str, re_evaluated: t.Optional[bool] = True) -> t.Any:
        if not self._is_expression(expr):
            return expr
        var_val = {}
        var_list = []
        expr_hash = None
        is_edge_case = False
        # Get A list of expressions (value that has been wrapped in curly braces {}) and find variables to bind
        for e in self._fetch_expression_list(expr):
            st = ast.parse(e)
            for node in ast.walk(st):
                if type(node) is ast.Name:
                    var_name = node.id.split(sep=".")[0]
                    self.bind_var(var_name)
                    var_list.append(var_name)
                    var_val[var_name] = attrgetter(var_name)(self._values)
        # The expr_string is placed here in case expr get replaced by edge case
        expr_string = 'f"' + expr.replace('"', '\\"') + '"'
        # simplify expression if it only contains var_name
        if m := Gui.__EXPR_IS_EDGE_CASE.match(expr):
            expr = m.group(1)
            expr_hash = expr if Gui.__EXPR_VALID_VAR_EDGE_CASE.match(expr) else None
            is_edge_case = True
        # validate whether expression has already been evaluated
        if expr in self._expr_to_hash:
            return "{" + self._expr_to_hash[expr] + "}"
        # evaluate expressions
        expr_evaluated = eval(expr_string, {}, var_val) if not is_edge_case else eval(expr, {}, var_val)
        # save the expression if it needs to be re-evaluated
        if re_evaluated:
            if expr_hash is None:
                expr_hash = self._expr_to_hash[expr] = "tp_" + hashlib.md5(expr.encode()).hexdigest()
                self.bind_var_val(expr_hash, expr_evaluated)
            else:
                self._expr_to_hash[expr] = expr
            self._hash_to_expr[expr_hash] = expr
            for var in var_val:
                if var not in self._var_to_expr_list:
                    self._var_to_expr_list[var] = [expr]
                else:
                    self._var_to_expr_list[var].append(expr)
            if expr not in self._expr_to_var_list:
                self._expr_to_var_list[expr] = var_list
            return "{" + expr_hash + "}"
        return expr_evaluated

    def on_update(self, f) -> None:
        self._update_function = f

    def on_action(self, f) -> None:
        self._action_function = f

    def load_config(self, app_config: t.Optional[dict] = {}, style_config: t.Optional[dict] = {}) -> None:
        self._config.load_config(app_config=app_config, style_config=style_config)

    def run(self, host=None, port=None, debug=None, load_dotenv=True) -> None:
        # Check with default config, override only if parameter
        # is not passed directly into the run function
        if host is None and self._config.app_config["host"] is not None:
            host = self._config.app_config["host"]
        if port is None and self._config.app_config["port"] is not None:
            port = self._config.app_config["port"]
        if debug is None and self._config.app_config["debug"] is not None:
            debug = self._config.app_config["debug"]
        # Save all local variables of the parent frame (usually __main__)
        self._locals_bind = inspect.currentframe().f_back.f_locals
        # Run parse markdown to force variables binding at runtime
        # (save rendered html to page.index_html for optimization)
        for page_i in self._config.pages:
            if page_i.md_template:
                page_i.index_html = self._parse_markdown(page_i.md_template)
            elif page_i.md_template_file:
                with open(page_i.md_template_file, "r") as f:
                    page_i.index_html = self._parse_markdown(f.read())
            # Server URL Rule for each page jsx
            self._server.add_url_rule(f"/flask-jsx/{page_i.route}/", view_func=self._render_page)
        for partial in self._config.partials:
            if partial.md_template:
                partial.index_html = self._parse_markdown(partial.md_template)
            elif partial.md_template_file:
                with open(partial.md_template_file, "r") as f:
                    partial.index_html = self._parse_markdown(f.read())
            # Server URL Rule for each page jsx
            self._server.add_url_rule(f"/flask-jsx/{partial.route}/", view_func=self._render_page)

        # server URL Rule for flask rendered react-router
        self._server.add_url_rule("/initialize/", view_func=self._render_route)

        # Start Flask Server
        self._server.runWithWS(host=host, port=port, debug=debug, load_dotenv=load_dotenv)
