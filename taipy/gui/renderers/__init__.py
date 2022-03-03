from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod
from os import path

from ..utils import _varname_from_content
from ._html import _TaipyHTMLParser

if t.TYPE_CHECKING:
    from ..gui import Gui


class Page(ABC):
    """
    The base class that transform template text to actual pages that can be
    displayed on a Web browser.

    When a page is requested to be displayed, it is transformed into HTML
    code that can be sent to the client. All control placeholders are
    replaced by the appropriate graphical component so you can display
    your application variables, and potentially interact with them.
    """

    def __init__(self, content: str) -> None:
        """Initializes a new Page with the indicated content.

        Args:
            content (string): The text content or the path to the file holding the text to be transformed.

        If `content` is a path to a readable file, the file is read entirely as the text template.
        """
        self._content: t.Optional[str] = None
        self._filepath: t.Optional[str] = None
        self.__process_content(content)

    def __process_content(self, content: str) -> None:
        if path.exists(content) and path.isfile(content):
            with open(t.cast(str, content), "r") as f:
                self._content = f.read()
                # save file path for error handling
                self._filepath = content
        else:
            self._content = content

    def set_content(self, content: str) -> None:
        self.__process_content(content)

    def _get_content_detail(self, gui: Gui) -> str:
        if self._filepath:
            return f"in file '{self._filepath}'"
        if varname := _varname_from_content(gui, self._content):
            return f"in variable '{varname}'"
        return ""

    @abstractmethod
    def render(self, gui: Gui) -> str:
        pass


class _EmptyPage(Page):
    def __init__(self) -> None:
        super().__init__("<PageContent />")

    def render(self, gui: Gui) -> str:
        return str(self._content)


class Markdown(Page):
    """
    The page renderer for _Markdown_ text.
    """

    def __init__(self, content: str) -> None:
        """Initializes a new `Markdown` page renderer.

        Args:
            content (string): The text content or the path to the file holding the Markdown text to be transformed.
        """
        super().__init__(content)

    # Generate JSX from Markdown
    def render(self, gui: Gui) -> str:
        return gui._markdown.convert(str(self._content))


class Html(Page):
    """
    The page renderer for _HTML_ text.
    """

    def __init__(self, content: str) -> None:
        """Initializes a new `Html` page renderer.

        Args:
            content (string): The text content or the path to the file holding the HTML text to be transformed.
        """
        super().__init__(content)
        self.head = None

    # Modify path routes
    def modify_taipy_base_url(self, base_url):
        self._content = str(self._content).replace("{{taipy_base_url}}", f"/{base_url}")

    # Generate JSX from HTML
    def render(self, gui: Gui) -> str:
        parser = _TaipyHTMLParser(gui)
        parser.feed_data(str(self._content))
        self.head = parser.head
        return parser.get_jsx()
