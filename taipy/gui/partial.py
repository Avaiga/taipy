from __future__ import annotations

import typing as t

from ._page import _Page


class Partial(_Page):
    """The class that allows to define a part of a page that is re-usable in Dialog or Pane controls."""

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self._route = f"TaiPy_partials_{len(Partial.__partials)}"
        Partial.__partials[self._route] = self
