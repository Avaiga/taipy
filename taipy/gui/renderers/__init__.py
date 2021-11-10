from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod
from os import path

from ._html import TaipyHTMLParser
from ._markdown import makeTaipyExtension


class PageRenderer(ABC):
    def __init__(self, content: str) -> None:
        self._content = None
        if path.exists(content) and path.isfile(content):
            with open(t.cast(str, content), "r") as f:
                self._content = f.read()
        else:
            self._content = content

    @abstractmethod
    def render(self) -> str:
        pass

class EmptyPageRenderer(PageRenderer):
    def __init__(self) -> None:
        super().__init__("<PageContent />")
    
    def render(self) -> str:
        return self._content

class Markdown(PageRenderer):
    def __init__(self, content: str) -> None:
        super().__init__(content)

    # Generate JSX from Markdown
    def render(self) -> str:
        from ..gui import Gui

        return Gui._markdown.convert(t.cast(str, self._content))


class Html(PageRenderer):
    def __init__(self, content: str) -> None:
        super().__init__(content)
        self.head = None

    # Modify path routes
    def modify_taipy_base_url(self, base_url):
        self._content = str(self._content).replace("{{taipy_base_url}}", f"/{base_url}")

    # Generate JSX from HTML
    def render(self) -> str:
        parser = TaipyHTMLParser()
        parser.feed(t.cast(str, self._content))
        self.head = parser.head
        return parser.get_jsx()
