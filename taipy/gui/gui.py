from __future__ import annotations

import datetime
import inspect
import os
import pathlib
import random
import re
import typing as t
import warnings
from importlib import util
from operator import attrgetter
from types import FrameType, FunctionType

import __main__
import markdown as md_lib
from flask import Blueprint, Flask, request

if util.find_spec("pyngrok"):
    from pyngrok import ngrok

from ._default_config import app_config_default, style_config_default
from .config import AppConfigOption, GuiConfig
from .data.data_accessor import DataAccessor, _DataAccessors
from .data.data_format import DataFormat
from .data.data_scope import _DataScopes
from .page import Page, Partial
from .renderers import EmptyPageRenderer, PageRenderer
from .server import Server
from .taipyimage import TaipyImage
from .types import WsType
from .utils import (
    ISOToDate,
    Singleton,
    _get_dict_value,
    _is_in_notebook,
    _MapDictionary,
    attrsetter,
    dateToISO,
    get_client_var_name,
)
from .utils._adapter import _Adapter
from .utils._evaluator import _Evaluator


class Gui(object, metaclass=Singleton):
    """The class that handles the Graphical User Interface."""

    __root_page_name = "TaiPy_root_page"
    __env_filename = "taipy.gui.env"
    __UI_BLOCK_NAME = "TaipyUiBlockVar"
    __MESSAGE_GROUPING_NAME = "TaipyMessageGrouping"

    __RE_HTML = re.compile(r"(.*?)\.html")
    __RE_MD = re.compile(r"(.*?)\.md")
    __RE_PAGE_NAME = re.compile(r"^[\w\-\/]+$")

    __reserved_routes: t.List[str] = ["initialize", "flask-jsx"]
    _agregate_functions: t.List[str] = ["count", "sum", "mean", "median", "min", "max", "std", "first", "last"]

    # Static variable _markdown for Markdown renderer reference (taipy.gui will be registered later in Gui.run function)
    #
    # NOTE: Make sure, if you change this extension list, that the User Manual gets updated.
    # There's a section that explicitly lists these extensions in
    #      docs/gui/user_pages.md#markdown-specifics
    _markdown = md_lib.Markdown(
        extensions=["fenced_code", "meta", "admonition", "sane_lists", "tables", "attr_list", "md_in_html"]
    )

    def __init__(
        self,
        css_file: str = os.path.splitext(os.path.basename(__main__.__file__))[0]
        if hasattr(__main__, "__file__")
        else "Taipy",
        page: t.Optional[PageRenderer] = None,
        pages: t.Optional[dict] = None,
        path_mapping: t.Optional[dict] = {},
        env_filename: t.Optional[str] = None,
        flask: t.Optional[Flask] = None,
    ):
        """Initializes a new Gui instance.

        Args:
            css_file (string):  An optional pathname to a CSS file that gets used as a style sheet in
                all the pages.

                The default value is a file that has the same basename as the Python
                file defining the `main` function, sitting next to this Python file,
                with the `.css` extension.

            page (PageRenderer): An optional `PageRenderer` class that is used when there
                is a single page in this interface, referenced as the root page (in `/`).
                Note that if `pages` is provided, those pages are added as well.
        """
        self._server = Server(
            self, path_mapping=path_mapping, flask=flask, css_file=css_file, root_page_name=Gui.__root_page_name
        )
        # Preserve server config for re-initialization on notebook
        self._path_mapping = path_mapping
        self._flask = flask
        self._css_file = css_file

        self._config = GuiConfig()
        self._accessors = _DataAccessors()
        self._scopes = _DataScopes()

        self.__evaluator = _Evaluator()
        self.__adapter = _Adapter()
        self.on_update = None
        self.on_action = None
        self.__directory_name_of_pages: t.List[str] = []

        # Load default config
        self._flask_blueprint: t.List[Blueprint] = []
        self._config.load_config(app_config_default, style_config_default)

        if page:
            self.add_page(name=Gui.__root_page_name, renderer=page)
        if pages is not None:
            self.add_pages(pages)
        if env_filename is not None:
            self.__env_filename = env_filename

    @staticmethod
    def _get_instance() -> Gui:
        return Gui._instances[Gui]

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

    def _get_data_scope(self):
        return self._scopes.get_scope()

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
        prop = property(self.__value_getter(name), lambda s, v: s.__update_var(name, v))  # Getter, Setter
        setattr(Gui, name, prop)

    def _bind_global(self, name: str, value: t.Any) -> None:
        global_scope = self._scopes.get_global_scope()
        if hasattr(global_scope, name):
            return
        setattr(global_scope, name, value)

    def __value_getter(self, name):
        def __getter(elt: Gui) -> t.Any:
            value = getattr(elt._get_data_scope(), name)
            if isinstance(value, _MapDictionary):
                return _MapDictionary(value._dict, lambda s, v: elt.__update_var(name + "." + s, v))
            else:
                return value

        return __getter

    def _manage_message(self, msg_type: WsType, message: dict) -> None:
        try:
            self.__set_client_id(message)
            if msg_type == WsType.UPDATE.value:
                self.__front_end_update(
                    message["name"],
                    message["payload"],
                    message.get("propagate", True),
                )
            elif msg_type == WsType.ACTION.value:
                self.__on_action(_get_dict_value(message, "name"), message["payload"])
            elif msg_type == WsType.DATA_UPDATE.value:
                self.__request_data_update(message["name"], message["payload"])
            elif msg_type == WsType.REQUEST_UPDATE.value:
                self.__request_var_update(message["payload"])
            elif msg_type == WsType.CLIENT_ID.value:
                self.__get_or_create_scope(message["payload"])
        except TypeError as te:
            warnings.warn(f"Decoding Message has failed: {message}\n{te}")
        except KeyError as ke:
            warnings.warn(f"Can't access: {message}\n{ke}")

    def __set_client_id(self, message: dict):
        self._scopes._set_client_id(_get_dict_value(message, "client_id"))

    def __get_or_create_scope(self, id: str):
        if not id:
            id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}-{random.random()}"
            self.__send_ws_id(id)
        self._scopes.create_scope(id)

    def __front_end_update(self, var_name: str, value: t.Any, propagate=True) -> None:
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
            elif self._accessors._cast_string_value(var_name, currentvalue) is None:
                return
        self.__update_var(var_name, value, propagate, True)

    def __update_var(self, var_name: str, value: t.Any, propagate=True, from_front=False) -> None:
        hash_expr = self._get_hash_from_expr(var_name)
        modified_vars = [hash_expr]
        # Use custom attrsetter function to allow value binding for MapDictionary
        if propagate:
            attrsetter(self._get_data_scope(), hash_expr, value)
            # In case expression == hash (which is when there is only a single variable in expression)
            if var_name == hash_expr:
                modified_vars.extend(self._re_evaluate_expr(var_name))
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if self.on_update:
            self.on_update(self, var_name, value)
        self.__send_var_list_update(modified_vars, var_name if from_front else None)

    def __send_var_list_update(self, modified_vars: list, front_var: t.Optional[str] = None):
        ws_dict = {}
        for _var in modified_vars:
            newvalue = attrgetter(_var)(self._get_data_scope())
            self._scopes.broadcast_data(_var, newvalue)
            if isinstance(newvalue, datetime.datetime):
                newvalue = dateToISO(newvalue)
            if self._accessors._is_data_access(_var, newvalue):
                ws_dict[_var + ".refresh"] = True
            else:
                if _var != front_var:
                    if isinstance(newvalue, list):
                        newvalue = [self._run_adapter_for_var(_var, elt, str(idx)) for idx, elt in enumerate(newvalue)]
                    else:
                        newvalue = self._run_adapter_for_var(_var, newvalue, id_only=True)
                if isinstance(newvalue, _MapDictionary):
                    continue  # this var has no transformer
                ws_dict[_var] = newvalue
        # TODO: What if value == newvalue?
        self.__send_ws_update_with_dict(ws_dict)

    def __request_data_update(self, var_name: str, payload: t.Any) -> None:
        # Use custom attrgetter function to allow value binding for MapDictionary
        var_name = self._get_hash_from_expr(var_name)
        newvalue = attrgetter(var_name)(self._get_data_scope())
        ret_payload = self._accessors._get_data(self, var_name, newvalue, payload)
        self.__send_ws_update_with_dict({var_name: ret_payload, var_name + ".refresh": False})

    def __request_var_update(self, payload):
        if "names" in payload and isinstance(payload["names"], list):
            self.__send_var_list_update(payload["names"])

    def __send_ws(self, payload: dict) -> None:
        grouping_message = self.__get_message_grouping()
        if grouping_message is None:
            try:
                self._server._ws.emit(
                    "message",
                    payload,
                    to=self.__get_ws_receiver(),
                )
            except Exception as e:
                warnings.warn(
                    f"Web Socket communication error in {t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back).f_code.co_name}\n{e}"
                )
        else:
            grouping_message.append(payload)

    def __send_ws_id(self, id: str) -> None:
        self.__send_ws(
            {
                "type": WsType.CLIENT_ID.value,
                "id": id,
            }
        )

    def __send_ws_alert(self, type: str, message: str, browser_notification: bool, duration: int) -> None:
        self.__send_ws(
            {
                "type": WsType.ALERT.value,
                "atype": type,
                "message": message,
                "browser": browser_notification,
                "duration": duration,
            }
        )

    def __send_ws_block(
        self,
        action: t.Optional[str] = None,
        message: t.Optional[str] = None,
        close: t.Optional[bool] = False,
        cancel: t.Optional[bool] = False,
    ):
        self.__send_ws(
            {
                "type": WsType.BLOCK.value,
                "action": action,
                "close": close,
                "message": message,
                "noCancel": not cancel,
            }
        )

    def __send_ws_navigate(
        self,
        to: t.Optional[str] = None,
    ):
        self.__send_ws(
            {
                "type": WsType.NAVIGATE.value,
                "to": to,
            }
        )

    def __send_ws_update_with_dict(self, modified_values: dict) -> None:
        payload = [
            {"name": get_client_var_name(k), "payload": (v if isinstance(v, dict) and "value" in v else {"value": v})}
            for k, v in modified_values.items()
        ]
        self.__send_ws({"type": WsType.MULTIPLE_UPDATE.value, "payload": payload})

    def __get_ws_receiver(self) -> t.Union[str, None]:
        if not hasattr(request, "sid") or self._scopes.get_single_client():
            return None
        return request.sid  # type: ignore

    def __get_message_grouping(self):
        scope = self._get_data_scope()
        if scope is self._scopes.get_global_scope():
            return
        if not hasattr(scope, Gui.__MESSAGE_GROUPING_NAME):
            return None
        return getattr(scope, Gui.__MESSAGE_GROUPING_NAME)

    def __enter__(self):
        self.__hold_messages()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.__send_messages()
        except Exception as e:
            warnings.warn(f"An exception was raised while sending messages: {e}")
        if exc_value:
            warnings.warn(f"An {exc_type or 'Exception'} was raised: {exc_value}")
        return True

    def __hold_messages(self):
        grouping_message = self.__get_message_grouping()
        if grouping_message is None:
            self.bind_var_val(Gui.__MESSAGE_GROUPING_NAME, [])

    def __send_messages(self):
        grouping_message = self.__get_message_grouping()
        if grouping_message is not None:
            delattr(self._get_data_scope(), Gui.__MESSAGE_GROUPING_NAME)
            if len(grouping_message):
                self.__send_ws({"type": WsType.MULTIPLE_MESSAGE.value, "payload": grouping_message})

    def __on_action(self, id: t.Optional[str], payload: t.Any) -> None:
        if isinstance(payload, dict):
            action = _get_dict_value(payload, "action")
        else:
            action = str(payload)
        if action and hasattr(self, action):
            if self.__call_function_with_args(action_function=getattr(self, action), id=id, payload=payload):
                return
        if self.on_action:
            self.__call_function_with_args(action_function=self.on_action, id=id, payload=payload, action=action)

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

    # Proxy methods for Evaluator
    def _evaluate_expr(
        self, expr: str, re_evaluated: t.Optional[bool] = True, get_hash: t.Optional[bool] = False
    ) -> t.Any:
        return self.__evaluator.evaluate_expr(self, expr, re_evaluated, get_hash)

    def _re_evaluate_expr(self, var_name: str) -> t.List[str]:
        return self.__evaluator.re_evaluate_expr(self, var_name)

    def _get_hash_from_expr(self, expr: str) -> str:
        return self.__evaluator.get_hash_from_expr(expr)

    def _get_expr_from_hash(self, hash: str) -> str:
        return self.__evaluator.get_expr_from_hash(hash)

    def _is_expression(self, expr: str) -> bool:
        return self.__evaluator._is_expression(expr)

    def _fetch_expression_list(self, expr: str) -> t.List:
        return self.__evaluator._fetch_expression_list(expr)

    # Proxy methods for Adapter
    def _add_list_for_variable(self, var_name: str, list_name: str) -> None:
        self.__adapter._add_list_for_variable(var_name, list_name)

    def _add_adapter_for_type(self, type_name: str, adapter: FunctionType) -> None:
        self.__adapter._add_adapter_for_type(type_name, adapter)

    def _add_type_for_var(self, var_name: str, type_name: str) -> None:
        self.__adapter._add_type_for_var(var_name, type_name)

    def _get_adapter_for_type(self, type_name: str) -> t.Optional[FunctionType]:
        return self.__adapter._get_adapter_for_type(type_name)

    def _run_adapter_for_var(self, var_name: str, value: t.Any, index: t.Optional[str] = None, id_only=False) -> t.Any:
        return self.__adapter._run_adapter_for_var(var_name, value, index, id_only)

    def _run_adapter(
        self, adapter: FunctionType, value: t.Any, var_name: str, index: t.Optional[str], id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        return self.__adapter._run_adapter(adapter, value, var_name, index, id_only)

    def _get_valid_adapter_result(
        self, value: t.Any, index: t.Optional[str], id_only=False
    ) -> t.Union[tuple[str, t.Union[str, TaipyImage]], str, None]:
        return self.__adapter._get_valid_adapter_result(value, index, id_only)

    def _is_ui_blocked(self):
        return getattr(self._get_data_scope(), Gui.__UI_BLOCK_NAME, False)

    def __get_on_cancel_block_ui(self, callback: t.Optional[str]):
        def _taipy_on_cancel_block_ui(guiApp, id: t.Optional[str], payload: t.Any):
            if hasattr(guiApp._get_data_scope(), Gui.__UI_BLOCK_NAME):
                setattr(guiApp._get_data_scope(), Gui.__UI_BLOCK_NAME, False)
            self.__on_action(id, callback)

        return _taipy_on_cancel_block_ui

    # Public methods
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
            if folder_name in self.__directory_name_of_pages:
                raise Exception(f"Base directory name {folder_name} of path {folder_path} is not unique")
            if folder_name in Gui.__reserved_routes:
                raise Exception(f"Invalid directory. Directory {folder_name} is a reserved route")
            self.__directory_name_of_pages.append(folder_name)
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

    def load_config(self, app_config: t.Optional[dict] = {}, style_config: t.Optional[dict] = {}) -> None:
        self._config.load_config(app_config=app_config, style_config=style_config)

    def show_notification(
        self,
        type: str = "I",
        message: str = "",
        browser_notification: t.Optional[bool] = None,
        duration: t.Optional[int] = None,
    ):
        """Sends a notification to the user interface.

        Args:
            type (string): The notification type. This can be one of `"success"`, `"info"`, `"warning"` or `"error"`.
                To remove the last notification, set this parameter to the empty string.
            message (string): The text message to display.
            browser_notification (bool): If set to `True`, the browser will also show the notification.
                If not specified or set to `None`, this parameter will user the value of
                `app_config[browser_notification]`.
            duration: The time, in milliseconds, during which the notification is shown.
                If not specified or set to `None`, this parameter will user the value of
                `app_config[notification_duration]`.

        Note that you can also call this function with _type_ set to the first letter or the alert type
        (ie setting _type_ to `"i"` is equivalent to setting it to `"info"`).
        """
        self.__send_ws_alert(
            type,
            message,
            self._get_app_config("browser_notification", True)
            if browser_notification is None
            else browser_notification,
            self._get_app_config("notification_duration", 3000) if duration is None else duration,
        )

    def block_ui(
        self,
        callback: t.Optional[t.Union[str, FunctionType]] = None,
        message: t.Optional[str] = "Work in Progress...",
    ):
        """Blocks the UI

        Args:
            action (string | function): The action to be carried on cancel. If empty string or None, no Cancel action will be provided to the user.
            message (string): The message to show. Default: Work in Progress...
        """
        action_name = callback.__name__ if isinstance(callback, FunctionType) else callback
        if action_name:
            self.bind_func(action_name)
        func = self.__get_on_cancel_block_ui(action_name)
        def_action_name = func.__name__
        setattr(self, def_action_name, func)

        if hasattr(self._get_data_scope(), Gui.__UI_BLOCK_NAME):
            setattr(self._get_data_scope(), Gui.__UI_BLOCK_NAME, True)
        else:
            self._bind(Gui.__UI_BLOCK_NAME, True)
        self.__send_ws_block(action=def_action_name, message=message, cancel=bool(action_name))

    def unblock_ui(self):
        """Unblocks the UI"""
        if hasattr(self._get_data_scope(), Gui.__UI_BLOCK_NAME):
            setattr(self._get_data_scope(), Gui.__UI_BLOCK_NAME, False)
        self.__send_ws_block(close=True)

    def navigate(self, to: t.Optional[str] = ""):
        """Navigate to a page

        Args:
            to: page to navigate to. Should be a valid page identifier. If ommitted, navigates to the root page.
        """
        to = to or Gui.__root_page_name
        if to not in self._config.routes:
            warnings.warn(f"cannot navigate to '{to}' which is not a declared route.")
            return
        self.__send_ws_navigate(to)

    def register_data_accessor(self, data_accessor_class: t.Type[DataAccessor]) -> None:
        self._accessors._register(data_accessor_class)

    def get_flask_app(self):
        return self._server.get_flask()

    def run(self, run_server: bool = True, **kwargs) -> None:
        """
        Starts the server that delivers pages to Web clients.

        Once you enter `run`, users can run Web browsers and point to the Web server
        URL that `Gui` serves. The default is to listen to the _localhost_ address
        (127.0.0.1) on the port number 5000. However, the configuration of the `Gui`
        object may impact that (see TODO-Configuration-TODO).

        Args:
            run_server (bool): whether or not to run a Web server locally.
                If set to `False`, a Web server is _not_ created and started.
        """
        if _is_in_notebook():
            if hasattr(self._server, "_thread"):
                self._server._thread.kill()
                self._server._thread.join()
            self._flask_blueprint = []
            self._server = Server(
                self,
                path_mapping=self._path_mapping,
                flask=self._flask,
                css_file=self._css_file,
                root_page_name=Gui.__root_page_name,
            )
            self._scopes = _DataScopes()
            self.__evaluator = _Evaluator()

        app_config = self._config.app_config

        # Register _root_dir for abs path
        if not hasattr(self, "_root_dir"):
            self._root_dir = os.path.dirname(
                inspect.getabsfile(t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back))
            )

        # Load application config from multiple sources (env files, kwargs, command line)
        self._config.build_app_config(self._root_dir, self.__env_filename, kwargs)

        # Special config for notebook runtime
        if _is_in_notebook():
            self._config.app_config["single_client"] = True

        if run_server and app_config["ngrok_token"]:
            ngrok.set_auth_token(app_config["ngrok_token"])
            http_tunnel = ngrok.connect(app_config["port"], "http")
            app_config["client_url"] = http_tunnel.public_url
            app_config["use_reloader"] = False
            print(f" * NGROK Public Url: {http_tunnel.public_url}")

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

        pages_bp = Blueprint("taipy_pages", __name__)
        self._flask_blueprint.append(pages_bp)

        _absolute_path = str(pathlib.Path(__file__).parent.resolve())
        self._flask_blueprint.append(
            self._server._get_default_blueprint(
                static_folder=f"{_absolute_path}{os.path.sep}webapp",
                template_folder=f"{_absolute_path}{os.path.sep}webapp",
                client_url=app_config["client_url"],
                title=self._get_app_config("title", "Taipy App"),
                favicon=self._get_app_config("favicon", "/favicon.png"),
                themes=self._get_themes(),
            )
        )

        # Run parse markdown to force variables binding at runtime
        # (save rendered html to page.rendered_jsx for optimization)
        for page in self._config.pages + self._config.partials:  # type: ignore
            # Server URL Rule for each page jsx
            pages_bp.add_url_rule(f"/flask-jsx/{page.route}/", view_func=self._server._render_page)

        # server URL Rule for flask rendered react-router
        pages_bp.add_url_rule("/initialize/", view_func=self._server._render_route)

        # Register Flask Blueprint if available
        for bp in self._flask_blueprint:
            self._server.get_flask().register_blueprint(bp)

        # Register data accessor communicaiton data format (JSON, Apache Arrow)
        self._accessors._set_data_format(DataFormat.APACHE_ARROW if app_config["use_arrow"] else DataFormat.JSON)

        # Use multi user or not
        self._scopes.set_single_client(app_config["single_client"])

        # Start Flask Server
        if run_server:
            self._server.runWithWS(
                host=app_config["host"],
                port=app_config["port"],
                debug=app_config["debug"],
                use_reloader=app_config["use_reloader"],
            )

    def stop(self):
        if _is_in_notebook() and hasattr(self._server, "_thread"):
            self._server._thread.kill()
            self._server._thread.join()
            print("Gui server has been stopped")
