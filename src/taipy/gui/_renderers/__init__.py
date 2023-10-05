# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from abc import ABC, abstractmethod
from os import path

from ..page import Page
from ..utils import _is_in_notebook, _varname_from_content
from ._class_api import (
    BlockElementApi,
    ControlElementApi,
    DefaultBlockElement,
    ElementApi,
    _ElementApiContextManager,
    _ElementApiGenerator,
    html,
)
from ._html import _TaipyHTMLParser

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Renderer(Page, ABC):
    def __init__(self, **kwargs) -> None:
        """Initialize a new _Renderer with the indicated content.

        Arguments:
            content (str): The text content or the path to the file holding the text to be transformed.

        If *content* is a path to a readable file, the file is read entirely as the text template.
        """
        super().__init__(**kwargs)
        content: t.Optional[t.Union[str, ElementApi]] = kwargs.get("content", None)
        if content is None:
            raise ValueError("'content' argument is missing for class '_Renderer'")
        self._content = ""
        self._base_element: t.Optional[ElementApi] = None
        self._filepath = ""
        if isinstance(content, str):
            self.__process_content(content)
        elif isinstance(content, ElementApi):
            self._base_element = content
        else:
            raise ValueError(
                f"'content' argument has incorrect type '{type(content).__name__}'. Property must be type of Union[str, ElementApi]"
            )

    def __process_content(self, content: str) -> None:
        if path.exists(content) and path.isfile(content):
            return self.__parse_file_content(content)
        if self._frame is not None:
            frame_dir_path = path.dirname(path.abspath(self._frame.f_code.co_filename))
            content_path = path.join(frame_dir_path, content)
            if path.exists(content_path) and path.isfile(content_path):
                return self.__parse_file_content(content_path)
        self._content = content

    def __parse_file_content(self, content):
        with open(t.cast(str, content), "r") as f:
            self._content = f.read()
            # Save file path for error handling
            self._filepath = content

    def set_content(self, content: str) -> None:
        """Set a new renderer content.

        Reads the new renderer content and reinitializes the _Renderer instance to reflect the change.

        !!! important
            This function can only be used in an IPython notebook context.

        Arguments:
            content (str): The text content or the path to the file holding the text to be transformed.
                If *content* is a path to a readable file, the file is read entirely as the text
                template.

        Exceptions:
            RuntimeError: If this method is called outside an IPython notebook context.
        """
        if not _is_in_notebook():
            raise RuntimeError("'set_content()' must be used in an IPython notebook context")
        self.__process_content(content)

    def _get_content_detail(self, gui: "Gui") -> str:
        if self._filepath:
            return f"in file '{self._filepath}'"
        if varname := _varname_from_content(gui, self._content):
            return f"in variable '{varname}'"
        return ""

    @abstractmethod
    def render(self, gui: "Gui") -> str:
        pass


class _EmptyPage(_Renderer):
    def __init__(self) -> None:
        super().__init__(content="<PageContent />")

    def render(self, gui: "Gui") -> str:
        return self._content


class Markdown(_Renderer):
    """
    Page generator for _Markdown_ text.

    Taipy can use Markdown text to create pages that are the base of
    user interfaces.

    You can find details on the Taipy Markdown-specific syntax and how to add
    Taipy Visual Elements in the [section on HTML](../gui/pages.md#using-markdown)
    of the User Manual.
    """

    def __init__(self, content: str, **kwargs) -> None:
        """Initialize a new `Markdown` page.

        Arguments:
            content (str): The text content or the path to the file holding the Markdown text
                to be transformed.<br/>
                If _content_ is a path to a readable file, the file is read as the Markdown
                template content.
        """
        kwargs["content"] = content
        super().__init__(**kwargs)

    # Generate JSX from Markdown
    def render(self, gui: "Gui") -> str:
        return gui._markdown.convert(self._content)


class Html(_Renderer):
    """Page generator for _HTML_ text.

    Taipy can use HTML code to create pages that are the base of
    user interfaces.

    You can find details on HTML-specific constructs and how to add
    Taipy Visual Elements in the [section on HTML](../gui/pages.md#using-html)
    of the User Manual.
    """

    def __init__(self, content: str, **kwargs) -> None:
        """Initialize a new `Html` page.

        Arguments:
            content (str): The text content or the path to the file holding the HTML text to
                be transformed.<br/>
                If _content_ is a path to a readable file, the file is read as the HTML
                template content.
        """
        kwargs["content"] = content
        super().__init__(**kwargs)
        self.head = None

    # Modify path routes
    def modify_taipy_base_url(self, base_url):
        self._content = self._content.replace("{{taipy_base_url}}", f"{base_url}")

    # Generate JSX from HTML
    def render(self, gui: "Gui") -> str:
        parser = _TaipyHTMLParser(gui)
        parser.feed_data(self._content)
        self.head = parser.head
        return parser.get_jsx()


class ClassApi(_Renderer):
    """
    Page generator for Element Api.
    """

    def __init__(self, content: t.Optional[ElementApi] = None, **kwargs) -> None:
        if content is None:
            content = DefaultBlockElement()
        kwargs["content"] = content
        super().__init__(**kwargs)

    # Generate JSX from Element Object
    def render(self, gui) -> str:
        if self._base_element is None:
            return "<h1>No Base Element found for Page</h1>"
        return self._base_element._render(gui)

    def add(self, *elements: ElementApi):
        if not isinstance(self._base_element, BlockElementApi):
            raise RuntimeError("Can't add child element to non-block element")
        for element in elements:
            if element not in self._base_element._children:
                self._base_element._children.append(element)
        return self

    def __enter__(self):
        if self._base_element is None:
            raise RuntimeError("Can't use context manager with missing block element for Page")
        if not isinstance(self._base_element, BlockElementApi):
            raise RuntimeError("Can't add child element to non-block element")
        _ElementApiContextManager().push(self._base_element)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _ElementApiContextManager().pop()
