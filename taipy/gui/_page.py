# _Page for multipage support
from __future__ import annotations

import logging
import typing as t
import warnings

if t.TYPE_CHECKING:
    from .gui import Gui
    from .renderers import Page


class _Page(object):
    def __init__(self):
        self.rendered_jsx: t.Optional[str] = None
        self.renderer: t.Optional[Page] = None
        self.style: t.Optional[str] = None
        self.route: t.Optional[str] = None
        self.head: t.Optional[str] = None

    def render(self, gui: Gui):
        if self.renderer is None:
            raise RuntimeError(f"Can't render page {self.route}: no renderer found")
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            self.rendered_jsx = self.renderer.render(gui)
            if w:
                s = "\033[1;31m\n"
                s += (
                    message := f"--- {len(w)} warning(s) were found for page '{'/' if self.route == gui._get_root_page_name() else self.route}' {self.renderer._get_content_detail(gui)} ---\n"
                )
                for i, wm in enumerate(w):
                    s += f" - Warning {i + 1}: {wm.message}\n"
                s += "-" * len(message)
                s += "\033[0m\n"
                logging.warn(s)
        if hasattr(self.renderer, "head"):
            self.head = str(self.renderer.head)  # type: ignore
