from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

from ._html_ext import TaipyHTMLParser


class PageRenderer(ABC):
    def __init__(self, content: t.Optional[str], filename: t.Optional[str]) -> None:
        self._content = None
        if content is None and filename is None:
            raise RuntimeError("Missing `content` and `filename`")
        elif content is not None and filename is not None:
            raise RuntimeError("Can only contain either `content` or `filename`")
        elif content is not None:
            self._content = content
        else:
            with open(t.cast(str, filename), "r") as f:
                self._content = f.read()

    @abstractmethod
    def render(self) -> str:
        pass


class Markdown(PageRenderer):
    def __init__(self, content: t.Optional[str] = None, filename: t.Optional[str] = None) -> None:
        super().__init__(content, filename)

    # Generate JSX from Markdown
    def render(self) -> str:
        from .gui import Gui

        return Gui._markdown.convert(t.cast(str, self._content))


class Html(PageRenderer):
    def __init__(self, content: t.Optional[str] = None, filename: t.Optional[str] = None) -> None:
        super().__init__(content, filename)

    # Generate JSX from HTML
    def render(self) -> str:
        parser = TaipyHTMLParser()
        parser.feed(t.cast(str, self._content))
        return parser.get_jsx()
