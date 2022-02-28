from __future__ import annotations

import typing as t

from ._page import _Page


class Partial(_Page):

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self.route = "TaiPy_partials_" + str(len(Partial.__partials))
        Partial.__partials[self.route] = self
