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
        self._rendered_jsx: t.Optional[str] = None
        self._renderer: t.Optional[Page] = None
        self._style: t.Optional[str] = None
        self._route: t.Optional[str] = None
        self._head: t.Optional[list] = None

    def render(self, gui: Gui):
        if self._renderer is None:
            raise RuntimeError(f"Can't render page {self._route}: no renderer found")
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            self._rendered_jsx = self._renderer.render(gui)
            if w:
                s = "\033[1;31m\n"
                s += (
                    message := f"--- {len(w)} warning(s) were found for page '{'/' if self._route == gui._get_root_page_name() else self._route}' {self._renderer._get_content_detail(gui)} ---\n"
                )
                for i, wm in enumerate(w):
                    s += f" - Warning {i + 1}: {wm.message}\n"
                s += "-" * len(message)
                s += "\033[0m\n"
                logging.warn(s)
        if hasattr(self._renderer, "head"):
            self._head = list(self._renderer.head)  # type: ignore
