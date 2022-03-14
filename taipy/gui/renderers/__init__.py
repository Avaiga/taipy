from ..page import Page

import typing as t

from ._html import _TaipyHTMLParser

if t.TYPE_CHECKING:
    from ..gui import Gui


class _EmptyPage(Page):
    def __init__(self) -> None:
        super().__init__("<PageContent />")

    def render(self, gui) -> str:
        return str(self._content)


class Markdown(Page):
    """
    Page generator for _Markdown_ text.
    """

    def __init__(self, content: str) -> None:
        """Initialize a new `Markdown` page.

        Arguments:
            content: The text content or the path to the file holding the Markdown text
                to be transformed.<br/>
                If _content_ is a path to a readable file, the file is read as the Markdown
                template content.
        """
        super().__init__(content)

    # Generate JSX from Markdown
    def render(self, gui) -> str:
        return gui._markdown.convert(str(self._content))


class Html(Page):
    """
    Page generator for _HTML_ text.
    """

    def __init__(self, content: str) -> None:
        """Initialize a new `Html` page.

        Arguments:
            content: The text content or the path to the file holding the HTML text to
                be transformed.<br/>
                If _content_ is a path to a readable file, the file is read as the HTML
                template content.
        """
        super().__init__(content)
        self.head = None

    # Modify path routes
    def modify_taipy_base_url(self, base_url):
        self._content = str(self._content).replace("{{taipy_base_url}}", f"/{base_url}")

    # Generate JSX from HTML
    def render(self, gui) -> str:
        parser = _TaipyHTMLParser(gui)
        parser.feed_data(str(self._content))
        self.head = parser.head
        return parser.get_jsx()
