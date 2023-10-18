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

from __future__ import annotations

import copy
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterable

from ._context_manager import _BuilderContextManager
from ._factory import _BuilderFactory

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Element(ABC):
    """NOT DOCUMENTED"""

    _ELEMENT_NAME = ""
    _DEFAULT_PROPERTY = ""

    def __new__(cls, *args, **kwargs):
        obj = super(_Element, cls).__new__(cls)
        parent = _BuilderContextManager().peek()
        if parent is not None:
            parent.add(obj)
        return obj

    def __init__(self, *args, **kwargs):
        self._properties: t.Dict[str, t.Any] = {}
        if args and self._DEFAULT_PROPERTY != "":
            self._properties = {self._DEFAULT_PROPERTY: args[0]}
        self._properties.update(kwargs)
        self.parse_properties()

    def update(self, **kwargs):
        self._properties.update(kwargs)
        self.parse_properties()

    # Convert property value to string
    def parse_properties(self):
        self._properties = {k: _Element._parse_property(v) for k, v in self._properties.items()}

    # Get a deepcopy version of the properties
    def _deepcopy_properties(self):
        return copy.deepcopy(self._properties)

    @staticmethod
    def _parse_property(value: t.Any) -> t.Any:
        if isinstance(value, (str, dict, Iterable)):
            return value
        if hasattr(value, "__name__"):
            return str(getattr(value, "__name__"))
        return str(value)

    @abstractmethod
    def _render(self, gui: "Gui") -> str:
        pass


class _Block(_Element):
    """NOT DOCUMENTED"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children: t.List[_Element] = []

    def add(self, *elements: _Element):
        for element in elements:
            if element not in self._children:
                self._children.append(element)
        return self

    def __enter__(self):
        _BuilderContextManager().push(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _BuilderContextManager().pop()

    def _render(self, gui: "Gui") -> str:
        el = _BuilderFactory.create_element(gui, self._ELEMENT_NAME, self._deepcopy_properties())
        return f"{el[0]}{self._render_children(gui)}</{el[1]}>"

    def _render_children(self, gui: "Gui") -> str:
        return "\n".join([child._render(gui) for child in self._children])


class _DefaultBlock(_Block):
    _ELEMENT_NAME = "part"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class html(_Block):
    """A visual element defined as an HTML tag.

    This element can be used as a block element.
    """

    def __init__(self, *args, **kwargs):
        """Create a new `html` block.

        TODO
        """
        super().__init__(*args, **kwargs)
        if not args:
            raise RuntimeError("Can't render html element. Missing html tag name.")
        self._ELEMENT_NAME = args[0]
        self._content = args[1] if len(args) > 1 else ""

    def _render(self, gui: "Gui") -> str:
        open_tag_attributes = " ".join([f'{k}="{str(v)}"' for k, v in self._properties.items()])
        open_tag = f"<{self._ELEMENT_NAME} {open_tag_attributes}>"
        return f"{open_tag}{self._content}{self._render_children(gui)}</{self._ELEMENT_NAME}>"


class _Control(_Element):
    """NOT DOCUMENTED"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _render(self, gui: "Gui") -> str:
        el = _BuilderFactory.create_element(gui, self._ELEMENT_NAME, self._deepcopy_properties())
        return (
            f"<div>{el[0]}</{el[1]}></div>"
            if f"<{el[1]}" in el[0] and f"</{el[1]}" not in el[0]
            else f"<div>{el[0]}</div>"
        )

    def __enter__(self):
        raise RuntimeError(f"Can't use Context Manager for control type '{self._ELEMENT_NAME}'")

    def __exit__(self, exc_type, exc_value, traceback):
        raise RuntimeError(f"Can't use Context Manager for control type '{self._ELEMENT_NAME}'")
