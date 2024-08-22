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

import ast
import inspect
import typing as t
from types import FrameType

from .get_module_name import _get_absolute_module_name_from_ast, _get_module_name_from_frame


def _get_imported_var(frame: FrameType) -> t.List[t.Tuple[str, str, str]]:
    st = ast.parse(inspect.getsource(frame))
    var_list: t.List[t.Tuple[str, str, str]] = []
    for node in ast.walk(st):
        if isinstance(node, ast.ImportFrom):
            # get the imported element as (name, asname, module)
            # ex: from module1 import a as x --> ("a", "x", "module1")
            frame_module_name = _get_module_name_from_frame(frame)
            node_module_name = ""
            if node.module and frame_module_name:
                node_module_name = _get_absolute_module_name_from_ast(str(frame_module_name), node.module, node.level)
            var_list.extend(
                (
                    child_node.name,
                    child_node.asname if child_node.asname is not None else child_node.name,
                    node_module_name,
                )
                for child_node in node.names
            )
    return var_list
