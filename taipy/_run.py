import inspect
import typing as t
from types import FrameType

from .gui import Gui
from .rest import Rest


class NoApplicationToStart(Exception):
    ...


def _run(*apps: t.List[t.Union[Gui, Rest]], **kwargs):
    """
    Run one or multiple Taipy services.

    An Taipy service is an instance of an object that exposes a Web application.

    Parameters:
        *args (List[Union[`Gui^`, `Rest^`]]): Services to run. If several services are provided, all the services run simultaneously.
        **kwargs: Other parameters to provide to the services.
    """
    gui = __typing_get(apps, Gui)
    rest = __typing_get(apps, Rest)

    if not rest and not gui:
        raise NoApplicationToStart("Empty list of services to run.")

    if gui:
        gui._set_frame(t.cast(FrameType, inspect.currentframe()).f_back)

    if gui and rest:
        gui._set_flask(rest._app)
        gui.run(**kwargs)
    else:
        app = rest or gui
        app.run(**kwargs)


def __typing_get(l, type_):
    return next(filter(lambda o: isinstance(o, type_), l), None)
