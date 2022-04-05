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

    Each callback (see [Callbacks](../gui/callbacks.md))) receives a specific
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
    directly in the Markdown code:
    ```
       <|Set variable|button|on_action={lambda s: s.assign("var_name", new_value}|>
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

    __attrs = ("_gui", "_user_var_list")
    __methods = ("assign",)
    __gui_attr = "_gui"

    def __init__(self, gui: "Gui", var_list: t.Iterable[str]) -> None:
        super().__setattr__(State.__attrs[1], list(var_list))
        super().__setattr__(State.__attrs[0], gui)

    def __getattribute__(self, name: str) -> t.Any:
        if name in State.__methods:
            return super().__getattribute__(name)
        gui = super().__getattribute__(State.__attrs[0])
        if name == State.__gui_attr:
            return gui
        if name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not defined.")
        if not hasattr(gui._bindings(), name):
            gui._bind_var(name)
        return getattr(gui._bindings(), name)

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name in State.__attrs:
            super().__setattr__(name, value)
        else:
            if name not in super().__getattribute__(State.__attrs[1]):
                raise AttributeError(f"Variable '{name}' is not accessible.")
            gui = super().__getattribute__(State.__attrs[0])
            if not hasattr(gui._bindings(), name):
                gui._bind_var(name)
            setattr(gui._bindings(), name, value)

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
