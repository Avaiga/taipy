# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import re
import typing as t
from abc import ABC, abstractmethod
from os import path

from charset_normalizer import detect

from taipy.common.logger._taipy_logger import _TaipyLogger

from ..page import Page
from ..utils import _is_in_notebook, _varname_from_content
from ._html import _TaipyHTMLParser

if t.TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver

    from ..gui import Gui


class _Renderer(Page, ABC):
    def __init__(self, **kwargs) -> None:
        """NOT DOCUMENTED
        Initialize a new _Renderer with the indicated content.

        Arguments:
            content (str): The text content or the path to the file holding the text to be transformed.

        If *content* is a path to a readable file, the file is read entirely as the text template.
        """
        from ..builder._element import _Element  # noqa: F811

        super().__init__(**kwargs)
        content: t.Optional[t.Union[str, _Element]] = kwargs.get("content", None)
        if content is None:
            raise ValueError("'content' argument is missing for class '_Renderer'")
        self._content = ""
        self._base_element: t.Optional[_Element] = None
        self._filepath = ""
        self._observer: t.Optional["BaseObserver"] = None
        self._encoding: t.Optional[str] = kwargs.get("encoding", None)
        if isinstance(content, str):
            self.__process_content(content)
        elif isinstance(content, _Element):
            self._base_element = content
        else:
            raise ValueError(
                f"'content' argument has incorrect type '{type(content).__name__}'. This must be a string or an Builder element."  # noqa: E501
            )

    def __process_content(self, content: str) -> None:
        relative_file_path = (
            None if self._frame is None else path.join(path.dirname(self._frame.f_code.co_filename), content)
        )
        if relative_file_path is not None and path.exists(relative_file_path) and path.isfile(relative_file_path):
            content = relative_file_path
        if content == relative_file_path or (path.exists(content) and path.isfile(content)):
            self.__parse_file_content(content)
            # Watchdog observer: watch for file changes
            if _is_in_notebook() and self._observer is None:
                self.__observe_file_change(content)
            return
        self._content = self.__sanitize_content(content)

    def __observe_file_change(self, file_path: str):
        from watchdog.observers import Observer

        from .utils import FileWatchdogHandler

        self._observer = Observer()
        file_path = path.abspath(file_path)
        self._observer.schedule(FileWatchdogHandler(file_path, self), path.dirname(file_path), recursive=False)
        self._observer.start()

    def __parse_file_content(self, content):
        with open(t.cast(str, content), "rb") as f:
            file_content = f.read()
            encoding = "utf-8"
            if self._encoding is not None:
                encoding = self._encoding
                _TaipyLogger._get_logger().info(f"'{encoding}' encoding was used to decode file '{content}'.")
            elif (detected_encoding := detect(file_content)["encoding"]) is not None:
                encoding = detected_encoding
                _TaipyLogger._get_logger().info(f"Detected '{encoding}' encoding for file '{content}'.")
            else:
                _TaipyLogger._get_logger().info(f"Using default '{encoding}' encoding for file '{content}'.")
            self._content = self.__sanitize_content(file_content.decode(encoding))
            # Save file path for error handling
            self._filepath = content

    def __sanitize_content(self, content: str) -> str:
        # Replace all CRLF (\r\n) and CR (\r) by LF (\n)
        return re.sub(r"\r", "\n", re.sub(r"\r\n", "\n", content))

    def set_content(self, content: str) -> None:
        if not _is_in_notebook():
            raise RuntimeError("'set_content()' must be used in an IPython notebook context")
        self.__process_content(content)
        if self._notebook_gui is not None and self._notebook_page is not None:
            if self._notebook_gui._config.root_page is self._notebook_page:
                self._notebook_gui._navigate("/", {"tp_reload_all": "true"})
                return
            self._notebook_gui._navigate(self._notebook_page._route, {"tp_reload_same_route_only": "true"})

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
    """Page generator for *Markdown* text.

    Taipy can use Markdown text to create pages that are the base of
    user interfaces.

    You can find details on the Taipy Markdown-specific syntax and how to add
    Taipy Visual Elements in the [section on Markdown](../../../../../userman/gui/pages/markdown.md)
    of the User Manual.
    """

    def __init__(self, content: str, **kwargs) -> None:
        """Initialize a new `Markdown` page.

        Arguments:
            content (str): The text content or the path to the file holding the Markdown text
                to be transformed.<br/>
                If *content* is a path to a readable file, the file is read as the Markdown
                template content.

        The `Markdown` constructor supports the *style* parameter as explained in the
        [section on Styling](../../../../../userman/gui/styling/index.md#style-sheets) and in the
        `(taipy.gui.Page.)set_style()^` method.
        """
        kwargs["content"] = content
        super().__init__(**kwargs)

    # Generate JSX from Markdown
    def render(self, gui: "Gui") -> str:
        return gui._markdown.convert(self._content)


class Html(_Renderer):
    """Page generator for *HTML* text.

    Taipy can use HTML code to create pages that are the base of
    user interfaces.

    You can find details on HTML-specific constructs and how to add
    Taipy Visual Elements in the [section on HTML](../../../../../userman/gui/pages/html.md)
    of the User Manual.
    """

    def __init__(self, content: str, **kwargs) -> None:
        """Initialize a new `Html` page.

        Arguments:
            content (str): The text content or the path to the file holding the HTML text to
                be transformed.<br/>
                If *content* is a path to a readable file, the file is read as the HTML
                template content.

        The `Html` constructor supports the *style* parameter as explained in the
        [section on Styling](../../../../../userman/gui/styling/index.md#style-sheets) and in the
        `(taipy.gui.Page.)set_style()^` method.
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
