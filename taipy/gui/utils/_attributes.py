from operator import attrgetter
import typing as t

if t.TYPE_CHECKING:
    from ..gui import Gui


def getuserattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._bindings(), name, more[0])
    return getattr(gui._bindings(), name)


def hasuserattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._bindings(), name)


def getscopeattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._bindings()._get_data_scope(), name, more[0])
    return getattr(gui._bindings()._get_data_scope(), name)


def getscopeattr_drill(gui: "Gui", name: str) -> t.Any:
    return attrgetter(name)(gui._bindings()._get_data_scope())


def setscopeattr(gui: "Gui", name: str, value: t.Any):
    setattr(gui._bindings()._get_data_scope(), name, value)


def setscopeattr_drill(gui: "Gui", name: str, value: t.Any):
    attrsetter(gui._bindings()._get_data_scope(), name, value)


def hasscopeattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._bindings()._get_data_scope(), name)


def delscopeattr(gui: "Gui", name: str):
    delattr(gui._bindings()._get_data_scope(), name)


def attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)
    setattr(obj, var_name_split[-1], value)
