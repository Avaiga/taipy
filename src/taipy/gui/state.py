# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from operator import attrgetter

from .utils._attributes import _attrsetter

if t.TYPE_CHECKING:
    from .gui import Gui


class State:
    """Accessor to the bound variables from callbacks.

    `State` is used when you need to access the value of variables
    bound to visual elements (see [Binding](../gui/binding.md)).<br/>
    Because each browser connected to the application server may represent and
    modify any variable at any moment as the result of user interaction, each
    connection holds its own set of variables along with their values. We call
    the set of these the application variables the application _state_, as seen
    by a given client.

    Each callback (see [Callbacks](../gui/callbacks.md)) receives a specific
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
    __attrs = (__gui_attr, "_user_var_list")
    __methods = ("assign", "_get_placeholder", "_set_placeholder", "_get_gui_attr", "_get_placeholder_attrs")
    __placeholder_attrs = ("_taipy_p1",)
    __excluded_attrs = __attrs + __methods + __placeholder_attrs

    def __init__(self, gui: "Gui", var_list: t.Iterable[str]) -> None:
        super().__setattr__(State.__attrs[1], list(State.__filter_var_list(var_list, State.__excluded_attrs)))
        super().__setattr__(State.__attrs[0], gui)

    @staticmethod
    def __filter_var_list(var_list: t.Iterable[str], excluded_attrs: t.Iterable[str]) -> t.Iterable[str]:
        return filter(lambda n: n not in excluded_attrs, var_list)

    def __getattribute__(self, name: str) -> t.Any:
        if name in State.__methods:
            return super().__getattribute__(name)
        gui = super().__getattribute__(State.__gui_attr)
        if name == State.__gui_attr:
            return gui
        if name in State.__excluded_attrs:
            raise AttributeError(f"Variable '{name}' is protected and is not accessible.")
        if name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not defined.")
        encoded_name = gui._bind_var(name)
        return getattr(gui._bindings(), encoded_name)

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not accessible.")
        gui = super().__getattribute__(State.__gui_attr)
        encoded_name = gui._bind_var(name)
        setattr(gui._bindings(), encoded_name, value)

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

    def _get_gui_attr(self):
        return State.__gui_attr

    def _get_placeholder_attrs(self):
        return State.__placeholder_attrs

    def assign(self, name: str, value: t.Any) -> t.Any:
        """Assign a value to a state variable.

        This should be used only from within a lambda function used
        as a callback in a visual element.

        Args:
            name (str): The variable name to assign to.
            value (Any): The new variable value.

        Returns:
            Any: The previous value of the variable.
        """
        val = attrgetter(name)(self)
        _attrsetter(self, name, value)
        return val

    def __enter__(self):
        super().__getattribute__(State.__attrs[0]).__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__getattribute__(State.__attrs[0]).__exit__(exc_type, exc_value, traceback)
