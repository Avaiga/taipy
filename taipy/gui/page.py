# Page and Partial for multipage support
from __future__ import annotations

import typing as t


class Page(object):
    def __init__(self):
        self.rendered_jsx = None
        self.renderer = None
        self.style = None
        self.route = None
        self.head = None

    def render(self):
        if self.renderer is None:
            raise RuntimeError(f"Can't render JSX for {self.route} due to missing renderer!")
        self.rendered_jsx = self.renderer.render()
        if hasattr(self.renderer, "head"):
            self.head = self.renderer.head


class Partial(Page):

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self.route = "TaiPy_partials_" + str(len(Partial.__partials))
        Partial.__partials[self.route] = self
