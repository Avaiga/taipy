from __future__ import annotations

import typing as t

from ._page import _Page


class Partial(_Page):
    """Re-usable Page content.

    Partials are used when you need to use a partial page content in different
    and not related pages. This allows not to have to repeat yourself when
    creating your page templates.

    Visual elements such as [`dialog`](../gui/viselements/dialog.md) or
    [`pane`](../gui/viselements/pane.md)] can use Partials.

    Note that `Partial` has no constructor (no `__init__()` method): to create a
    Partial, you must call the `Gui.add_partial()^` function.
    """

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self._route = f"TaiPy_partials_{len(Partial.__partials)}"
        Partial.__partials[self._route] = self
