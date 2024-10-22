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
import typing as t
from operator import attrgetter
from types import FrameType

_python_builtins = dir(builtins)


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
        var_parts = node.id.split(".", 2)
        if var_parts[0] in self.non_vars:
            return node
        value = _get_value_in_frame(self.frame, var_parts[0])
        if callable(value):
            return node
        if len(var_parts) > 1:
            value = attrgetter(var_parts[1])(value)
        return ast.Constant(value=value, kind=None)


class _LambdaByName(ast.NodeVisitor):
    _DEFAULT_NAME = "<default>"

    def __init__(self, element_name: str, lineno: int, lambdas: t.Dict[str, ast.Lambda]) -> None:
        super().__init__()
        self.element_name = element_name.split(".")[-1]
        self.lambdas = lambdas
        self.lineno = lineno + 1

    def visit_Call(self, node):
        if getattr(node.func, "attr", None) == self.element_name:
            if self.lambdas.get(_LambdaByName._DEFAULT_NAME, None) is None and (
                a_lambda := next(
                    (
                        arg
                        for arg in node.args
                        if isinstance(arg, ast.Lambda)
                        and arg.lineno is not None
                        and arg.end_lineno is not None
                        and self.lineno >= arg.lineno
                        and self.lineno <= arg.end_lineno
                    ),
                    None,
                )
            ):
                self.lambdas[_LambdaByName._DEFAULT_NAME] = a_lambda

            for kwd in node.keywords:
                if (
                    kwd.arg is not None
                    and isinstance(kwd.value, ast.Lambda)
                    and kwd.value.lineno is not None
                    and kwd.value.end_lineno is not None
                    and self.lineno >= kwd.value.lineno
                    and self.lineno <= kwd.value.end_lineno
                ):
                    self.lambdas[kwd.arg] = kwd.value
