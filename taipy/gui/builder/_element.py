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

from __future__ import annotations

import ast
import builtins
import copy
import inspect
import io
import re
import sys
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterable
from operator import attrgetter
from types import FrameType, FunctionType

from .._warnings import _warn

if sys.version_info < (3, 9):
    from ..utils.unparse import _Unparser
from ._context_manager import _BuilderContextManager
from ._factory import _BuilderFactory

if t.TYPE_CHECKING:
    from ..gui import Gui

python_builtins = dir(builtins)


def _get_value_in_frame(frame: FrameType, name: str):
    if not frame:
        return None
    if name in frame.f_locals:
        return frame.f_locals.get(name)
    return _get_value_in_frame(t.cast(FrameType, frame.f_back), name)


class _TransformVarToValue(ast.NodeTransformer):
    def __init__(self, frame: FrameType, non_vars: t.List[str]) -> None:
        super().__init__()
        self.frame = frame
        self.non_vars = non_vars

    def visit_Name(self, node):
        var_name = node.id.split(".", 2)[0]
        if var_name in self.non_vars:
            return node
        value = _get_value_in_frame(self.frame, var_name)
        if var_name != node.id:
            value = attrgetter(node.id.split(".", 2)[1])(value)
        return ast.Constant(value=value, kind=None)


class _Element(ABC):
    """NOT DOCUMENTED"""

    _ELEMENT_NAME = ""
    _DEFAULT_PROPERTY = ""
    __RE_INDEXED_PROPERTY = re.compile(r"^(.*?)__([\w\d]+)$")

    def __new__(cls, *args, **kwargs):
        obj = super(_Element, cls).__new__(cls)
        parent = _BuilderContextManager().peek()
        if parent is not None:
            parent.add(obj)
        return obj

    def __init__(self, *args, **kwargs) -> None:
        self.__variables: t.Dict[str, FunctionType] = {}
        self._properties: t.Dict[str, t.Any] = {}
        self.__calling_frame = t.cast(
            FrameType, t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back).f_back
        )

        if args and self._DEFAULT_PROPERTY != "":
            self._properties = {self._DEFAULT_PROPERTY: args[0]}
        self._properties.update(kwargs)
        self.parse_properties()

    def update(self, **kwargs):
        self._properties.update(kwargs)
        self.parse_properties()

    # Convert property value to string/function
    def parse_properties(self):
        self._properties = {
            _Element._parse_property_key(k): self._parse_property(k, v) for k, v in self._properties.items()
        }

    # Get a deepcopy version of the properties
    def _deepcopy_properties(self):
        return copy.deepcopy(self._properties)

    @staticmethod
    def _parse_property_key(key: str) -> str:
        if match := _Element.__RE_INDEXED_PROPERTY.match(key):
            return f"{match.group(1)}[{match.group(2)}]"
        return key

    def _parse_property(self, key: str, value: t.Any) -> t.Any:
        if isinstance(value, (str, dict, Iterable)):
            return value
        if isinstance(value, FunctionType):
            if key.startswith("on_"):
                return value
            else:
                try:
                    st = ast.parse(inspect.getsource(value).strip())
                    lambda_fn = next((node for node in ast.walk(st) if isinstance(node, ast.Lambda)), None)
                    if lambda_fn is not None:
                        args = [arg.arg for arg in lambda_fn.args.args]
                        targets = [
                            compr.target.id  # type: ignore[attr-defined]
                            for node in ast.walk(lambda_fn.body)
                            if isinstance(node, ast.ListComp)
                            for compr in node.generators
                        ]
                        tree = _TransformVarToValue(self.__calling_frame, args + targets + python_builtins).visit(
                            lambda_fn
                        )
                        ast.fix_missing_locations(tree)
                        if sys.version_info < (3, 9): # python 3.8 ast has no unparse
                            string_fd = io.StringIO()
                            _Unparser(tree, string_fd)
                            string_fd.seek(0)
                            lambda_text = string_fd.read()
                        else:
                            lambda_text = ast.unparse(tree)
                        new_code = compile("new_lambda = " + lambda_text, "<ast>", "exec")
                        namespace: t.Dict[str, FunctionType] = {}
                        exec(new_code, namespace)
                        var_name = f"__lambda_{id(namespace['new_lambda'])}"
                        self.__variables[var_name] = namespace["new_lambda"]
                        return f'{{{var_name}({", ".join(args)})}}'
                except Exception as e:
                    _warn("Error in lambda expression", e)
        if hasattr(value, "__name__"):
            return str(getattr(value, "__name__"))  # noqa: B009
        return str(value)

    def _bind_variables(self, gui: "Gui"):
        for var_name, var_value in self.__variables.items():
            gui._bind_var_val(var_name, var_value)

    @abstractmethod
    def _render(self, gui: "Gui") -> str:
        pass


class _Block(_Element):
    """NOT DOCUMENTED"""

    def __init__(self, *args, **kwargs) -> None:
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
        self._bind_variables(gui)
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

    Use this class to integrate raw HTML to your page.

    This element can be used as a block element.
    """

    def __init__(self, *args, **kwargs):
        """Create a new `html` block.

        Arguments:
            args (any[]): A list of one or two unnamed arguments:

                - *args[0]* is the HTML tag name. If empty or None, this represents an HTML text
                  node.
                - *args[1]* (optional) is the text of this element.<br/>
                  Note that special HTML characters (such as '&lt;' or '&amp;') do not need to be protected.
            kwargs (dict[str, any]): the HTML attributes for this element.<br/>
                These should be valid attribute names, with valid attribute values.

        Examples:
            - To generate `<br/>`, use:
               ```
               html("br")
               ```
            - To generate `<h1>My page title</h1>`, use:
               ```
               html("h1", "My page title")
               ```
            - To generate `<h1 id="page-title">My page title</h1>`, use:
               ```
               html("h1", "My page title", id="page-title")
               ```
            - To generate `<p>This is a <b>Taipy GUI</b> element.</p>`, use:
               ```
               with html("p"):
                   html(None, "This is a ")
                   html("b", "Taipy GUI")
                   html(None, " element.")
               ```
        """
        super().__init__(*args, **kwargs)
        if not args:
            raise RuntimeError("Can't render html element. Missing html tag name.")
        self._ELEMENT_NAME = args[0] if args[0] else None
        self._content = args[1] if len(args) > 1 else ""

    def _render(self, gui: "Gui") -> str:
        self._bind_variables(gui)
        if self._ELEMENT_NAME:
            attrs = ""
            if self._properties:
                attrs = " " + " ".join([f'{k}="{str(v)}"' for k, v in self._properties.items()])
            return f"<{self._ELEMENT_NAME}{attrs}>{self._content}{self._render_children(gui)}</{self._ELEMENT_NAME}>"
        else:
            return self._content


class _Control(_Element):
    """NOT DOCUMENTED"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _render(self, gui: "Gui") -> str:
        self._bind_variables(gui)
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
