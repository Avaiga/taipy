import inspect
from types import FrameType
from typing import Union, List

import typing
from taipy.gui import Gui
from taipy.rest import Rest


class NoApplicationToStart(Exception):
    ...


def _run(*apps: List[Union[Gui, Rest]], **kwargs):
    """
    Run a single or multiple Taipy services at the same time.

    An Taipy service is an instance of an object that can expose an web application.

    Parameters:
        *args (List[Union[`Gui^`, `Rest^`]]): Services to run.
        **kwargs: Other parameters to provide to the services.
    """
    gui = __typing_get(apps, Gui)
    rest = __typing_get(apps, Rest)

    if not rest and not gui:
        raise NoApplicationToStart("You should provide a application to run.")

    if gui:
        gui._set_frame(typing.cast(FrameType, inspect.currentframe()).f_back)

    if gui and rest:
        gui._set_flask(rest._app)
        gui.run(**kwargs)
    else:
        app = rest or gui
        app.run(**kwargs)


def __typing_get(l, type_):
    return next(filter(lambda o: isinstance(o, type_), l), None)
