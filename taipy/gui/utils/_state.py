import typing as t

from ._map_dict import _MapDict

if t.TYPE_CHECKING:
    from ..gui import Gui


class State:
    __attrs = ("_gui", "_user_var_list")
    __methods = ("assign")

    def __init__(self, gui: "Gui", var_list: t.Iterable[str]) -> None:
        super().__setattr__(State.__attrs[1], list(var_list))
        super().__setattr__(State.__attrs[0], gui)

    def __getattribute__(self, name: str) -> t.Any:
        if name in State.__methods:
            return super().__getattribute__(name)
        if name not in super().__getattribute__(State.__attrs[1]):
            raise AttributeError(f"Variable '{name}' is not defined.")
        gui = super().__getattribute__(State.__attrs[0])
        if not hasattr(gui._bindings(), name):
            gui._bind_var(name)
        return getattr(gui._bindings(), name)

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name in State.__attrs:
            super().__setattr__(name, value)
        else:
            if name not in super().__getattribute__(State.__attrs[1]):
                raise AttributeError(f"Variable '{name}' is not defined.")
            gui = super().__getattribute__(State.__attrs[0])
            if not hasattr(gui._bindings(), name):
                gui._bind_var(name)
            setattr(gui._bindings(), name, value)

    def assign(self, name: str, value: t.Any) -> t.Any:
        val = getattr(self, name)
        setattr(self, name, value)
        return val

    def __enter__(self):
        super().__getattribute__(State.__attrs[0]).__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__getattribute__(State.__attrs[0]).__exit__(exc_type, exc_value, traceback)
