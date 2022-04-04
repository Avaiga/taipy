import typing as t

from .gui import Gui
from .rest import Rest


def _run(*apps: t.List[t.Union[Gui, Rest]], **kwargs):
    """Run one or multiple Taipy services.

    A Taipy service is an instance of a class that runs code as a Web application.

    Parameters:
        *args (List[Union[`Gui^`, `Rest^`]]): Services to run. If several services are provided, all the services run simultaneously. If this is empty or set to None, this method does nothing.
        **kwargs: Other parameters to provide to the services.
    """
    gui = __typing_get(apps, Gui)
    rest = __typing_get(apps, Rest)

    if not rest and not gui:
        return

    if gui and rest:
        gui._set_flask(rest._app)
        gui.run(**kwargs)
    else:
        app = rest or gui
        app.run(**kwargs)


def __typing_get(l, type_):
    return next(filter(lambda o: isinstance(o, type_), l), None)
