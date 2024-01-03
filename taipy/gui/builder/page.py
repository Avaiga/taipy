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

import typing as t

from .._renderers import _Renderer
from ._context_manager import _BuilderContextManager
from ._element import _Block, _DefaultBlock, _Element


class Page(_Renderer):
    """Page generator for the Builder API.

    This class is used to create a page created with the Builder API.<br/>
    Instance of this class can be added to the application using `Gui.add_page()^`.

    This class is typically be used as a Python Context Manager to add the elements.<br/>
    Here is how you can create a single-page application, creating the elements with code:
    ```py
    from taipy.gui import Gui
    from taipy.gui.builder import Page, button

    def do_something(state):
        pass

    with Page() as page:
        button(label="Press me", on_action=do_something)

    Gui(page).run()
    ```
    """

    def __init__(self, element: t.Optional[_Element] = None, **kwargs) -> None:
        """Initialize a new page.

        Arguments:
            element (*Element*): An optional element, defined in the `taipy.gui.builder` module,
                that is created in the page.<br/>
                The default creates a `part` where several elements can be stored.
        """
        if element is None:
            element = _DefaultBlock()
        kwargs["content"] = element
        super().__init__(**kwargs)

    # Generate JSX from Element Object
    def render(self, gui) -> str:
        if self._base_element is None:
            return "<h1>No Base Element found for Page</h1>"
        return self._base_element._render(gui)

    def add(self, *elements: _Element):
        if not isinstance(self._base_element, _Block):
            raise RuntimeError("Can't add child element to non-block element")
        for element in elements:
            if element not in self._base_element._children:
                self._base_element._children.append(element)
        return self

    def __enter__(self):
        if self._base_element is None:
            raise RuntimeError("Can't use context manager with missing block element for Page")
        if not isinstance(self._base_element, _Block):
            raise RuntimeError("Can't add child element to non-block element")
        _BuilderContextManager().push(self._base_element)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _BuilderContextManager().pop()
