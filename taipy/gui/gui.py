from __future__ import annotations

import ast
import datetime
import inspect
import os
import pathlib
import re
import typing as t
import warnings
from operator import attrgetter
from types import FrameType, FunctionType, SimpleNamespace

import __main__
import markdown as md_lib
from flask import Blueprint, jsonify, request

from ._default_config import default_config
from .config import GuiConfig
from .data.data_accessor import DataAccessor, _DataAccessors
from .page import Page, Partial
from .renderers import EmptyPageRenderer, PageRenderer
from .server import Server
from .taipyimage import TaipyImage
from .utils import (
    ISOToDate,
    Singleton,
    _get_dict_value,
    _get_expr_var_name,
    _MapDictionary,
    attrsetter,
    dateToISO,
    get_client_var_name,
)
from .wstype import WsType


class Gui(object, metaclass=Singleton):
    """The class that handles the Graphical User Interface."""

    __root_page_name = "TaiPy_root_page"
    # Regex to separate content from inside curly braces when evaluating f string expressions
    __EXPR_RE = re.compile(r"\{(.*?)\}")
    __EXPR_IS_EXPR = re.compile(r"[^\\][{}]")
    __EXPR_IS_EDGE_CASE = re.compile(r"^\s*{([^}]*)}\s*$")
    __EXPR_VALID_VAR_EDGE_CASE = re.compile(r"^([a-zA-Z\.\_]*)$")
    __RE_HTML = re.compile(r"(.*?)\.html")
    __RE_MD = re.compile(r"(.*?)\.md")
    __RE_JSX_RENDER_ROUTE = re.compile(r"/flask-jsx/(.*)/")
    __RE_PAGE_NAME = re.compile(r"^[\w\-\/]+$")

    # Static variable _markdown for Markdown renderer reference (taipy.gui will be registered later in Gui.run function)
    _markdown = md_lib.Markdown(
        extensions=["fenced_code", "meta", "admonition", "sane_lists", "tables", "attr_list", "md_in_html"]
    )

    def __init__(
        self,
        css_file: str = os.path.splitext(os.path.basename(__main__.__file__))[0]
        if hasattr(__main__, "__file__")
        else "Taipy",
        default_page_renderer: t.Optional[PageRenderer] = None,
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
        # Data Registry
        self._data_accessors = _DataAccessors()

        # Load default config
        self._reserved_routes: t.List[str] = ["initialize", "flask-jsx"]
        self._directory_name_of_pages: t.List[str] = []
        self._flask_blueprint: t.List[Blueprint] = []
        self._config.load_config(default_config["app_config"], default_config["style_config"])
        self._values = SimpleNamespace()
        self._adapter_for_type: t.Dict[str, FunctionType] = {}
        self._type_for_variable: t.Dict[str, str] = {}
        self._list_for_variable: t.Dict[str, str] = {}
        self._update_function = None
        self._action_function = None
        # key = expression, value = hashed value of the expression
        self._expr_to_hash: t.Dict[str, str] = {}
        # key = hashed value of the expression, value = expression
        self._hash_to_expr: t.Dict[str, str] = {}
        # key = variable name of the expression, key = list of related expressions
        # ex: {x + y}
        # "x": ["{x + y}"],
        # "y": ["{x + y}"],
        self._var_to_expr_list: t.Dict[str, t.List[str]] = {}
        # key = expression, value = list of related variables
        # "{x + y}": ["x", "y"]
        self._expr_to_var_list: t.Dict[str, t.List[str]] = {}
        if default_page_renderer:
            self.add_page(name=Gui.__root_page_name, renderer=default_page_renderer)
        if pages is not None:
            self.add_pages(pages)

    @staticmethod
    def _get_instance() -> Gui:
        return Gui._instances[Gui]

    def _render_page(self) -> t.Any:
        page = None
        render_path_name = Gui.__RE_JSX_RENDER_ROUTE.match(request.path).group(1)
        # Get page instance
        for page_i in self._config.pages:
            if page_i.route == render_path_name:
                page = page_i
        # try partials
        if page is None:
            for partial in self._config.partials:
                if partial.route == render_path_name:
                    page = partial
        # Make sure that there is a page instance found
        if page is None:
            return (jsonify({"error": "Page doesn't exist!"}), 400, {"Content-Type": "application/json; charset=utf-8"})
        if page.rendered_jsx is None:
            page.render()
            if render_path_name == Gui.__root_page_name and "<PageContent" not in page.rendered_jsx:
                page.rendered_jsx += "<PageContent />"

        # Return jsx page
        if page.rendered_jsx is not None:
            return self._server.render(page.rendered_jsx, page.style if hasattr(page, "style") else "", page.head)
        else:
            return ("No page template", 404)

    def _render_route(self) -> t.Any:
        # Generate router
        routes = self._config.routes
        locations = {}
        router = '<Router key="router"><Routes key="routes">'
        router += (
            '<Route path="/" key="'
            + Gui.__root_page_name
            + '" element={<MainPage key="tr'
            + Gui.__root_page_name
            + '" path="/'
            + Gui.__root_page_name
            + '"'
        )
        route = next((r for r in routes if r != Gui.__root_page_name), None)
        router += (' route="/' + route + '"') if route else ""
        router += ' />} >'
        locations["/"] = "/" + Gui.__root_page_name
        for route in routes:
            if route != Gui.__root_page_name:
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
        router += "</Routes></Router>"

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
            setattr(self._values, name, _MapDictionary(value))
        else:
            setattr(self._values, name, value)
        prop = property(self.__value_getter(name), lambda s, v: s._update_var(name, v))  # Getter, Setter
        setattr(Gui, name, prop)

    def __value_getter(self, name):
        def __getter(elt: Gui) -> t.Any:
            value = getattr(elt._values, name)
            if isinstance(value, _MapDictionary):
                return _MapDictionary(value._dict, lambda s, v: elt._update_var(name + "." + s, v))
            else:
                return value

        return __getter

    def _manage_message(self, msg_type: WsType, message: dict) -> None:
        try:
            if msg_type == WsType.UPDATE.value:
                self._front_end_update(
                    message["name"],
                    message["payload"],
                    message["propagate"] if "propagate" in message else True,
                )
            elif msg_type == WsType.ACTION.value:
                self._on_action(_get_dict_value(message, "name"), message["payload"])
            elif msg_type == WsType.DATA_UPDATE.value:
                self._request_data_update(message["name"], message["payload"])
            elif msg_type == WsType.REQUEST_UPDATE.value:
                self._request_var_update(message["payload"])
        except TypeError as te:
            warnings.warn(f"Decoding Message has failed: {message}\n{te}")
        except KeyError as ke:
            warnings.warn(f"Can't access: {message}\n{ke}")

    def _front_end_update(self, var_name: str, value: t.Any, propagate=True) -> None:
        # Check if Variable is type datetime
        currentvalue = attrgetter(self._expr_to_hash[var_name])(self._values)
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
            elif self._data_accessors._cast_string_value(var_name, currentvalue) is None:
                return
        self._update_var(var_name, value, propagate)

    def _update_var(self, var_name: str, value: t.Any, propagate=True) -> None:
        hash_expr = self._expr_to_hash[var_name]
        modified_vars = [hash_expr]
        # Use custom attrsetter function to allow value binding for MapDictionary
        if propagate:
            attrsetter(self._values, hash_expr, value)
            # In case expression == hash (which is when there is only a single variable in expression)
            if var_name == hash_expr:
                modified_vars.extend(self._re_evaluate_expr(var_name))
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if self._update_function:
            self._update_function(self, var_name, value)
        self.__send_var_list_update(modified_vars)

    def __send_var_list_update(self, modified_vars: list):
        ws_dict = {}
        for _var in modified_vars:
            newvalue = attrgetter(_var)(self._values)
            if isinstance(newvalue, datetime.datetime):
                newvalue = dateToISO(newvalue)
            if self._data_accessors._is_data_access(_var, newvalue):
                ws_dict[_var + ".refresh"] = True
            else:
                if isinstance(newvalue, list):
                    new_list = [self._run_adapter_for_var(_var, elt, idx) for idx, elt in enumerate(newvalue)]
                    newvalue = new_list
                else:
                    newvalue = self._run_adapter_for_var(_var, newvalue, id_only=True)
                    if isinstance(newvalue, _MapDictionary):
                        continue  # this var has no transformer
                ws_dict[_var] = newvalue

        # TODO: What if value == newvalue?
        self._send_ws_update_with_dict(ws_dict)

    def _request_data_update(self, var_name: str, payload: t.Any) -> None:
        # Use custom attrgetter function to allow value binding for MapDictionary
        var_name = self._expr_to_hash[var_name]
        newvalue = attrgetter(var_name)(self._values)
        ret_payload = self._data_accessors._get_data(var_name, newvalue, payload)
        self._send_ws_update_with_dict({var_name: ret_payload, var_name + ".refresh": False})

    def _request_var_update(self, payload):
        if "names" in payload and isinstance(payload["names"], list):
            self.__send_var_list_update(payload["names"])

    def _send_ws_update(self, var_name: str, payload: dict) -> None:
        try:
            self._server._ws.send(
                {"type": WsType.UPDATE.value, "name": get_client_var_name(var_name), "payload": payload}
            )
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _send_ws_update_with_dict(self, modified_values: dict) -> None:
        payload = [
            {"name": get_client_var_name(k), "payload": (v if isinstance(v, dict) and "value" in v else {"value": v})}
            for k, v in modified_values.items()
        ]
        try:
            self._server._ws.send({"type": WsType.MULTIPLE_UPDATE.value, "payload": payload})
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _on_action(self, id: t.Optional[str], payload: t.any) -> None:
        if isinstance(payload, dict):
            action = _get_dict_value(payload, "action")
        else:
            action = str(payload)
        if action and hasattr(self, action):
            if self.__call_function_with_args(action_function=getattr(self, action), id=id, payload=payload):
                return
        if self._action_function:
            self.__call_function_with_args(action_function=self._action_function, id=id, payload=payload, action=action)

    def __call_function_with_args(*args, **kwargs):
        action_function = _get_dict_value(kwargs, "action_function")
        id = _get_dict_value(kwargs, "id")
        action = _get_dict_value(kwargs, "action")
        payload = _get_dict_value(kwargs, "payload")
        pself = args[0]

        if isinstance(action_function, FunctionType):
            try:
                argcount = action_function.__code__.co_argcount
                if argcount == 0:
                    action_function()
                elif argcount == 1:
                    action_function(pself)
                elif argcount == 2:
                    action_function(pself, id)
                elif argcount == 3:
                    if action is not None:
                        action_function(pself, id, action)
                    else:
                        action_function(pself, id, payload)
                elif argcount == 4 and action is not None:
                    action_function(pself, id, action, payload)
                else:
                    warnings.warn(f"Wrong signature for action '{action_function.__name__}'")
                    return False
                return True
            except Exception as e:
                warnings.warn(f"on action '{action_function.__name__}' exception: {e}")
        return False

    def _re_evaluate_expr(self, var_name: str) -> t.List:
        """
        This function will execute when the _update_var function is handling
        an expression with only a single variable
        """
        modified_vars: t.List[str] = []
        if var_name not in self._var_to_expr_list.keys():
            return modified_vars
        for expr in self._var_to_expr_list[var_name]:
            if expr == var_name:
                continue
            hash_expr = self._expr_to_hash[expr]
            expr_var_list = self._expr_to_var_list[expr]  # ["x", "y"]
            eval_dict = {v: attrgetter(v)(self._values) for v in expr_var_list}

            if self._is_expression(expr):
                expr_string = 'f"' + expr.replace('"', '\\"') + '"'
            else:
                expr_string = expr

            expr_evaluated = eval(expr_string, {}, eval_dict)
            attrsetter(self._values, hash_expr, expr_evaluated)
            modified_vars.append(hash_expr)
        return modified_vars

    def _is_expression(self, expr: str) -> bool:
        return len(Gui.__EXPR_IS_EXPR.findall(expr)) != 0

    def _fetch_expression_list(self, expr: str) -> t.List:
        return Gui.__EXPR_RE.findall(expr)

    def add_page(
        self,
        name: str,
        renderer: PageRenderer,
        style: t.Optional[str] = "",
    ) -> None:
        # Validate name
        if name is None:
            raise Exception("name is required for add_page function!")
        if not Gui.__RE_PAGE_NAME.match(name):
            raise SyntaxError(
                f'Page name "{name}" is invalid. It must only contain letters, digits, dash (-), underscore (_), and forward slash (/) characters.'
            )
        if name.startswith("/"):
            raise SyntaxError(f'Page name "{name}" cannot start with forward slash (/) character')
        if name in self._config.routes:
            raise Exception(f'Page name "{name if name != Gui.__root_page_name else "/"}" is already defined')
        if not isinstance(renderer, PageRenderer):
            raise Exception(f'Page name "{name if name != Gui.__root_page_name else "/"}" has invalid PageRenderer')
        # Init a new page
        new_page = Page()
        new_page.route = name
        new_page.renderer = renderer
        new_page.style = style
        # Append page to _config
        self._config.pages.append(new_page)
        self._config.routes.append(name)

    def add_pages(self, pages: t.Union[dict[str, PageRenderer], str] = None) -> None:
        if isinstance(pages, dict):
            for k, v in pages.items():
                if k == "/":
                    k = Gui.__root_page_name
                self.add_page(name=k, renderer=v)
        elif isinstance(folder_name := pages, str):
            if not hasattr(self, "_root_dir"):
                self._root_dir = os.path.dirname(
                    inspect.getabsfile(t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back))
                )
            folder_path = os.path.join(self._root_dir, folder_name) if not os.path.isabs(folder_name) else folder_name
            folder_name = os.path.basename(folder_path)
            if not os.path.isdir(folder_path):
                raise RuntimeError(f"Path {folder_path} is not a valid directory")
            if folder_name in self._directory_name_of_pages:
                raise Exception(f"Base directory name {folder_name} of path {folder_path} is not unique")
            if folder_name in self._reserved_routes:
                raise Exception(f"Invalid directory. Directory {folder_name} is a reserved route")
            self._directory_name_of_pages.append(folder_name)
            list_of_files = os.listdir(folder_path)
            for file_name in list_of_files:
                from .renderers import Html, Markdown

                if re_match := Gui.__RE_HTML.match(file_name):
                    renderers = Html(os.path.join(folder_path, file_name))
                    renderers.modify_taipy_base_url(folder_name)
                    self.add_page(name=re_match.group(1), renderer=renderers)
                elif re_match := Gui.__RE_MD.match(file_name):
                    renderers_md = Markdown(os.path.join(folder_path, file_name))
                    self.add_page(name=re_match.group(1), renderer=renderers_md)
                elif os.path.isdir(assets_folder := os.path.join(folder_path, file_name)):
                    assets_dir_name = f"{folder_name}/{file_name}"
                    self._flask_blueprint.append(
                        Blueprint(
                            assets_dir_name, __name__, static_folder=assets_folder, url_prefix=f"/{assets_dir_name}"
                        )
                    )

    def add_partial(
        self,
        renderer: PageRenderer,
    ) -> Partial:
        # Init a new partial
        new_partial = Partial()
        # Validate name
        if new_partial.route in self._config.partial_routes or new_partial.route in self._config.routes:
            warnings.warn(f'Partial name "{new_partial.route}" is already defined')
        if not isinstance(renderer, PageRenderer):
            raise Exception(f'Partial name "{new_partial.route}" has invalid PageRenderer')
        new_partial.renderer = renderer
        # Append partial to _config
        self._config.partials.append(new_partial)
        self._config.partial_routes.append(new_partial.route)
        return new_partial

    def _add_list_for_variable(self, var_name: str, list_name: str) -> None:
        self._list_for_variable[var_name] = list_name

    def add_adapter_for_type(self, type_name: str, adapter: FunctionType) -> None:
        self._adapter_for_type[type_name] = adapter

    def add_type_for_var(self, var_name: str, type_name: str) -> None:
        self._type_for_variable[var_name] = type_name

    def _get_adapter_for_type(self, type_name: str) -> t.Optional[FunctionType]:
        return _get_dict_value(self._adapter_for_type, type_name)

    def _run_adapter_for_var(self, var_name: str, value: t.Any, index: t.Optional[int] = None, id_only=False) -> t.Any:
        adapter = None
        type_name = _get_dict_value(self._type_for_variable, var_name)
        if not isinstance(type_name, str):
            adapter = _get_dict_value(self._adapter_for_type, var_name)
            if isinstance(adapter, FunctionType):
                type_name = var_name
            else:
                type_name = type(value).__name__
        if adapter is None:
            adapter = _get_dict_value(self._adapter_for_type, type_name)
        if isinstance(adapter, FunctionType):
            ret = self._run_adapter(adapter, value, var_name, index, id_only)
            if ret is not None:
                return ret
        return value

    def _run_adapter(
        self, adapter: FunctionType, value: t.Any, var_name: str, index: t.Optional[int], id_only=False
    ) -> t.Union[tuple[str, t.Union[str, TaipyImage]], str, None]:
        try:
            result = adapter(value if not isinstance(value, _MapDictionary) else value._dict)
            result = self._get_valid_adapter_result(result, index, id_only)
            if result is None:
                warnings.warn(
                    f"Adapter for {var_name} does not return a valid result. It should return a type (id, label) or a label with label being a string or a TaipyImage instance"
                )
            else:
                return result
        except Exception as e:
            warnings.warn(f"Can't run adapter for {var_name}: {e}")
        return None

    def _get_valid_adapter_result(
        self, value: t.Any, index: t.Optional[int], id_only=False
    ) -> t.Union[tuple[str, t.Union[str, TaipyImage]], str, None]:
        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], str)
            and isinstance(value[1], (str, TaipyImage))
        ):
            if id_only:
                return value[0]
            else:
                return (value[0], TaipyImage.get_dict_or(value[1]))  # type: ignore
        elif isinstance(value, (str, TaipyImage)):
            if id_only:
                return self._get_id(value, index)
            else:
                return (self._get_id(value, index), TaipyImage.get_dict_or(value))  # type: ignore
        return None

    def _get_id(self, value: t.Any, index: t.Optional[int]) -> str:
        if hasattr(value, "id"):
            return str(value.id)
        elif hasattr(value, "__getitem__") and "id" in value:
            return str(value["id"])
        elif index is not None:
            return str(index)
        else:
            return id(value)  # type: ignore

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
            and func_name in (self._get_instance()._locals_bind)
            and isinstance((self._get_instance()._locals_bind[func_name]), FunctionType)
        ):
            setattr(self, func_name, self._get_instance()._locals_bind[func_name])
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
                    try:
                        var_val[var_name] = attrgetter(var_name)(self._values)
                        var_list.append(var_name)
                    except AttributeError:
                        warnings.warn(f"Variable '{var_name}' is not defined")
        # The expr_string is placed here in case expr get replaced by edge case
        expr_string = 'f"' + expr.replace('"', '\\"') + '"'
        # simplify expression if it only contains var_name
        m = Gui.__EXPR_IS_EDGE_CASE.match(expr)
        if m:
            expr = m.group(1)
            expr_hash = expr if Gui.__EXPR_VALID_VAR_EDGE_CASE.match(expr) else None
            is_edge_case = True
        # validate whether expression has already been evaluated
        if expr in self._expr_to_hash:
            return "{" + self._expr_to_hash[expr] + "}"
        try:
            # evaluate expressions
            expr_evaluated = eval(expr_string if not is_edge_case else expr, {}, var_val)
        except Exception:
            warnings.warn(f"Cannot evaluate expression '{expr if is_edge_case else expr_string}'")
            expr_evaluated = None
        # save the expression if it needs to be re-evaluated
        if re_evaluated:
            if expr_hash is None:
                expr_hash = self._expr_to_hash[expr] = _get_expr_var_name(expr)
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

    def register_data_accessor(self, data_accessor_class: t.Type[DataAccessor]) -> None:
        self._data_accessors.register(data_accessor_class)

    def run(self, host=None, port=None, debug=None, run_server=True) -> None:
        # Check with default config, override only if parameter
        # is not passed directly into the run function
        if host is None and self._config.app_config["host"] is not None:
            host = self._config.app_config["host"]
        if port is None and self._config.app_config["port"] is not None:
            port = self._config.app_config["port"]
        if debug is None and self._config.app_config["debug"] is not None:
            debug = self._config.app_config["debug"]
        # Register taipy.gui markdown extensions for Markdown renderer
        Gui._markdown.registerExtensions(extensions=["taipy.gui"], configs={})
        # Save all local variables of the parent frame (usually __main__)
        self._locals_bind: t.Dict[str, t.Any] = t.cast(
            FrameType, t.cast(FrameType, inspect.currentframe()).f_back
        ).f_locals

        # add en empty main page if it is not defined
        if Gui.__root_page_name not in self._config.routes:
            new_page = Page()
            new_page.route = Gui.__root_page_name
            new_page.renderer = EmptyPageRenderer()
            self._config.pages.append(new_page)
            self._config.routes.append(Gui.__root_page_name)

        # Run parse markdown to force variables binding at runtime
        # (save rendered html to page.rendered_jsx for optimization)
        for page in self._config.pages + self._config.partials:
            # Server URL Rule for each page jsx
            self._server.add_url_rule(f"/flask-jsx/{page.route}/", view_func=self._render_page)

        # server URL Rule for flask rendered react-router
        self._server.add_url_rule("/initialize/", view_func=self._render_route)

        # Register Flask Blueprint if available
        for bp in self._flask_blueprint:
            self._server.register_blueprint(bp)

        self._server._set_client_url(self._config.app_config["client_url"])

        # Start Flask Server
        if run_server:
            self._server.runWithWS(host=host, port=port, debug=debug)

    def get_flask_app(self):
        return self._server
