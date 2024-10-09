# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
import typing as t
from contextlib import nullcontext
from operator import attrgetter
from pathlib import Path
from types import FrameType

from flask import has_app_context

from .utils import _get_module_name_from_frame, _is_in_notebook
from .utils._attributes import _attrsetter

if t.TYPE_CHECKING:
    from .gui import Gui


class State:
    """Accessor to the bound variables from callbacks.

    `State` is used when you need to access the value of variables
    bound to visual elements (see [Binding](../../../../../userman/gui/binding.md)).<br/>
    Because each browser connected to the application server may represent and
    modify any variable at any moment as the result of user interaction, each
    connection holds its own set of variables along with their values. We call
    the set of these the application variables the application _state_, as seen
    by a given client.

    Each callback (see [Callbacks](../../../../../userman/gui/callbacks.md)) receives a specific
    instance of the `State` class, where you can find all the variables bound to
    visual elements in your application.

    Note that `State` also is a Python Context Manager: In situations where you
    have several variables to update, it is more clear and more efficient to assign
    the variable values in a `with` construct:
    ```py
    def my_callback(state, ...):
      ...
      with state as s:
        s.var1 = value1
        s.var2 = value2
      ...
    ```

    You cannot set a variable in the context of a lambda function because Python
    prevents any use of the assignment operator.<br/>
    You can, however, use the `assign()` method on the state that the lambda function
    receives, so you can work around this limitation:

    Here is how you could define a button that changes the value of a variable
    directly in a page expressed using Markdown:
    ```
       <|Set variable|button|on_action={lambda s: s.assign("var_name", new_value)}|>
    ```
    This would be strictly similar to the Markdown line:
    ```
       <|Set variable|button|on_action=change_variable|>
    ```
    with the Python code:
    ```py
    def change_variable(state):
        state.var_name = new_value
    ```
    """

    __gui_attr = "_gui"
    __attrs = (
        __gui_attr,
        "_user_var_list",
        "_context_list",
    )
    __methods = (
        "assign",
        "broadcast",
        "get_gui",
        "refresh",
        "set_favicon",
        "_set_context",
        "_notebook_context",
        "_get_placeholder",
        "_set_placeholder",
        "_get_gui_attr",
        "_get_placeholder_attrs",
        "_add_attribute",
    )
    __placeholder_attrs = (
        "_taipy_p1",
        "_current_context",
    )
    __excluded_attrs = __attrs + __methods + __placeholder_attrs

    def __init__(self, gui: "Gui", var_list: t.Iterable[str], context_list: t.Iterable[str]) -> None:
        super().__setattr__(State.__attrs[1], list(State.__filter_var_list(var_list, State.__excluded_attrs)))
        super().__setattr__(State.__attrs[2], list(context_list))
        super().__setattr__(State.__attrs[0], gui)

    def get_gui(self) -> "Gui":
        """Return the Gui instance for this state object.

        Returns:
            Gui: The Gui instance for this state object.
        """
        return super().__getattribute__(State.__gui_attr)

    @staticmethod
    def __filter_var_list(var_list: t.Iterable[str], excluded_attrs: t.Iterable[str]) -> t.Iterable[str]:
        return filter(lambda n: n not in excluded_attrs, var_list)

    def __getattribute__(self, name: str) -> t.Any:
        if name == "__class__":
            return State
        if name in State.__methods:
            return super().__getattribute__(name)
        gui: "Gui" = self.get_gui()
        if name == State.__gui_attr:
            return gui
        if name in State.__excluded_attrs:
            raise AttributeError(f"Variable '{name}' is protected and is not accessible.")
        if gui._is_in_brdcst_callback() and (
            name not in gui._get_shared_variables() and not gui._bindings()._is_single_client()
        ):
            raise AttributeError(f"Variable '{name}' is not available to be accessed in shared callback.")
        if not name.startswith("__") and name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not defined.")
        with self._notebook_context(gui), self._set_context(gui):
            encoded_name = gui._bind_var(name)
            return getattr(gui._bindings(), encoded_name)

    def __setattr__(self, name: str, value: t.Any) -> None:
        gui: "Gui" = super().__getattribute__(State.__gui_attr)
        if gui._is_in_brdcst_callback() and (
            name not in gui._get_shared_variables() and not gui._bindings()._is_single_client()
        ):
            raise AttributeError(f"Variable '{name}' is not available to be accessed in shared callback.")
        if not name.startswith("__") and name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not accessible.")
        with self._notebook_context(gui), self._set_context(gui):
            encoded_name = gui._bind_var(name)
            setattr(gui._bindings(), encoded_name, value)

    def __getitem__(self, key: str):
        context = key if key in super().__getattribute__(State.__attrs[2]) else None
        if context is None:
            gui: "Gui" = super().__getattribute__(State.__gui_attr)
            page_ctx = gui._get_page_context(key)
            context = page_ctx if page_ctx is not None else None
        if context is None:
            raise RuntimeError(f"Can't resolve context '{key}' from state object")
        self._set_placeholder(State.__placeholder_attrs[1], context)
        return self

    def _set_context(self, gui: "Gui") -> t.ContextManager[None]:
        if (pl_ctx := self._get_placeholder(State.__placeholder_attrs[1])) is not None:
            self._set_placeholder(State.__placeholder_attrs[1], None)
            if pl_ctx != gui._get_locals_context():
                return gui._set_locals_context(pl_ctx)
        if len(inspect.stack()) > 1:
            ctx = _get_module_name_from_frame(t.cast(FrameType, t.cast(FrameType, inspect.stack()[2].frame)))
            current_context = gui._get_locals_context()
            # ignore context if the current one starts with the new one (to resolve for class modules)
            if ctx != current_context and not current_context.startswith(str(ctx)):
                return gui._set_locals_context(ctx)
        return nullcontext()

    def _notebook_context(self, gui: "Gui"):
        return gui.get_flask_app().app_context() if not has_app_context() and _is_in_notebook() else nullcontext()

    def _get_placeholder(self, name: str):
        if name in State.__placeholder_attrs:
            try:
                return super().__getattribute__(name)
            except AttributeError:
                return None
        return None

    def _set_placeholder(self, name: str, value: t.Any):
        if name in State.__placeholder_attrs:
            super().__setattr__(name, value)

    def _get_placeholder_attrs(self):
        return State.__placeholder_attrs

    def _add_attribute(self, name: str, default_value: t.Optional[t.Any] = None) -> bool:
        attrs: t.List[str] = super().__getattribute__(State.__attrs[1])
        if name not in attrs:
            attrs.append(name)
            gui = super().__getattribute__(State.__gui_attr)
            return gui._bind_var_val(name, default_value)
        return False

    def assign(self, name: str, value: t.Any) -> t.Any:
        """Assign a value to a state variable.

        This should be used only from within a lambda function used
        as a callback in a visual element.

        Arguments:
            name (str): The variable name to assign to.
            value (Any): The new variable value.

        Returns:
            Any: The previous value of the variable.
        """
        val = attrgetter(name)(self)
        _attrsetter(self, name, value)
        return val

    def refresh(self, name: str):
        """Refresh a state variable.

        This allows to re-sync the user interface with a variable value.

        Arguments:
            name (str): The variable name to refresh.
        """
        val = attrgetter(name)(self)
        _attrsetter(self, name, val)

    def broadcast(self, name: str, value: t.Any):
        """Update a variable on all clients.

        All connected clients will receive an update of the variable called *name* with the
        provided value, even if it is not shared.

        Arguments:
            name (str): The variable name to update.
            value (Any): The new variable value.
        """
        gui: "Gui" = super().__getattribute__(State.__gui_attr)
        with self._set_context(gui):
            encoded_name = gui._bind_var(name)
            gui._broadcast_all_clients(encoded_name, value)

    def __enter__(self):
        super().__getattribute__(State.__attrs[0]).__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__getattribute__(State.__attrs[0]).__exit__(exc_type, exc_value, traceback)

    def set_favicon(self, favicon_path: t.Union[str, Path]):
        """Change the favicon for the client of this state.

        This function dynamically changes the favicon (the icon associated with the application's
        pages) of Taipy GUI pages for the specific client of this state.

        Note that the *favicon* parameter to `(Gui.)run()^` can also be used to change
        the favicon when the application starts.

        Arguments:
            favicon_path: The path to the image file to use.<br/>
                This can be expressed as a path name or a URL (relative or not).
        """
        super().__getattribute__(State.__gui_attr).set_favicon(favicon_path, self)
