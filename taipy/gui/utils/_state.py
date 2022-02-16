import typing as t


class State:
    __attrs = ("_gui", "_user_var_list")

    def __init__(self, gui: t.Any) -> None:
        super().__setattr__(State.__attrs[1], list(gui._locals_bind.keys()))
        super().__setattr__(State.__attrs[0], gui)

    def __getattribute__(self, name: str) -> t.Any:
        if name in super().__getattribute__(State.__attrs[1]):
            gui = super().__getattribute__(State.__attrs[0])
            if not hasattr(gui, name):
                gui.bind_var(name)
            return getattr(gui, name)
        else:
            raise AttributeError(f"Local script has no attribute '{name}'.")

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name in State.__attrs:
            super().__setattr__(name, value)
        else:
            if name in super().__getattribute__(State.__attrs[1]):
                gui = super().__getattribute__(State.__attrs[0])
                if not hasattr(gui, name):
                    gui.bind_var(name)
                setattr(gui, name, value)
            else:
                raise AttributeError(f"Local script has no attribute '{name}'.")

    def __enter__(self):
        return super().__getattribute__(State.__attrs[0]).__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__getattribute__(State.__attrs[0]).__exit__(exc_type, exc_value, traceback)
