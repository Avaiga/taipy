from operator import attrgetter
import typing as t

from . import attrsetter

if t.TYPE_CHECKING:
    from ..gui import Gui


def getuserattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._get_user_data(), name, more[0])
    return getattr(gui._get_user_data(), name)


def hasuserattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._get_user_data(), name)


def getscopeattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._get_user_data()._get_data_scope(), name, more[0])
    return getattr(gui._get_user_data()._get_data_scope(), name)


def getscopeattr_drill(gui: "Gui", name: str) -> t.Any:
    return attrgetter(name)(gui._get_user_data()._get_data_scope())


def setscopeattr(gui: "Gui", name: str, value: t.Any):
    setattr(gui._get_user_data()._get_data_scope(), name, value)


def setscopeattr_drill(gui: "Gui", name: str, value: t.Any):
    attrsetter(gui._get_user_data()._get_data_scope(), name, value)


def hasscopeattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._get_user_data()._get_data_scope(), name)


def delscopeattr(gui: "Gui", name: str):
    delattr(gui._get_user_data()._get_data_scope(), name)
