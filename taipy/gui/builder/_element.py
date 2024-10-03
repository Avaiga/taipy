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
import copy
import inspect
import re
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterable
from types import FrameType, FunctionType

from .._warnings import _warn
from ..utils import _get_lambda_id, _getscopeattr
from ._context_manager import _BuilderContextManager
from ._factory import _BuilderFactory
from ._utils import _LambdaByName, _python_builtins, _TransformVarToValue

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Element(ABC):
    """NOT DOCUMENTED"""

    _ELEMENT_NAME = ""
    _DEFAULT_PROPERTY = ""
    __RE_INDEXED_PROPERTY = re.compile(r"^(.*?)__([\w\d]+)$")
    _TAIPY_EMBEDDED_PREFIX = "_tp_embedded_"
    _EMBEDDED_PROPERTIES = ["decimator"]
    _TYPES: t.Dict[str, str] = {}
    __LAMBDA_VALUE_IDX = 0

    def __new__(cls, *args, **kwargs):
        obj = super(_Element, cls).__new__(cls)
        parent = _BuilderContextManager().peek()
        if parent is not None:
            parent.add(obj)
        return obj

    def __init__(self, *args, **kwargs) -> None:
        self._properties: t.Dict[str, t.Any] = {}
        self._lambdas: t.Dict[str, str] = {}
        self.__calling_frame = t.cast(
            FrameType, t.cast(FrameType, t.cast(FrameType, inspect.currentframe()).f_back).f_back
        )

        if args and self._DEFAULT_PROPERTY != "":
            self._properties = {self._DEFAULT_PROPERTY: args[0]}
        # special attribute for inline
        self._is_inline = kwargs.pop("inline", False)
        self._properties.update(kwargs)
        self.parse_properties()

    def update(self, **kwargs):
        self._properties.update(kwargs)
        self.parse_properties()

    @staticmethod
    def __get_lambda_index():
        _Element.__LAMBDA_VALUE_IDX += 1
        _Element.__LAMBDA_VALUE_IDX %= 0xFFFFFFF0
        return _Element.__LAMBDA_VALUE_IDX

    def _evaluate_lambdas(self, gui: Gui):
        for k, lmbd in self._lambdas.items():
            expr = gui._evaluate_expr(lmbd, lambda_expr=True)
            gui._bind_var_val(k, _getscopeattr(gui, expr))

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

    def _is_callable(self, name: str):
        return (
            "callable" in self._TYPES.get(f"{parts[0]}__" if len(parts := name.split("__")) > 1 else name, "").lower()
        )

    def _parse_property(self, key: str, value: t.Any) -> t.Any:
        if isinstance(value, (str, dict, Iterable)):
            return value
        if isinstance(value, FunctionType):
            if key.startswith("on_") or self._is_callable(key):
                return value if value.__name__.startswith("<") else value.__name__
            # Parse lambda function_is_callable
            if (lambda_call := self.__parse_lambda_property(key, value)) is not None:
                return lambda_call
        # Embed value in the caller frame
        if not isinstance(value, str) and key in self._EMBEDDED_PROPERTIES:
            return self.__embed_object(value, is_expression=False)
        if hasattr(value, "__name__"):
            return str(getattr(value, "__name__"))  # noqa: B009
        return str(value)

    def __parse_lambda_property(self, key: str, value: t.Any) -> t.Any:
        try:
            source = inspect.findsource(value)
            st = ast.parse("".join(source[0]))
            lambda_by_name: t.Dict[str, ast.Lambda] = {}
            _LambdaByName(self._ELEMENT_NAME, source[1], lambda_by_name).visit(st)
            lambda_fn = lambda_by_name.get(
                key,
                lambda_by_name.get(_LambdaByName._DEFAULT_NAME, None) if key == self._DEFAULT_PROPERTY else None,
            )
            if lambda_fn is None:
                return None
            args = [arg.arg for arg in lambda_fn.args.args]
            targets = [
                comprehension.target.id  # type: ignore[attr-defined]
                for node in ast.walk(lambda_fn.body)
                if isinstance(node, ast.ListComp)
                for comprehension in node.generators
            ]
            tree = _TransformVarToValue(self.__calling_frame, args + targets + _python_builtins).visit(lambda_fn)
            ast.fix_missing_locations(tree)
            lambda_text = ast.unparse(tree)
            lambda_name = _get_lambda_id(value, index=(_Element.__get_lambda_index()))
            self._lambdas[lambda_name] = lambda_text
            return f'{{{lambda_name}({", ".join(args)})}}'
        except Exception as e:
            _warn("Error in lambda expression", e)
        return None

    def __embed_object(self, obj: t.Any, is_expression=True) -> str:
        """NOT DOCUMENTED
        Embed an object in the caller frame

        Return the Taipy expression of the embedded object
        """
        frame_locals = self.__calling_frame.f_locals
        obj_var_name = self._TAIPY_EMBEDDED_PREFIX + obj.__class__.__name__
        index = 0
        while f"{obj_var_name}_{index}" in frame_locals:
            index += 1
        obj_var_name = f"{obj_var_name}_{index}"
        frame_locals[obj_var_name] = obj
        return f"{{{obj_var_name}}}" if is_expression else obj_var_name

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
        self._evaluate_lambdas(gui)
        el = _BuilderFactory.create_element(gui, self._ELEMENT_NAME, self._deepcopy_properties())
        return f"{el[0]}{self._render_children(gui)}</{el[1]}>"

    def _render_children(self, gui: "Gui") -> str:
        return "\n".join([child._render(gui) for child in self._children])


class _DefaultBlock(_Block):
    _ELEMENT_NAME = "part"

    def __init__(self, *args, **kwargs):  # do not remove as it could break the search in frames
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
        self._evaluate_lambdas(gui)
        if self._ELEMENT_NAME:
            attrs = ""
            if self._properties:
                attrs = " " + " ".join([f'{k}="{str(v)}"' for k, v in self._properties.items()])
            return f"<{self._ELEMENT_NAME}{attrs}>{self._content}{self._render_children(gui)}</{self._ELEMENT_NAME}>"
        else:
            return self._content


class _Control(_Element):
    """NOT DOCUMENTED"""

    def __init__(self, *args, **kwargs):  # do not remove as it could break the search in frames
        super().__init__(*args, **kwargs)

    def _render(self, gui: "Gui") -> str:
        self._evaluate_lambdas(gui)
        el = _BuilderFactory.create_element(gui, self._ELEMENT_NAME, self._deepcopy_properties())
        inline_block = 'style="display:inline-block;"' if self._is_inline else ""
        return (
            f"<div {inline_block}>{el[0]}</{el[1]}></div>"
            if f"<{el[1]}" in el[0] and f"</{el[1]}" not in el[0]
            else f"<div {inline_block}>{el[0]}</div>"
        )

    def __enter__(self):
        raise RuntimeError(f"Can't use Context Manager for control type '{self._ELEMENT_NAME}'")

    def __exit__(self, exc_type, exc_value, traceback):
        raise RuntimeError(f"Can't use Context Manager for control type '{self._ELEMENT_NAME}'")


class content(_Control):
    """
    Create a `content` pseudo-element

    This pseudo-element can be used in the root page of your application. It is replaced at runtime
    by the content of the page the user navigates to.

    The usage of this pseudo-element is described in
    [this page](../../../../../../userman/gui/pages/index.md#application-header-and-footer).
    """

    def _render(self, gui: "Gui") -> str:
        el = _BuilderFactory.create_element(gui, "content", {})
        return f"{el[0]}</{el[1]}>"
