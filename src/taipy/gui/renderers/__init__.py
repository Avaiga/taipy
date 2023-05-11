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

from ..page import Page
from ._html import _TaipyHTMLParser

if t.TYPE_CHECKING:
    from ..gui import Gui


class _EmptyPage(Page):
    def __init__(self) -> None:
        super().__init__("<PageContent />")

    def render(self, gui) -> str:
        return self._content


class Markdown(Page):
    """
    Page generator for _Markdown_ text.

    Taipy can use Markdown text to create pages that are the base of
    user interfaces.

    You can find details on the Taipy Markdown-specific syntax and how to add
    Taipy Visual Elements in the [section on HTML](../../gui/pages/#using-markdown)
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
        super().__init__(content, **kwargs)

    # Generate JSX from Markdown
    def render(self, gui) -> str:
        return gui._markdown.convert(self._content)


class Html(Page):
    """
    Page generator for _HTML_ text.

    Taipy can use HTML code to create pages that are the base of
    user interfaces.

    You can find details on HTML-specific constructs and how to add
    Taipy Visual Elements in the [section on HTML](../../gui/pages/#using-html)
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
        super().__init__(content, **kwargs)
        self.head = None

    # Modify path routes
    def modify_taipy_base_url(self, base_url):
        self._content = self._content.replace("{{taipy_base_url}}", f"{base_url}")

    # Generate JSX from HTML
    def render(self, gui) -> str:
        parser = _TaipyHTMLParser(gui)
        parser.feed_data(self._content)
        self.head = parser.head
        return parser.get_jsx()
