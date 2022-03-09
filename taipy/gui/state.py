import typing as t

from .utils import _MapDict

if t.TYPE_CHECKING:
    from .gui import Gui


class State:
    """This class allows access to the script variables in callbacks

    Attributes:

        assign (Callable): allows to set a variable inside a lambda function (state.assign("name", value) is equivalent to state.name = value).
    """

    __attrs = ("_gui", "_user_var_list")
    __methods = "assign"
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
        val = getattr(gui._bindings(), name)
        return val._dict if isinstance(val, _MapDict) else val

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
        """Allows to set a variable inside a lambda function.

        Args:
            name (string): The variable name.
            value (Any): New variable value.

        Returns (Any):
            Previous value.
        """
        val = getattr(self, name)
        setattr(self, name, value)
        return val

    def __enter__(self):
        super().__getattribute__(State.__attrs[0]).__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__getattribute__(State.__attrs[0]).__exit__(exc_type, exc_value, traceback)
