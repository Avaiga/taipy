# Page and Partial for multipage support
from __future__ import annotations

import typing as t


class Page(object):
    def __init__(self):
        self.rendered_jsx = None
        self.template_renderer = None
        self.style = None
        self.route = None

    def render(self):
        if self.template_renderer is None:
            raise RuntimeError(f"Can't render JSX for {self.route} due to missing template_renderer!")
        self.rendered_jsx = self.template_renderer.render()


class Partial(Page):

    __partials: t.Dict[str, Partial] = {}

    def __init__(self):
        super().__init__()
        self.route = "/partials/tp_" + str(len(Partial.__partials))
        Partial.__partials[self.route] = self
