from __future__ import annotations

import inspect
import os
import pathlib
import re
import tempfile
import typing as t
import warnings
from importlib import util
from types import FrameType

import __main__
import markdown as md_lib
from flask import Blueprint, Flask, request, send_from_directory
from werkzeug.utils import secure_filename

if util.find_spec("pyngrok"):
    from pyngrok import ngrok

from ._default_config import app_config_default, style_config_default
from .config import AppConfigOption, GuiConfig
from .data.content_accessor import ContentAccessor
from .data.data_accessor import DataAccessor, _DataAccessors
from .data.data_format import DataFormat
from .page import Page, Partial
from .renderers import EmptyPageRenderer, PageRenderer
from .renderers._markdown import TaipyMarkdownExtension
from .server import Server
from .types import WsType
from .utils import (
    TaipyBase,
    TaipyContent,
    TaipyContentImage,
    TaipyData,
    TaipyLov,
    TaipyLovValue,
    _get_non_existent_file_path,
    _is_in_notebook,
    _MapDict,
    delscopeattr,
    get_client_var_name,
    getscopeattr,
    getscopeattr_drill,
    getuserattr,
    hasscopeattr,
    hasuserattr,
    setscopeattr,
    setscopeattr_drill,
)
from .utils._adapter import _Adapter
from .utils._bindings import _Bindings
from .utils._evaluator import _Evaluator
from .utils._state import State


class Gui:
    """The class that handles the Graphical User Interface.

    Attributes:

        on_action (Callable): The default function that is called when a control
            triggers an action, as the result of an interaction with the end-user.
        on_change (Callable): The function that is called when a control
            modifies the variable it is bound to, as the result of an interaction with the end-user.
    """

    __root_page_name = "TaiPy_root_page"
    __env_filename = "taipy.gui.env"
    __UI_BLOCK_NAME = "TaipyUiBlockVar"
    __MESSAGE_GROUPING_NAME = "TaipyMessageGrouping"
    __CONTENT_ROOT = "/taipy-content/"
    __UPLOAD_URL = "/taipy-uploads"

    __RE_HTML = re.compile(r"(.*?)\.html")
    __RE_MD = re.compile(r"(.*?)\.md")
    __RE_PAGE_NAME = re.compile(r"^[\w\-\/]+$")

    __reserved_routes: t.List[str] = ["taipy-init", "taipy-jsx", "taipy-content", "taipy-uploads"]
    _aggregate_functions: t.List[str] = ["count", "sum", "mean", "median", "min", "max", "std", "first", "last"]

    def __init__(
        self,
        css_file: str = os.path.splitext(os.path.basename(__main__.__file__))[0]
        if hasattr(__main__, "__file__")
        else "Taipy",
        page: t.Optional[t.Union[str, PageRenderer]] = None,
        pages: t.Optional[dict] = None,
        path_mapping: t.Optional[dict] = {},
        env_filename: t.Optional[str] = None,
        flask: t.Optional[Flask] = None,
    ):
        """Initializes a new Gui instance.

        Parameters:

            page (t.Union[str, PageRenderer], optional): An optional `PageRenderer` instance
                that is used when there is a single page in this interface, referenced as the
                root page (located at `/`).

                If `page` is a raw string, a `Markdown` page renderer is built from that string.

                Note that if `pages` is provided, those pages are added as well.

            css_file (string):  An optional pathname to a CSS file that gets used as a style sheet in
                all the pages.

                The default value is a file that has the same base name as the Python
                file defining the `main` function, sitting next to this Python file,
                with the `.css` extension.
        """
        self._server = Server(
            self, path_mapping=path_mapping, flask=flask, css_file=css_file, root_page_name=Gui.__root_page_name
        )
        # Preserve server config for re-initialization on notebook
        self._path_mapping = path_mapping
        self._flask = flask
        self._css_file = css_file

        self._config = GuiConfig()
        self.__content_accessor = None
        self._accessors = _DataAccessors()
        self.__state: State = None
        self.__bindings = _Bindings(self)
        self.__locals_bind: t.Dict[str, t.Any] = {}

        self.__evaluator: _Evaluator = None
        self.__adapter = _Adapter()
        self.__directory_name_of_pages: t.List[str] = []

        # Load default config
        self._flask_blueprint: t.List[Blueprint] = []
        self._config.load_config(app_config_default, style_config_default)

        # Load Markdown extension
        # NOTE: Make sure, if you change this extension list, that the User Manual gets updated.
        # There's a section that explicitly lists these extensions in
        #      docs/gui/user_pages.md#markdown-specifics
        self._markdown = md_lib.Markdown(
            extensions=[
                "fenced_code",
                "meta",
                "admonition",
                "sane_lists",
                "tables",
                "attr_list",
                "md_in_html",
                TaipyMarkdownExtension(gui=self),
            ]
        )

        if page:
            self.add_page(name=Gui.__root_page_name, renderer=page)
        if pages is not None:
            self.add_pages(pages)
        if env_filename is not None:
            self.__env_filename = env_filename

    def __get_content_accessor(self):
        if self.__content_accessor is None:
            self.__content_accessor = ContentAccessor(self._get_app_config("data_url_max_size", 50 * 1024))
        return self.__content_accessor

    def _bindings(self):
        return self.__bindings

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

    def _bind(self, name: str, value: t.Any) -> None:
        self._bindings()._bind(name, value)

    def _manage_message(self, msg_type: WsType, message: dict) -> None:
        try:
            self._bindings()._set_client_id(message)
            if msg_type == WsType.UPDATE.value:
                payload = message.get("payload", {})
                self.__front_end_update(
                    message.get("name"),
                    payload.get("value"),
                    message.get("propagate", True),
                    payload.get("relvar"),
                )
            elif msg_type == WsType.ACTION.value:
                self.__on_action(message.get("name"), message.get("payload"))
            elif msg_type == WsType.DATA_UPDATE.value:
                self.__request_data_update(message.get("name"), message.get("payload"))
            elif msg_type == WsType.REQUEST_UPDATE.value:
                self.__request_var_update(message.get("payload"))
            elif msg_type == WsType.CLIENT_ID.value:
                self._bindings()._get_or_create_scope(message.get("payload", ""))
        except Exception as e:
            warnings.warn(f"Decoding Message has failed: {message}\n{e}")

    def __front_end_update(self, var_name: str, value: t.Any, propagate=True, rel_var: t.Optional[str] = None) -> None:
        # Check if Variable is a managed type
        current_value = getscopeattr_drill(self, self._get_hash_from_expr(var_name))
        if isinstance(current_value, TaipyData):
            return
        elif rel_var and isinstance(current_value, TaipyLovValue):
            lov_holder = getscopeattr_drill(self, self._get_hash_from_expr(rel_var))
            if isinstance(lov_holder, TaipyLov):
                if isinstance(value, list):
                    val = value
                else:
                    val = [value]

                def mapping(v):
                    ret = v
                    for elt in lov_holder.get():
                        if v == self._run_adapter_for_var(lov_holder.get_name(), elt, id_only=True):
                            ret = elt
                            break
                    return ret

                ret_val = map(mapping, val)
                if isinstance(value, list):
                    value = TaipyLovValue(list(ret_val), current_value.get_name())
                else:
                    value = TaipyLovValue(next(ret_val), current_value.get_name())

        elif isinstance(current_value, TaipyBase):
            value = current_value.cast_value(value)
        self._update_var(var_name, value, propagate, current_value if isinstance(current_value, TaipyBase) else None)

    def _update_var(self, var_name: str, value: t.Any, propagate=True, holder: TaipyBase = None) -> None:
        if holder:
            var_name = holder.get_name()
        hash_expr = self._get_hash_from_expr(var_name)
        modified_vars = set([hash_expr])
        # Use custom attrsetter function to allow value binding for _MapDict
        if propagate:
            setscopeattr_drill(self, hash_expr, value)
            # In case expression == hash (which is when there is only a single variable in expression)
            if var_name == hash_expr:
                modified_vars.update(self._re_evaluate_expr(var_name))
        elif holder:
            modified_vars.update(self._evaluate_holders(hash_expr))
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if hasattr(self, "on_change") and callable(self.on_change):
            try:
                argcount = self.on_change.__code__.co_argcount
                args = [None for _ in range(argcount)]
                if argcount > 0:
                    args[0] = self.__state
                if argcount > 1:
                    args[1] = var_name
                if argcount > 2:
                    args[2] = (
                        value.get()
                        if isinstance(value, TaipyBase)
                        else value._dict
                        if isinstance(value, _MapDict)
                        else value
                    )
                self.on_change(*args)
            except Exception as e:
                warnings.warn(f"on_change: function invocation exception: {e}")
        self.__send_var_list_update(list(modified_vars), var_name)

    def _get_content(self, var_name: str, value: t.Any, image: bool) -> t.Any:
        ret_value = self.__get_content_accessor().get_info(var_name, value, image)
        if isinstance(ret_value, tuple):
            string_value = Gui.__CONTENT_ROOT + ret_value[0]
        else:
            string_value = ret_value
        return string_value

    def __serve_content(self, path: str) -> t.Any:
        parts = path.split("/")
        if len(parts) > 1:
            file_name = parts[-1]
            (dir_path, as_attachment) = self.__get_content_accessor().get_content_path(
                path[: -len(file_name) - 1], file_name, request.args.get("bypass")
            )
            if dir_path:
                return send_from_directory(str(dir_path), file_name, as_attachment=as_attachment)
        return ("", 404)

    def __upload_files(self):
        if "var_name" not in request.form:
            warnings.warn("No var name")
            return ("No var name", 400)
        var_name = request.form["var_name"]
        multiple = "multiple" in request.form and request.form["multiple"] == "True"
        if "blob" not in request.files:
            warnings.warn("No file part")
            return ("No file part", 400)
        file = request.files["blob"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            warnings.warn("No selected file")
            return ("No selected file", 400)
        suffix = ""
        complete = True
        part = 0
        if "total" in request.form:
            total = int(request.form["total"])
            if total > 1 and "part" in request.form:
                part = int(request.form["part"])
                suffix = f".part.{part}"
                complete = part == total - 1
        if file:  # and allowed_file(file.filename)
            upload_path = pathlib.Path(self._get_app_config("upload_folder", tempfile.gettempdir())).resolve()
            file_path = _get_non_existent_file_path(upload_path, secure_filename(file.filename))
            file.save(str(upload_path / (file_path.name + suffix)))
            if complete:
                if part > 0:
                    try:
                        with open(file_path, "wb") as grouped_file:
                            for nb in range(part + 1):
                                with open(upload_path / f"{file_path.name}.part.{nb}", "rb") as part_file:
                                    grouped_file.write(part_file.read())
                    except EnvironmentError as ee:
                        warnings.warn(f"cannot group file after chunk upload {ee}")
                        return
                # notify the file is uploaded
                newvalue = str(file_path)
                if multiple:
                    value = getscopeattr(self, var_name)
                    if not isinstance(value, t.List):
                        value = [] if value is None else [value]
                    value.append(newvalue)
                    newvalue = value
                setattr(self._bindings(), var_name, newvalue)
        return ("", 200)

    def __send_var_list_update(
        self,
        modified_vars: t.List[str],
        front_var: t.Optional[str] = None,
    ):
        ws_dict = {}
        values = {v: getscopeattr_drill(self, v) for v in modified_vars}
        for v in values.values():
            if isinstance(v, TaipyData) and v.get_name() in modified_vars:
                modified_vars.remove(v.get_name())
        for _var in modified_vars:
            newvalue = values.get(_var)
            # self._scopes.broadcast_data(_var, newvalue)
            if isinstance(newvalue, TaipyData):
                ws_dict[newvalue.get_name() + ".refresh"] = True
            else:
                if isinstance(newvalue, (TaipyContent, TaipyContentImage)):
                    ret_value = self.__get_content_accessor().get_info(
                        front_var, newvalue.get(), isinstance(newvalue, TaipyContentImage)
                    )
                    if isinstance(ret_value, tuple):
                        newvalue = Gui.__CONTENT_ROOT + ret_value[0]
                    else:
                        newvalue = ret_value
                elif isinstance(newvalue, TaipyLov):
                    newvalue = [
                        self._run_adapter_for_var(newvalue.get_name(), elt, str(idx))
                        for idx, elt in enumerate(newvalue.get())
                    ]
                elif isinstance(newvalue, TaipyLovValue):
                    newvalue = self._run_adapter_for_var(newvalue.get_name(), newvalue.get(), id_only=True)
                if isinstance(newvalue, (dict, _MapDict)):
                    continue  # this var has no transformer
                ws_dict[_var] = newvalue
        # TODO: What if value == newvalue?
        self.__send_ws_update_with_dict(ws_dict)

    def __request_data_update(self, var_name: str, payload: t.Any) -> None:
        # Use custom attrgetter function to allow value binding for _MapDict
        newvalue = getscopeattr_drill(self, var_name)
        if isinstance(newvalue, TaipyData):
            ret_payload = self._accessors._get_data(self, var_name, newvalue, payload)
            self.__send_ws_update_with_dict({var_name: ret_payload, newvalue.get_name() + ".refresh": False})

    def __request_var_update(self, payload: t.Any):
        if isinstance(payload, dict) and isinstance(payload.get("names"), list):
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

    def _send_ws_id(self, id: str) -> None:
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
        if not hasattr(request, "sid") or self._bindings()._get_single_client():
            return None
        return request.sid  # type: ignore

    def __get_message_grouping(self):
        if not hasscopeattr(self, Gui.__MESSAGE_GROUPING_NAME):
            return None
        return getscopeattr(self, Gui.__MESSAGE_GROUPING_NAME)

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
            delscopeattr(self, Gui.__MESSAGE_GROUPING_NAME)
            if len(grouping_message):
                self.__send_ws({"type": WsType.MULTIPLE_MESSAGE.value, "payload": grouping_message})

    def _get_user_function(self, func_name: str):
        func = getscopeattr(self, func_name, None)
        if not callable(func):
            func = self.__locals_bind.get(func_name)
        if callable(func):
            return func
        return func_name

    def __on_action(self, id: t.Optional[str], payload: t.Any) -> None:
        action = payload.get("action") if isinstance(payload, dict) else str(payload)
        if action:
            if self.__call_function_with_args(action_function=self._get_user_function(action), id=id, payload=payload, action=action):
                return
            else:
                warnings.warn(f"on_action: '{action}' is not a function")
        if hasattr(self, "on_action"):
            self.__call_function_with_args(action_function=self.on_action, id=id, payload=payload, action=action)

    def __call_function_with_args(self, **kwargs):
        action_function = kwargs.get("action_function")
        id = kwargs.get("id")
        action = kwargs.get("action")
        payload = kwargs.get("payload")

        if callable(action_function):
            try:
                argcount = action_function.__code__.co_argcount
                args = [None for _ in range(argcount)]
                if argcount > 0:
                    args[0] = self.__state
                if argcount > 1:
                    args[1] = id
                if argcount > 2:
                    args[2] = payload if action is None else action
                if argcount > 3 and action is not None:
                    args[3] = payload
                action_function(*args)
                return True
            except Exception as e:
                warnings.warn(f"on_action: '{action_function.__name__}' function invocation exception: {e}")

        return False

    # Proxy methods for Evaluator
    def _evaluate_expr(self, expr: str, bind=False) -> t.Any:
        return self.__evaluator.evaluate_expr(self, expr, bind)

    def _re_evaluate_expr(self, var_name: str) -> t.Set[str]:
        return self.__evaluator.re_evaluate_expr(self, var_name)

    def _get_hash_from_expr(self, expr: str) -> str:
        return self.__evaluator.get_hash_from_expr(expr)

    def _get_expr_from_hash(self, hash: str) -> str:
        return self.__evaluator.get_expr_from_hash(hash)

    def _evaluate_bind_holder(self, holder: t.Type[TaipyBase], expr: str) -> str:
        return self.__evaluator.evaluate_bind_holder(self, holder, expr)

    def _evaluate_holders(self, expr: str) -> t.List[str]:
        return self.__evaluator.evaluate_holders(self, expr)

    def _is_expression(self, expr: str) -> bool:
        return self.__evaluator._is_expression(expr)

    def _fetch_expression_list(self, expr: str) -> t.List:
        return self.__evaluator._fetch_expression_list(expr)

    # Proxy methods for Adapter
    def _add_list_for_variable(self, var_name: str, list_name: str) -> None:
        self.__adapter._add_list_for_variable(var_name, list_name)

    def _add_adapter_for_type(self, type_name: str, adapter: t.Callable) -> None:
        self.__adapter._add_adapter_for_type(type_name, adapter)

    def _add_type_for_var(self, var_name: str, type_name: str) -> None:
        self.__adapter._add_type_for_var(var_name, type_name)

    def _get_adapter_for_type(self, type_name: str) -> t.Optional[t.Callable]:
        return self.__adapter._get_adapter_for_type(type_name)

    def _run_adapter_for_var(self, var_name: str, value: t.Any, index: t.Optional[str] = None, id_only=False) -> t.Any:
        return self.__adapter._run_adapter_for_var(var_name, value, index, id_only)

    def _run_adapter(
        self, adapter: t.Callable, value: t.Any, var_name: str, index: t.Optional[str], id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        return self.__adapter._run_adapter(adapter, value, var_name, index, id_only)

    def _get_valid_adapter_result(
        self, value: t.Any, index: t.Optional[str], id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        return self.__adapter._get_valid_adapter_result(value, index, id_only)

    def _is_ui_blocked(self):
        return getscopeattr(self, Gui.__UI_BLOCK_NAME, False)

    def __get_on_cancel_block_ui(self, callback: t.Optional[str]):
        def _taipy_on_cancel_block_ui(guiApp, id: t.Optional[str], payload: t.Any):
            if hasscopeattr(self, Gui.__UI_BLOCK_NAME):
                setscopeattr(self, Gui.__UI_BLOCK_NAME, False)
            self.__on_action(id, callback)

        return _taipy_on_cancel_block_ui

    # Public methods
    def add_page(
        self,
        name: str,
        renderer: t.Union[str, PageRenderer],
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
        if isinstance(renderer, str):
            from .renderers import Markdown

            renderer = Markdown(renderer)
        elif not isinstance(renderer, PageRenderer):
            raise Exception(f'Page name "{name if name != Gui.__root_page_name else "/"}" has invalid PageRenderer')
        # Init a new page
        new_page = Page()
        new_page.route = name
        new_page.renderer = renderer
        new_page.style = style
        # Append page to _config
        self._config.pages.append(new_page)
        self._config.routes.append(name)

    def add_pages(self, pages: t.Union[dict[str, t.Union[str, PageRenderer]], str] = None) -> None:
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
        renderer: t.Union[str, PageRenderer],
    ) -> Partial:
        # Init a new partial
        new_partial = Partial()
        # Validate name
        if new_partial.route in self._config.partial_routes or new_partial.route in self._config.routes:
            warnings.warn(f'Partial name "{new_partial.route}" is already defined')
        if isinstance(renderer, str):
            from .renderers import Markdown

            renderer = Markdown(renderer)
        elif not isinstance(renderer, PageRenderer):
            raise Exception(f'Partial name "{new_partial.route}" has invalid PageRenderer')
        new_partial.renderer = renderer
        # Append partial to _config
        self._config.partials.append(new_partial)
        self._config.partial_routes.append(str(new_partial.route))
        return new_partial

    # Main binding method (bind in markdown declaration)
    def bind_var(self, var_name: str) -> bool:
        if not hasattr(self._bindings(), var_name) and var_name in self.__locals_bind.keys():
            self._bind(var_name, self.__locals_bind[var_name])
            return True
        return False

    def bind_var_val(self, var_name: str, value: t.Any) -> bool:
        if not hasattr(self._bindings(), var_name):
            self._bind(var_name, value)
            return True
        return False

    def __bind_local_func(self, name: str):
        func = getattr(self, name, None)
        if func is not None and not callable(func):
            warnings.warn(
                f"{self.__class__.__name__}.{name}: {func} should be a function; looking for {name} in the script."
            )
            func = None
        if func is None:
            func = self.__locals_bind.get(name)
        if func is not None:
            if callable(func):
                setattr(self, name, func)
            else:
                warnings.warn(f"{name}: {func} should be a function")

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
        callback: t.Optional[t.Union[str, t.Callable]] = None,
        message: t.Optional[str] = "Work in Progress...",
    ):
        """Blocks the UI

        Args:
            action (string | function): The action to be carried on cancel. If empty string or None, no Cancel action will be provided to the user.
            message (string): The message to show. Default: Work in Progress...
        """
        action_name = callback.__name__ if callable(callback) else callback
        func = self.__get_on_cancel_block_ui(action_name)
        def_action_name = func.__name__
        setscopeattr(self, def_action_name, func)

        if hasscopeattr(self, Gui.__UI_BLOCK_NAME):
            setscopeattr(self, Gui.__UI_BLOCK_NAME, True)
        else:
            self._bind(Gui.__UI_BLOCK_NAME, True)
        self.__send_ws_block(action=def_action_name, message=message, cancel=bool(action_name))

    def unblock_ui(self):
        """Unblocks the UI"""
        if hasscopeattr(self, Gui.__UI_BLOCK_NAME):
            setscopeattr(self, Gui.__UI_BLOCK_NAME, False)
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
            self._bindings()._new_scopes()

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

        # Save all local variables of the parent frame (usually __main__)
        self.__locals_bind: t.Dict[str, t.Any] = t.cast(
            FrameType, t.cast(FrameType, inspect.currentframe()).f_back
        ).f_locals

        self.__state = State(self, self.__locals_bind.keys())

        # base global ctx is TaipyHolder classes + script modules and callables
        glob_ctx = {t.__name__: t for t in TaipyBase.__subclasses__()}
        glob_ctx.update({k: v for k, v in self.__locals_bind.items() if inspect.ismodule(v) or callable(v)})
        self.__evaluator: _Evaluator = _Evaluator(glob_ctx)

        # bind on_change and on_action function if available
        self.__bind_local_func("on_change")
        self.__bind_local_func("on_action")

        # add en empty main page if it is not defined
        if Gui.__root_page_name not in self._config.routes:
            new_page = Page()
            new_page.route = Gui.__root_page_name
            new_page.renderer = EmptyPageRenderer()
            self._config.pages.append(new_page)
            self._config.routes.append(Gui.__root_page_name)

        pages_bp = Blueprint("taipy_pages", __name__)
        self._flask_blueprint.append(pages_bp)

        # server URL Rule for taipy images
        images_bp = Blueprint("taipy_images", __name__)
        images_bp.add_url_rule(f"{Gui.__CONTENT_ROOT}<path:path>", view_func=self.__serve_content)

        self._flask_blueprint.append(images_bp)

        # server URL for uploaded files
        upload_bp = Blueprint("taipy_upload", __name__)
        upload_bp.add_url_rule(Gui.__UPLOAD_URL, view_func=self.__upload_files, methods=["POST"])
        self._flask_blueprint.append(upload_bp)

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
            pages_bp.add_url_rule(f"/taipy-jsx/{page.route}/", view_func=self._server._render_page)

        # server URL Rule for flask rendered react-router
        pages_bp.add_url_rule("/taipy-init/", view_func=self._server._render_route)

        # Register Flask Blueprint if available
        for bp in self._flask_blueprint:
            self._server.get_flask().register_blueprint(bp)

        # Register data accessor communicaiton data format (JSON, Apache Arrow)
        self._accessors._set_data_format(DataFormat.APACHE_ARROW if app_config["use_arrow"] else DataFormat.JSON)

        # Use multi user or not
        self._bindings()._set_single_client(bool(app_config["single_client"]))

        # Start Flask Server
        if run_server:
            self._server.runWithWS(
                host=app_config["host"],
                port=app_config["port"],
                debug=app_config["debug"],
                use_reloader=app_config["use_reloader"],
                flask_log=app_config["flask_log"],
            )

    def stop(self):
        if _is_in_notebook() and hasattr(self._server, "_thread"):
            self._server._thread.kill()
            self._server._thread.join()
            print("Gui server has been stopped")
