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
from dotenv import dotenv_values
from flask import Blueprint, jsonify, request

from ._default_config import app_config_default, style_config_default
from .config import AppConfigOption, GuiConfig
from .data.data_accessor import DataAccessor, _DataAccessors
from .data.data_format import DataFormat
from .data.data_scope import _DataScopes
from .expression_evaluator import _ExpressionEvaluator
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
    __env_filename = "taipy.gui.env"

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
        env_filename: t.Optional[str] = None,
    ):
        """Initializes a new Gui instance.

        Parameters:
            css_file (string):  An optional pathname to a CSS file that gets used as a style sheet in
                all the pages.

                The default value is a file that has the same basename as the Python
                file defining the `main` function, sitting next to this Python file,
                with the `.css` extension.

            default_page_renderer (PageRenderer): An optional `PageRenderer` class that is used to render pages.
        """
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

        # Data Scopes
        self._data_scopes = _DataScopes()

        self._expression_evaluator = _ExpressionEvaluator()

        # Load default config
        self._reserved_routes: t.List[str] = ["initialize", "flask-jsx"]
        self._directory_name_of_pages: t.List[str] = []
        self._flask_blueprint: t.List[Blueprint] = []
        self._config.load_config(app_config_default, style_config_default)
        self._adapter_for_type: t.Dict[str, FunctionType] = {}
        self._type_for_variable: t.Dict[str, str] = {}
        self._list_for_variable: t.Dict[str, str] = {}
        self._update_function = None
        self._action_function = None
        if default_page_renderer:
            self.add_page(name=Gui.__root_page_name, renderer=default_page_renderer)
        if pages is not None:
            self.add_pages(pages)
        if env_filename is not None:
            self.__env_filename = env_filename

    @staticmethod
    def _get_instance() -> Gui:
        return Gui._instances[Gui]

    def _render_page(self) -> t.Any:
        page = None
        render_path_name = Gui.__RE_JSX_RENDER_ROUTE.match(request.path).group(1)  # type: ignore
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
        # TODO: assign global scopes to current scope if the page has been rendered
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
        router += " />} >"
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
                "darkMode": self._get_app_config("dark_mode", True),
            }
        )

    def _get_data_scope(self):
        return self._data_scopes.get_scope()

    # TODO: Check name value to avoid conflicting with Flask,
    # or, simply, compose with Flask instead of inherit from it.
    def _bind(self, name: str, value: t.Any) -> None:
        if hasattr(self, name):
            raise ValueError(f"Variable '{name}' is already bound")
        if not name.isidentifier():
            raise ValueError(f"Variable name '{name}' is invalid")
        if isinstance(value, dict):
            setattr(self._get_data_scope(), name, _MapDictionary(value))
            self._bind_global(name, _MapDictionary(value))
        else:
            setattr(self._get_data_scope(), name, value)
            self._bind_global(name, value)
        prop = property(self.__value_getter(name), lambda s, v: s._update_var(name, v))  # Getter, Setter
        setattr(Gui, name, prop)

    def _bind_global(self, name: str, value: t.Any) -> None:
        global_scope = self._data_scopes.get_global_scope()
        if hasattr(global_scope, name):
            return
        setattr(global_scope, name, value)

    def __value_getter(self, name):
        def __getter(elt: Gui) -> t.Any:
            value = getattr(elt._get_data_scope(), name)
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
        currentvalue = attrgetter(self._get_hash_from_expr(var_name))(self._get_data_scope())
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
        hash_expr = self._get_hash_from_expr(var_name)
        modified_vars = [hash_expr]
        # Use custom attrsetter function to allow value binding for MapDictionary
        if propagate:
            attrsetter(self._get_data_scope(), hash_expr, value)
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
            newvalue = attrgetter(_var)(self._get_data_scope())
            self._data_scopes.broadcast_data(_var, newvalue)
            if isinstance(newvalue, datetime.datetime):
                newvalue = dateToISO(newvalue)
            if self._data_accessors._is_data_access(_var, newvalue):
                ws_dict[_var + ".refresh"] = True
            else:
                if isinstance(newvalue, list):
                    new_list = [self._run_adapter_for_var(_var, elt, str(idx)) for idx, elt in enumerate(newvalue)]
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
        var_name = self._get_hash_from_expr(var_name)
        newvalue = attrgetter(var_name)(self._get_data_scope())
        ret_payload = self._data_accessors._get_data(var_name, newvalue, payload)
        self._send_ws_update_with_dict({var_name: ret_payload, var_name + ".refresh": False})

    def _request_var_update(self, payload):
        if "names" in payload and isinstance(payload["names"], list):
            self.__send_var_list_update(payload["names"])

    def _send_ws_update(self, var_name: str, payload: dict) -> None:
        try:
            self._server._ws.emit(
                "message",
                {"type": WsType.UPDATE.value, "name": get_client_var_name(var_name), "payload": payload},
                to=self._get_ws_receiver(),
            )
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _send_ws_alert(self, type: str, message: str, browser_notification: bool, duration: int) -> None:
        try:
            self._server._ws.emit(
                "message",
                {
                    "type": WsType.ALERT.value,
                    "atype": type,
                    "message": message,
                    "browser": browser_notification,
                    "duration": duration,
                },
                to=self._get_ws_receiver(),
            )
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _send_ws_update_with_dict(self, modified_values: dict) -> None:
        payload = [
            {"name": get_client_var_name(k), "payload": (v if isinstance(v, dict) and "value" in v else {"value": v})}
            for k, v in modified_values.items()
        ]
        try:
            self._server._ws.emit(
                "message",
                {"type": WsType.MULTIPLE_UPDATE.value, "payload": payload},
                to=self._get_ws_receiver(),
            )
        except Exception as e:
            warnings.warn(f"Web Socket communication error {e}")

    def _get_ws_receiver(self) -> t.Union[str, None]:
        if not hasattr(request, "sid") or not self._data_scopes.get_multi_user():
            return None
        return request.sid  # type: ignore

    def _on_action(self, id: t.Optional[str], payload: t.Any) -> None:
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

    def _run_adapter_for_var(self, var_name: str, value: t.Any, index: t.Optional[str] = None, id_only=False) -> t.Any:
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
        self, adapter: FunctionType, value: t.Any, var_name: str, index: t.Optional[str], id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        if value is None:
            return None
        try:
            result = adapter(value if not isinstance(value, _MapDictionary) else value._dict)
            result = self._get_valid_adapter_result(result, index, id_only)
            if result is None:
                warnings.warn(
                    f"Adapter for {var_name} does not return a valid result. It should return a tuple (id, label) or a label with label being a string or a TaipyImage instance"
                )
            else:
                if not id_only and len(result) > 2 and isinstance(result[2], list):
                    result = (result[0], result[1], self.__adapter_on_tree(adapter, result[2], str(index) + "."))
                return result
        except Exception as e:
            warnings.warn(f"Can't run adapter for {var_name}: {e}")
        return None

    def __adapter_on_tree(self, adapter: FunctionType, tree: t.List[t.Any], prefix: str):
        ret_list = []
        for idx, elt in enumerate(tree):
            ret = self._run_adapter(adapter, elt, adapter.__name__, prefix + str(idx))
            if ret is not None:
                if len(ret) > 2 and isinstance(ret[2], list):
                    ret = (ret[0], ret[1], self.__adapter_on_tree(adapter, ret[2], prefix + str(idx) + "."))
                ret_list.append(ret)
        return ret_list

    def _get_valid_adapter_result(
        self, value: t.Any, index: t.Optional[str], id_only=False
    ) -> t.Union[tuple[str, t.Union[str, TaipyImage]], str, None]:
        if (
            isinstance(value, tuple)
            and len(value) > 1
            and isinstance(value[0], str)
            and isinstance(value[1], (str, TaipyImage))
        ):
            if id_only:
                return value[0]
            elif len(value) > 2 and isinstance(value[2], list):
                return (value[0], TaipyImage.get_dict_or(value[1]), value[2])  # type: ignore
            else:
                return (value[0], TaipyImage.get_dict_or(value[1]))  # type: ignore
        else:
            id = self.__get_id(value, index)
            if id_only:
                return id
            else:
                label = self.__get_label(value)
                if label is None:
                    return None
                if len(value) > 2 and isinstance(value[2], list):
                    return (id, label, self.__get_children(value))  # type: ignore
                else:
                    return (id, label)  # type: ignore

    def __get_id(self, value: t.Any, index: t.Optional[str]) -> str:
        if hasattr(value, "id"):
            return str(value.id)
        elif hasattr(value, "__getitem__") and "id" in value:
            return str(value["id"])
        elif index is not None:
            return index
        else:
            return str(id(value))

    def __get_label(self, value: t.Any) -> t.Union[str, t.Dict, None]:
        if isinstance(value, (str, TaipyImage)):
            return TaipyImage.get_dict_or(value)
        elif hasattr(value, "label"):
            return TaipyImage.get_dict_or(value.label)
        elif hasattr(value, "__getitem__") and "label" in value:
            return TaipyImage.get_dict_or(value["label"])
        return None

    def __get_children(self, value: t.Any) -> t.List[t.Any]:
        if isinstance(value, list):
            return value
        elif hasattr(value, "children"):
            return value.children if isinstance(value.children, list) else [value.children]
        elif hasattr(value, "__getitem__") and "children" in value:
            return value["children"] if isinstance(value["children"], list) else [value["children"]]
        return []

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

    def _evaluate_expr(self, expr: str, re_evaluated: t.Optional[bool] = True) -> t.Any:
        return self._expression_evaluator.evaluate_expr(self, expr, re_evaluated)

    def _re_evaluate_expr(self, var_name: str) -> t.List[str]:
        return self._expression_evaluator.re_evaluate_expr(self, var_name)

    def _get_hash_from_expr(self, expr: str) -> str:
        return self._expression_evaluator.get_hash_from_expr(expr)

    def _get_expr_from_hash(self, hash: str) -> str:
        return self._expression_evaluator.get_expr_from_hash(hash)

    def _is_expression(self, expr: str) -> bool:
        return self._expression_evaluator._is_expression(expr)

    def _fetch_expression_list(self, expr: str) -> t.List:
        return self._expression_evaluator._fetch_expression_list(expr)

    def on_update(self, f) -> None:
        self._update_function = f

    def on_action(self, f) -> None:
        self._action_function = f

    def load_config(self, app_config: t.Optional[dict] = {}, style_config: t.Optional[dict] = {}) -> None:
        self._config.load_config(app_config=app_config, style_config=style_config)

    def _get_app_config(self, name: AppConfigOption, default_value: t.Any) -> t.Any:
        return self._config._get_app_config(name, default_value)

    def _get_themes(self) -> t.Optional[t.Dict[str, t.Any]]:
        theme = self._get_app_config("theme", None)
        dark_theme = self._get_app_config("theme[dark]", None)
        light_theme = self._get_app_config("theme[light]", None)
        res = {}
        if theme:
            res["base"] = theme
        if dark_theme:
            res["dark"] = dark_theme
        if light_theme:
            res["light"] = light_theme
        if theme or dark_theme or light_theme:
            return res
        return None

    def send_alert(
        self,
        type: str = "I",
        message: str = "",
        browser_notification: t.Optional[bool] = None,
        duration: t.Optional[int] = None,
    ):
        """Sends a notification alert to the UI.

        Arguments:
        type -- One of success, info, warning, error (or first letter of), empty string removes the alert (default: I)
        message -- text message to display (default: empty string)
        browser_notification -- Ask the browser to also show the notification (default: app_config[browser_notification])
        duration -- time during which the notification is shown in ms (default: app_config[notification_duration])
        """
        self._send_ws_alert(
            type,
            message,
            self._get_app_config("browser_notification", True)
            if browser_notification is None
            else browser_notification,
            self._get_app_config("notification_duration", 3000) if duration is None else duration,
        )

    def register_data_accessor(self, data_accessor_class: t.Type[DataAccessor]) -> None:
        self._data_accessors._register(data_accessor_class)

    def run(self, run_server=True, **kwargs) -> None:
        app_config = self._config.app_config
        # Load config from gui env file if available
        if not hasattr(self, "_root_dir"):
            self._root_dir = os.path.dirname(
                inspect.getabsfile(t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back))
            )
        env_file_abs_path = (
            self.__env_filename
            if os.path.isabs(self.__env_filename)
            else os.path.join(self._root_dir, self.__env_filename)
        )
        if os.path.isfile(env_file_abs_path):
            for key, value in dotenv_values(env_file_abs_path).items():
                key = key.lower()
                if value is not None and key in app_config:
                    try:
                        app_config[key] = value if app_config[key] is None else type(app_config[key])(value)  # type: ignore
                    except Exception as e:
                        warnings.warn(
                            f"Invalid env value in Gui.run {key} - {value}. Unable to parse value to the correct type.\n{e}"
                        )
        # Load keyword arguments
        for key, value in kwargs.items():
            key = key.lower()
            if value is not None and key in app_config:
                try:
                    app_config[key] = value if app_config[key] is None else type(app_config[key])(value)  # type: ignore
                except Exception as e:
                    warnings.warn(
                        f"Invalid keyword arguments value in Gui.run {key} - {value}. Unable to parse value to the correct type.\n{e}"
                    )
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
        for page in self._config.pages + self._config.partials:  # type: ignore
            # Server URL Rule for each page jsx
            self._server.add_url_rule(f"/flask-jsx/{page.route}/", view_func=self._render_page)

        # server URL Rule for flask rendered react-router
        self._server.add_url_rule("/initialize/", view_func=self._render_route)

        # Register Flask Blueprint if available
        for bp in self._flask_blueprint:
            self._server.register_blueprint(bp)

        # Register data accessor communicaiton data format (JSON, Apache Arrow)
        self._data_accessors._set_data_format(DataFormat.APACHE_ARROW if app_config["use_arrow"] else DataFormat.JSON)

        # Use multi user or not
        self._data_scopes.set_multi_user(app_config["multi_user"])

        self._server._set_client_url(app_config["client_url"])

        # Start Flask Server
        if run_server:
            self._server.runWithWS(host=app_config["host"], port=app_config["port"], debug=app_config["debug"])

    def get_flask_app(self):
        return self._server
