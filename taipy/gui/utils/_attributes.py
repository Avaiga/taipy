import typing as t
from operator import attrgetter

if t.TYPE_CHECKING:
    from ..gui import Gui


def _getscopeattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._bindings()._get_data_scope(), name, more[0])
    return getattr(gui._bindings()._get_data_scope(), name)


def _getscopeattr_drill(gui: "Gui", name: str) -> t.Any:
    return attrgetter(name)(gui._bindings()._get_data_scope())


def _setscopeattr(gui: "Gui", name: str, value: t.Any):
    setattr(gui._bindings()._get_data_scope(), name, value)


def _setscopeattr_drill(gui: "Gui", name: str, value: t.Any):
    _attrsetter(gui._bindings()._get_data_scope(), name, value)


def _hasscopeattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._bindings()._get_data_scope(), name)


def _delscopeattr(gui: "Gui", name: str):
    delattr(gui._bindings()._get_data_scope(), name)


def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)
    setattr(obj, var_name_split[-1], value)
