# Page and Partial for multipage support
from __future__ import annotations

import typing as t
import warnings

from colorama import Fore

if t.TYPE_CHECKING:
    from .gui import Gui
    from .renderers import PageRenderer


class Page(object):
    """A page that can be served by a `Gui` instance.

    In order for `Gui` to serve pages to a Web browser, you must create instances of `Page`.

    Every page has a name, so it can be located in the address bar of the browser, and some
    content that is generated from a text template.

    Attributes:
        renderer (PageRenderer):  The renderer to be used for this page.
        route (string): The name of this page.
        style (string): TBD
        head: TBD
    """

    def __init__(self):
        self.rendered_jsx: t.Union[str, None] = None
        self.renderer: t.Union[PageRenderer, None] = None
        self.style: t.Union[str, None] = None
        self.route: t.Union[str, None] = None
        self.head: t.Union[str, None] = None

    def render(self, gui: Gui):
        if self.renderer is None:
            raise RuntimeError(f"Can't render page {self.route}: no renderer found")
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            self.rendered_jsx = self.renderer.render(gui)
            if len(w) > 0:
                print(Fore.RED)
                print(
                    message := f"--- {len(w)} warning(s) were found for page '{'/' if self.route == gui._get_root_page_name() else self.route}' {self.renderer._get_content_detail(gui)} ---",
                    flush=True,
                )
                for i, wm in enumerate(w):
                    print(f" - Warning {i + 1}: {wm.message}", flush=True)
                print("-" * len(message), Fore.RESET, flush=True)
        if hasattr(self.renderer, "head"):
            self.head = str(self.renderer.head)  # type: ignore


class Partial(Page):

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self.route = "TaiPy_partials_" + str(len(Partial.__partials))
        Partial.__partials[self.route] = self
