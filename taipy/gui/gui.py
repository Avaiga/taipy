from __future__ import annotations

import inspect
import json
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

from ._default_config import default_config
from ._page import _Page
from .config import Config, ConfigParameter, _Config
from .data.content_accessor import _ContentAccessor
from .data.data_accessor import _DataAccessor, _DataAccessors
from .data.data_format import _DataFormat
from .page import Page
from .partial import Partial
from .renderers import _EmptyPage
from .renderers._markdown import _TaipyMarkdownExtension
from .renderers.jsonencoder import _TaipyJsonEncoder
from .server import _Server
from .state import State
from .types import _WsType
from .utils import (
    _delscopeattr,
    _get_client_var_name,
    _get_non_existent_file_path,
    _getscopeattr,
    _getscopeattr_drill,
    _hasscopeattr,
    _is_in_notebook,
    _MapDict,
    _setscopeattr,
    _setscopeattr_drill,
    _TaipyBase,
    _TaipyContent,
    _TaipyContentImage,
    _TaipyData,
    _TaipyLov,
    _TaipyLovValue,
)
from .utils._adapter import _Adapter
from .utils._bindings import _Bindings
from .utils._evaluator import _Evaluator


class Gui:
    """Entry point for the Graphical User Interface generation.

    Attributes:

        on_action (Callable): The function that is called when a control
            triggers an action, as the result of an interaction with the end-user.<br/>
            It defaults to the _on_action_ global function defined in the Python
            application. If there is no such function, actions will not trigger anything.
        on_change (Callable): The function that is called when a control
            modifies variables it is bound to, as the result of an interaction with the
            end-user.<br/>
            It defaults to the _on_change_ global function defined in the Python
            application. If there is no such function, user interactions will not trigger
            anything.
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
        page: t.Optional[t.Union[str, Page]] = None,
        pages: t.Optional[dict] = None,
        css_file: str = os.path.splitext(os.path.basename(__main__.__file__))[0]
        if hasattr(__main__, "__file__")
        else "Taipy",
        path_mapping: t.Optional[dict] = {},
        env_filename: t.Optional[str] = None,
        flask: t.Optional[Flask] = None,
    ):
        """Initialize a new Gui instance.

        Arguments:
            page: An optional `Page^` instance that is used when there is a single page
                in this interface, referenced as the _root_ page (located at `/`).<br/>
                If _page_ is a raw string and if it holds a path to a readable file then
                a `Markdown^` page is built from the content of that file.<br/>
                If _page_ is a string that does not indicate a path to readable file then
                a `Markdown^` page is built from that string.<br/>
                Note that if _pages_ is provided, those pages are added as well.
            pages: Used if you want to initialize this instance with a set of pages.
                The method `(Gui.)add_pages()^` is called if _pages_ is not None, and
                you can find details on the possible values of this argument in the
                documentation for this method.
            css_file:  An optional pathname to a CSS file that gets used as a style sheet in
                all the pages.<br/>
                The default value is a file that has the same base name as the Python
                file defining the `main` function, sitting next to this Python file,
                with the `.css` extension.
            path_mapping: TODO explain what this does.
            env_filename: An optional file from which to load application configuration
                variables (see the [Configuration](../gui/configuration.md#configuring-the-gui-instance)
                section for details.)</br>
                The default value is "taipy.gui.env"
            flask: TODO explain what this does.
        """
        self._server = _Server(
            self, path_mapping=path_mapping, flask=flask, css_file=css_file, root_page_name=Gui.__root_page_name
        )
        # Preserve server config for re-initialization on notebook
        self._path_mapping = path_mapping
        self._flask = flask
        self._css_file = css_file

        self._config = _Config()
        self.__content_accessor = None
        self._accessors = _DataAccessors()
        self.__state: t.Optional[State] = None
        self.__bindings = _Bindings(self)
        self.__locals_bind: t.Dict[str, t.Any] = {}

        self.__evaluator: _Evaluator = None  # type: ignore
        self.__adapter = _Adapter()
        self.__directory_name_of_pages: t.List[str] = []

        # default actions
        self.on_change: t.Optional[t.Callable] = None
        self.on_action: t.Optional[t.Callable] = None

        # Load default config
        self._flask_blueprint: t.List[Blueprint] = []
        self._config._load(default_config)

        # Load Markdown extension
        # NOTE: Make sure, if you change this extension list, that the User Manual gets updated.
        # There's a section that explicitly lists these extensions in
        #      docs/gui/pages.md#markdown-specifics
        self._markdown = md_lib.Markdown(
            extensions=[
                "fenced_code",
                "meta",
                "admonition",
                "sane_lists",
                "tables",
                "attr_list",
                "md_in_html",
                _TaipyMarkdownExtension(gui=self),
            ]
        )

        if page:
            self.add_page(name=Gui.__root_page_name, page=page)
        if pages is not None:
            self.add_pages(pages)
        if env_filename is not None:
            self.__env_filename = env_filename

    def __get_content_accessor(self):
        if self.__content_accessor is None:
            self.__content_accessor = _ContentAccessor(self._get_config("data_url_max_size", 50 * 1024))
        return self.__content_accessor

    def _bindings(self):
        return self.__bindings

    def _get_config(self, name: ConfigParameter, default_value: t.Any) -> t.Any:
        return self._config._get_config(name, default_value)

    def _get_themes(self) -> t.Optional[t.Dict[str, t.Any]]:
        theme = self._get_config("theme", None)
        dark_theme = self._get_config("theme[dark]", None)
        light_theme = self._get_config("theme[light]", None)
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

    def _manage_message(self, msg_type: _WsType, message: dict) -> None:
        try:
            self._bindings()._set_client_id(message)
            if msg_type == _WsType.UPDATE.value:
                payload = message.get("payload", {})
                self.__front_end_update(
                    str(message.get("name")),
                    payload.get("value"),
                    message.get("propagate", True),
                    payload.get("relvar"),
                )
            elif msg_type == _WsType.ACTION.value:
                self.__on_action(message.get("name"), message.get("payload"))
            elif msg_type == _WsType.DATA_UPDATE.value:
                self.__request_data_update(str(message.get("name")), message.get("payload"))
            elif msg_type == _WsType.REQUEST_UPDATE.value:
                self.__request_var_update(message.get("payload"))
            elif msg_type == _WsType.CLIENT_ID.value:
                self._bindings()._get_or_create_scope(message.get("payload", ""))
        except Exception as e:
            warnings.warn(f"Decoding Message has failed: {message}\n{e}")

    def __front_end_update(self, var_name: str, value: t.Any, propagate=True, rel_var: t.Optional[str] = None) -> None:
        # Check if Variable is a managed type
        current_value = _getscopeattr_drill(self, self.__evaluator.get_hash_from_expr(var_name))
        if isinstance(current_value, _TaipyData):
            return
        elif rel_var and isinstance(current_value, _TaipyLovValue):  # pragma: no cover
            lov_holder = _getscopeattr_drill(self, self.__evaluator.get_hash_from_expr(rel_var))
            if isinstance(lov_holder, _TaipyLov):
                if isinstance(value, list):
                    val = value
                else:
                    val = [value]
                elt_4_ids = self.__adapter._get_elt_per_ids(lov_holder.get_name(), lov_holder.get())
                ret_val = [elt_4_ids.get(x, x) for x in val]
                if not isinstance(value, list):
                    if ret_val:
                        value = ret_val[0]
                else:
                    value = ret_val

        elif isinstance(current_value, _TaipyBase):
            value = current_value.cast_value(value)
        self._update_var(var_name, value, propagate, current_value if isinstance(current_value, _TaipyBase) else None)

    def _update_var(self, var_name: str, value: t.Any, propagate=True, holder: _TaipyBase = None) -> None:
        if holder:
            var_name = holder.get_name()
        hash_expr = self.__evaluator.get_hash_from_expr(var_name)
        modified_vars = set([hash_expr])
        # Use custom attrsetter function to allow value binding for _MapDict
        if propagate:
            _setscopeattr_drill(self, hash_expr, value)
            # In case expression == hash (which is when there is only a single variable in expression)
            if var_name == hash_expr:
                modified_vars.update(self._re_evaluate_expr(var_name))
        elif holder:
            modified_vars.update(self._evaluate_holders(hash_expr))
        # TODO: what if _update_function changes 'var_name'... infinite loop?
        if hasattr(self, "on_change") and callable(self.on_change):
            try:
                argcount = self.on_change.__code__.co_argcount
                args: t.List[t.Any] = [None for _ in range(argcount)]
                if argcount > 0:
                    args[0] = self.__state
                if argcount > 1:
                    args[1] = var_name
                if argcount > 2:
                    args[2] = (
                        value.get()
                        if isinstance(value, _TaipyBase)
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
            upload_path = pathlib.Path(self._get_config("upload_folder", tempfile.gettempdir())).resolve()
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
                    value = _getscopeattr(self, var_name)
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
        values = {v: _getscopeattr_drill(self, v) for v in modified_vars}
        for v in values.values():
            if isinstance(v, _TaipyData) and v.get_name() in modified_vars:
                modified_vars.remove(v.get_name())
        for _var in modified_vars:
            newvalue = values.get(_var)
            # self._scopes.broadcast_data(_var, newvalue)
            if isinstance(newvalue, _TaipyData):
                ws_dict[newvalue.get_name() + ".refresh"] = True
            else:
                if isinstance(newvalue, (_TaipyContent, _TaipyContentImage)):
                    ret_value = self.__get_content_accessor().get_info(
                        front_var, newvalue.get(), isinstance(newvalue, _TaipyContentImage)
                    )
                    if isinstance(ret_value, tuple):
                        newvalue = Gui.__CONTENT_ROOT + ret_value[0]
                    else:
                        newvalue = ret_value
                elif isinstance(newvalue, _TaipyLov):
                    newvalue = [self.__adapter._run_for_var(newvalue.get_name(), elt) for elt in newvalue.get()]
                elif isinstance(newvalue, _TaipyLovValue):
                    if isinstance(newvalue.get(), list):
                        newvalue = [
                            self.__adapter._run_for_var(newvalue.get_name(), elt, id_only=True)
                            for elt in newvalue.get()
                        ]
                    else:
                        newvalue = self.__adapter._run_for_var(newvalue.get_name(), newvalue.get(), id_only=True)
                if isinstance(newvalue, (dict, _MapDict)):
                    continue  # this var has no transformer
                with warnings.catch_warnings(record=True) as w:
                    warnings.resetwarnings()
                    json.dumps(newvalue, cls=_TaipyJsonEncoder)
                    if len(w):
                        # do not send data that is not serializable
                        continue
                ws_dict[_var] = newvalue
        # TODO: What if value == newvalue?
        self.__send_ws_update_with_dict(ws_dict)

    def __request_data_update(self, var_name: str, payload: t.Any) -> None:
        # Use custom attrgetter function to allow value binding for _MapDict
        newvalue = _getscopeattr_drill(self, var_name)
        if isinstance(newvalue, _TaipyData):
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
                "type": _WsType.CLIENT_ID.value,
                "id": id,
            }
        )

    def _send_ws_download(self, content: str, name: str, on_action: str) -> None:
        self.__send_ws({"type": _WsType.DOWNLOAD_FILE.value, "content": content, "name": name, "on_action": on_action})

    def __send_ws_alert(self, type: str, message: str, browser_notification: bool, duration: int) -> None:
        self.__send_ws(
            {
                "type": _WsType.ALERT.value,
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
                "type": _WsType.BLOCK.value,
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
                "type": _WsType.NAVIGATE.value,
                "to": to,
            }
        )

    def __send_ws_update_with_dict(self, modified_values: dict) -> None:
        payload = [
            {"name": _get_client_var_name(k), "payload": (v if isinstance(v, dict) and "value" in v else {"value": v})}
            for k, v in modified_values.items()
        ]
        self.__send_ws({"type": _WsType.MULTIPLE_UPDATE.value, "payload": payload})

    def __get_ws_receiver(self) -> t.Union[str, None]:
        if not hasattr(request, "sid") or self._bindings()._get_single_client():
            return None
        return request.sid  # type: ignore

    def __get_message_grouping(self):
        if not _hasscopeattr(self, Gui.__MESSAGE_GROUPING_NAME):
            return None
        return _getscopeattr(self, Gui.__MESSAGE_GROUPING_NAME)

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
            self._bind_var_val(Gui.__MESSAGE_GROUPING_NAME, [])

    def __send_messages(self):
        grouping_message = self.__get_message_grouping()
        if grouping_message is not None:
            _delscopeattr(self, Gui.__MESSAGE_GROUPING_NAME)
            if len(grouping_message):
                self.__send_ws({"type": _WsType.MULTIPLE_MESSAGE.value, "payload": grouping_message})

    def _get_user_function(self, func_name: str):
        func = _getscopeattr(self, func_name, None)
        if not callable(func):
            func = self.__locals_bind.get(func_name)
        if callable(func):
            return func
        return func_name

    def __on_action(self, id: t.Optional[str], payload: t.Any) -> None:
        action = payload.get("action") if isinstance(payload, dict) else str(payload)
        if action:
            if self.__call_function_with_args(
                action_function=self._get_user_function(action), id=id, payload=payload, action=action
            ):
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
    def _evaluate_expr(self, expr: str) -> t.Any:
        return self.__evaluator.evaluate_expr(self, expr)

    def _re_evaluate_expr(self, var_name: str) -> t.Set[str]:
        return self.__evaluator.re_evaluate_expr(self, var_name)

    def _get_expr_from_hash(self, hash: str) -> str:
        return self.__evaluator.get_expr_from_hash(hash)

    def _evaluate_bind_holder(self, holder: t.Type[_TaipyBase], expr: str) -> str:
        return self.__evaluator.evaluate_bind_holder(self, holder, expr)

    def _evaluate_holders(self, expr: str) -> t.List[str]:
        return self.__evaluator.evaluate_holders(self, expr)

    def _is_expression(self, expr: str) -> bool:
        return self.__evaluator._is_expression(expr)

    # Proxy methods for Adapter
    def _add_adapter_for_type(self, type_name: str, adapter: t.Callable) -> None:
        self.__adapter._add_for_type(type_name, adapter)

    def _add_type_for_var(self, var_name: str, type_name: str) -> None:
        self.__adapter._add_type_for_var(var_name, type_name)

    def _get_adapter_for_type(self, type_name: str) -> t.Optional[t.Callable]:
        return self.__adapter._get_for_type(type_name)

    def _run_adapter(
        self, adapter: t.Optional[t.Callable], value: t.Any, var_name: str, id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        return self.__adapter._run(adapter, value, var_name, id_only)

    def _get_valid_adapter_result(self, value: t.Any, id_only=False) -> t.Union[t.Tuple[str, ...], str, None]:
        return self.__adapter._get_valid_result(value, id_only)

    def _is_ui_blocked(self):
        return _getscopeattr(self, Gui.__UI_BLOCK_NAME, False)

    def __get_on_cancel_block_ui(self, callback: t.Optional[str]):
        def _taipy_on_cancel_block_ui(guiApp, id: t.Optional[str], payload: t.Any):
            if _hasscopeattr(self, Gui.__UI_BLOCK_NAME):
                _setscopeattr(self, Gui.__UI_BLOCK_NAME, False)
            self.__on_action(id, callback)

        return _taipy_on_cancel_block_ui

    def __add_pages_in_folder(self, folder_name: str, folder_path: str):
        list_of_files = os.listdir(folder_path)
        for file_name in list_of_files:
            from .renderers import Html, Markdown

            if re_match := Gui.__RE_HTML.match(file_name):
                renderers = Html(os.path.join(folder_path, file_name))
                renderers.modify_taipy_base_url(folder_name)
                self.add_page(name=f"{folder_name}/{re_match.group(1)}", page=renderers)
            elif re_match := Gui.__RE_MD.match(file_name):
                renderers_md = Markdown(os.path.join(folder_path, file_name))
                self.add_page(name=f"{folder_name}/{re_match.group(1)}", page=renderers_md)
            elif os.path.isdir(child_dir_path := os.path.join(folder_path, file_name)):
                child_dir_name = f"{folder_name}/{file_name}"
                self.__add_pages_in_folder(child_dir_name, child_dir_path)

    def _get_locals_bind(self):
        return self.__locals_bind

    def _get_root_page_name(self):
        return self.__root_page_name

    # Public methods
    def add_page(
        self,
        name: str,
        page: t.Union[str, Page],
        style: t.Optional[str] = "",
    ) -> None:
        """Add a page to the graphical User Interface.

        Arguments:
            name: The name of the page.
            page (Union[str, Page]): The content of the page.<br/>
                It can be an instance of `Markdown^` or `Html^`.<br/>
                If _page_ is a string, then:

                - If _page_ is set to the pathname of a readable file, the page
                  content is read as Markdown input text.
                - If it is not, the page content is read from this string as
                  Markdown text.
            style (Optional[str]): Additional CSS style to apply to this page.

        Note that page names cannot start with the slash ('/') character and that each
        page must have a unique name.
        """
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
        if isinstance(page, str):
            from .renderers import Markdown

            page = Markdown(page)
        elif not isinstance(page, Page):
            raise Exception(f'"page" is invalid for page name "{name if name != Gui.__root_page_name else "/"}')
        # Init a new page
        new_page = _Page()
        new_page._route = name
        new_page._renderer = page
        new_page._style = style
        # Append page to _config
        self._config.pages.append(new_page)
        self._config.routes.append(name)

    def add_pages(self, pages: t.Union[dict[str, t.Union[str, Page]], str] = None) -> None:
        """Add several pages to the graphical User Interface.

        Arguments:
            pages (Union[dict[str, Union[str, Page]], str]): The pages to add.<br/>
                If _pages_ is a dictionnary, a page is added to this `Gui` instance:

                - The entry key is used as the page name.
                - The entry value is used as the page content:
                    - The value can can be an instance of `Markdown^` or `Html^`, then
                      it is used as the page definition.
                    - If entry value is a string, then:
                        - If it is set to the pathname of a readable file, the page
                          content is read as Markdown input text.
                        - If it is not, the page content is read from this string as
                          Markdown text.

                If _pages_ is a string that contains the path to a directory, then
                this directory is read to create pages. See below for details.

        !!! note "Reading pages from a directory"
            If _pages_ is a string that holds the path to a readable directory, then
            this directory is traversed, recursively, to find files that Taipy can build
            pages from.

            For every new directory that is traversed, a new hierarchical level
            for pages is created.

            For every file that is found:

                - If the filename extention is _.md_, it is read as Markdown content and
                  a new page is created with the base name of this filename.
                - If the filename extention is _.html_, it is read as HTML content and
                  a new page is created with the base name of this filename.

            For example, say you have the following directory structure:
            ```
            reports
            ├── home.html
            ├── budget/
            │   ├── expenses/
            │   │   ├── marketing.md
            │   │   └── production.md
            │   └── revenue/
            │       ├── EMAE.md
            │       ├── USA.md
            │       └── ASIA.md
            └── cashflow/
                ├── weekly.md
                ├── monthly.md
                └── yearly.md
            ```

            Calling `gui.add_pages('reports')` is equivalent to calling:
            ```py
            gui.add_pages({
                            "reports/home", Html("reports/home.html"),
                            "reports/budget/expenses/marketing", Markdown("reports/budget/expenses/marketing.md"),
                            "reports/budget/expenses/production", Markdown("reports/budget/expenses/production.md"),
                            "reports/budget/revenue/EMAE", Markdown("reports/budget/revenue/EMAE.md"),
                            "reports/budget/revenue/USA", Markdown("reports/budget/revenue/USA.md"),
                            "reports/budget/revenue/ASIA", Markdown("reports/budget/revenue/ASIA.md"),
                            "reports/cashflow/weekly", Markdown("reports/cashflow/weekly.md"),
                            "reports/cashflow/monthly", Markdown("reports/cashflow/monthly.md"),
                            "reports/cashflow/yearly", Markdown("reports/cashflow/yearly.md")
            })
            ```
        """
        if isinstance(pages, dict):
            for k, v in pages.items():
                if k == "/":
                    k = Gui.__root_page_name
                self.add_page(name=k, page=v)
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
            self.__add_pages_in_folder(folder_name, folder_path)

    def add_partial(
        self,
        page: t.Union[str, Page],
    ) -> Partial:
        """Create a new `Partial^`.

        The [User Manual section on Partials](../../gui/pages/#partials) gives details on
        when and how to use this class.

        Arguments:
            page (Union[str, Page]): The page to create a new Partial from.<br/>
                It can be an instance of `Markdown^` or `Html^`.<br/>
                If _page_ is a string, then:

                - If _page_ is set to the pathname of a readable file, the content of
                  the new `Partial` is read as Markdown input text.
                - If it is not, the content of the new `Partial` is read from this string
                  as Markdown text.

        Returns:
            Partial: the new Partial object defined by _page_.
        """
        new_partial = Partial()
        # Validate name
        if new_partial._route in self._config.partial_routes or new_partial._route in self._config.routes:
            warnings.warn(f'Partial name "{new_partial._route}" is already defined')
        if isinstance(page, str):
            from .renderers import Markdown

            page = Markdown(page)
        elif not isinstance(page, Page):
            raise Exception(f'Partial name "{new_partial._route}" has invalid Page')
        new_partial._renderer = page
        # Append partial to _config
        self._config.partials.append(new_partial)
        self._config.partial_routes.append(str(new_partial._route))
        return new_partial

    # Main binding method (bind in markdown declaration)
    def _bind_var(self, var_name: str) -> bool:
        if not hasattr(self._bindings(), var_name) and var_name in self.__locals_bind.keys():
            self._bind(var_name, self.__locals_bind[var_name])
            return True
        return False

    def _bind_var_val(self, var_name: str, value: t.Any) -> bool:
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

    def load_config(self, config: Config) -> None:
        self._config._load(config)

    def _download(self, content: t.Any, name: t.Optional[str] = "", on_action: t.Optional[str] = ""):
        content_str = self._get_content("Gui.download", content, False)
        self._send_ws_download(content_str, str(name), str(on_action))

    def _notify(
        self,
        notification_type: str = "I",
        message: str = "",
        browser_notification: t.Optional[bool] = None,
        duration: t.Optional[int] = None,
    ):
        self.__send_ws_alert(
            notification_type,
            message,
            self._get_config("browser_notification", True) if browser_notification is None else browser_notification,
            self._get_config("notification_duration", 3000) if duration is None else duration,
        )

    def _hold_actions(
        self,
        callback: t.Optional[t.Union[str, t.Callable]] = None,
        message: t.Optional[str] = "Work in Progress...",
    ):  # pragma: no cover
        action_name = callback.__name__ if callable(callback) else callback
        func = self.__get_on_cancel_block_ui(action_name)
        def_action_name = func.__name__
        _setscopeattr(self, def_action_name, func)

        if _hasscopeattr(self, Gui.__UI_BLOCK_NAME):
            _setscopeattr(self, Gui.__UI_BLOCK_NAME, True)
        else:
            self._bind(Gui.__UI_BLOCK_NAME, True)
        self.__send_ws_block(action=def_action_name, message=message, cancel=bool(action_name))

    def _resume_actions(self):  # pragma: no cover
        if _hasscopeattr(self, Gui.__UI_BLOCK_NAME):
            _setscopeattr(self, Gui.__UI_BLOCK_NAME, False)
        self.__send_ws_block(close=True)

    def _navigate(self, to: t.Optional[str] = ""):
        to = to or Gui.__root_page_name
        if to not in self._config.routes:
            warnings.warn(f'cannot navigate to "{to if to != Gui.__root_page_name else "/"}": unknown page.')
            return
        self.__send_ws_navigate(to)

    def _register_data_accessor(self, data_accessor_class: t.Type[_DataAccessor]) -> None:
        self._accessors._register(data_accessor_class)

    def _get_flask_app(self):
        return self._server.get_flask()

    def run(self, run_server: bool = True, run_in_thread: bool = False, **kwargs) -> None:
        """
        Starts the server that delivers pages to Web clients.

        Once you enter `run`, users can run Web browsers and point to the Web server
        URL that `Gui` serves. The default is to listen to the _localhost_ address
        (127.0.0.1) on the port number 5000. However, the configuration of this `Gui`
        object may impact that (see the [Configuration](../gui/configuration.md#configuring-the-gui-instance)
        section for details).

        Arguments:
            run_server (bool): whether or not to run a Web server locally.
                If set to _False_, a Web server is _not_ created and started.
            run_in_thread: TODO
            kwargs: TODO
        """
        if (_is_in_notebook() or run_in_thread) and hasattr(self._server, "_thread"):
            self._server._thread.kill()
            self._server._thread.join()
            self._flask_blueprint = []
            self._server = _Server(
                self,
                path_mapping=self._path_mapping,
                flask=self._flask,
                css_file=self._css_file,
                root_page_name=Gui.__root_page_name,
            )
            self._bindings()._new_scopes()

        app_config = self._config.config

        run_root_dir = os.path.dirname(
            inspect.getabsfile(t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back))
        )

        # Register _root_dir for abs path
        if not hasattr(self, "_root_dir"):
            self._root_dir = run_root_dir

        # Load application config from multiple sources (env files, kwargs, command line)
        self._config._build_config(run_root_dir, self.__env_filename, kwargs)

        # Special config for notebook runtime
        if _is_in_notebook() or run_in_thread:
            self._config.config["single_client"] = True

        if run_server and app_config["ngrok_token"]:  # pragma: no cover
            if not util.find_spec("pyngrok"):
                raise RuntimeError("Cannot use ngrok as pyngrok package is not installed")
            else:
                ngrok.set_auth_token(app_config["ngrok_token"])
                http_tunnel = ngrok.connect(app_config["port"], "http")
                app_config["use_reloader"] = False
                print(f" * NGROK Public Url: {http_tunnel.public_url}")

        # Save all local variables of the parent frame (usually __main__)
        if isinstance(kwargs.get("locals_bind"), dict):
            self.__locals_bind = kwargs.get("locals_bind")  # type: ignore
            warnings.warn("Caution: the Gui instance is using a custom 'locals_bind' setting.")
        else:
            self.__locals_bind = t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back).f_locals

        self.__state = State(self, self.__locals_bind.keys())

        # base global ctx is TaipyHolder classes + script modules and callables
        glob_ctx = {t.__name__: t for t in _TaipyBase.__subclasses__()}
        glob_ctx.update({k: v for k, v in self.__locals_bind.items() if inspect.ismodule(v) or callable(v)})
        self.__evaluator = _Evaluator(glob_ctx)

        # bind on_change and on_action function if available
        self.__bind_local_func("on_change")
        self.__bind_local_func("on_action")

        # add en empty main page if it is not defined
        if Gui.__root_page_name not in self._config.routes:
            new_page = _Page()
            new_page._route = Gui.__root_page_name
            new_page._renderer = _EmptyPage()
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
                title=self._get_config("title", "Taipy App"),
                favicon=self._get_config("favicon", "/favicon.png"),
                themes=self._get_themes(),
                root_margin=self._get_config("margin", None),
            )
        )

        # Run parse markdown to force variables binding at runtime
        # (save rendered html to page.rendered_jsx for optimization)
        for page in self._config.pages + self._config.partials:  # type: ignore
            # Server URL Rule for each page jsx
            pages_bp.add_url_rule(f"/taipy-jsx/{page._route}/", view_func=self._server._render_page)

        # server URL Rule for flask rendered react-router
        pages_bp.add_url_rule("/taipy-init/", view_func=self._server._render_route)

        # Register Flask Blueprint if available
        for bp in self._flask_blueprint:
            self._server.get_flask().register_blueprint(bp)

        # Register data accessor communicaiton data format (JSON, Apache Arrow)
        self._accessors._set_data_format(_DataFormat.APACHE_ARROW if app_config["use_arrow"] else _DataFormat.JSON)

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
                run_in_thread=run_in_thread,
            )

    def stop(self):
        if hasattr(self._server, "_thread"):
            self._server._thread.kill()
            self._server._thread.join()
            print("Gui server has been stopped")
