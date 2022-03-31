import typing as t
from abc import ABC, abstractmethod
from os import path

from .utils import _is_in_notebook, _varname_from_content


class Page(ABC):
    """
    Generic page generator.
    
    The `Page` class transforms template text into actual pages that can be displayed
    on a Web browser.

    When a page is requested to be displayed, it is converted into HTML
    code that can be sent to the client. All control placeholders are
    replaced by their respective graphical component so you can show
    your application variables and interact with them.
    """

    def __init__(self, content: str) -> None:
        """Initialize a new Page with the indicated content.

        Arguments:
            content: The text content or the path to the file holding the text to be transformed.

        If _content_ is a path to a readable file, the file is read entirely as the text template.
        """
        self._content = ""
        self._filepath = ""
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
        """Set a new page content.

        Reads the new page content and reinitializes the page to reflect the change.

        !!! important
            This function can only be used an IPython notebook context.

        Arguments:
            content: The text content or the path to the file holding the text to be transformed.
                If _content_ is a path to a readable file, the file is read entirely as the text
                template.

        Exceptions:
            RuntimeError: If this method is called outside an IPython notebook context.
        """
        if not _is_in_notebook():
            raise RuntimeError("'set_content()' must be used in an IPython notebook context")
        self.__process_content(content)

    def _get_content_detail(self, gui) -> str:
        if self._filepath:
            return f"in file '{self._filepath}'"
        if varname := _varname_from_content(gui, self._content):
            return f"in variable '{varname}'"
        return ""

    @abstractmethod
    def render(self, gui) -> str:
        pass
