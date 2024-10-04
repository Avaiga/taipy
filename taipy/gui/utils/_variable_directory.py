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
from types import FrameType

from ._locals_context import _LocalsContext
from .get_imported_var import _get_imported_var
from .get_module_name import _get_module_name_from_frame, _get_module_name_from_imported_var


class _VariableDirectory:
    def __init__(self, locals_context: _LocalsContext):
        self._locals_context = locals_context
        self._default_module = ""
        self._var_dir: t.Dict[str, t.Dict] = {}
        self._var_head: t.Dict[str, t.List[t.Tuple[str, str]]] = {}
        self._imported_var_dir: t.Dict[str, t.List[t.Tuple[str, str, str]]] = {}

    def set_default(self, frame: FrameType) -> None:
        self._default_module = _get_module_name_from_frame(frame)
        self.add_frame(frame)

    def add_frame(self, frame: t.Optional[FrameType]) -> None:
        if frame is None:
            return
        module_name = _get_module_name_from_frame(frame)
        if module_name not in self._imported_var_dir:
            imported_var_list = _get_imported_var(frame)
            self._imported_var_dir[t.cast(str, module_name)] = imported_var_list

    def pre_process_module_import_all(self) -> None:
        for imported_dir in self._imported_var_dir.values():
            additional_var_list: t.List[t.Tuple[str, str, str]] = []
            for name, asname, module in imported_dir:
                if name != "*" or asname != "*":
                    continue
                if module not in self._locals_context._locals_map.keys():
                    continue
                with self._locals_context.set_locals_context(module):
                    additional_var_list.extend(
                        (v, v, module) for v in self._locals_context.get_locals().keys() if not v.startswith("_")
                    )
            imported_dir.extend(additional_var_list)

    def process_imported_var(self) -> None:
        self.pre_process_module_import_all()
        default_imported_dir = self._imported_var_dir[t.cast(str, self._default_module)]
        with self._locals_context.set_locals_context(self._default_module):
            for name, asname, module in default_imported_dir:
                if name == "*" and asname == "*":
                    continue
                imported_module_name = _get_module_name_from_imported_var(
                    name, self._locals_context.get_locals().get(asname, None), module
                )
                temp_var_name = self.add_var(asname, self._default_module)
                self.add_var(name, imported_module_name, temp_var_name)

        for k, v in self._imported_var_dir.items():
            with self._locals_context.set_locals_context(k):
                for name, asname, module in v:
                    if name == "*" and asname == "*":
                        continue
                    imported_module_name = _get_module_name_from_imported_var(
                        name, self._locals_context.get_locals().get(asname, None), module
                    )
                    var_name = self.get_var(name, imported_module_name)
                    var_asname = self.get_var(asname, k)
                    if var_name is None and var_asname is None:
                        temp_var_name = self.add_var(asname, k)
                        self.add_var(name, imported_module_name, temp_var_name)
                    elif var_name is not None:
                        self.add_var(asname, k, var_name)
                    else:
                        self.add_var(name, imported_module_name, var_asname)

    def add_var(self, name: str, module: t.Optional[str], var_name: t.Optional[str] = None) -> str:
        if module is None:
            module = t.cast(str, self._default_module)
        if gv := self.get_var(name, module):
            return gv
        var_encode = _variable_encode(name, module) if module != self._default_module else name
        if var_name is None:
            var_name = var_encode
        self.__add_var_head(name, module, var_name)
        if var_encode != var_name:
            var_name_decode, module_decode = _variable_decode(var_name)
            if module_decode is None:
                module_decode = t.cast(str, self._default_module)
            self.__add_var_head(var_name_decode, module_decode, var_encode)
        if name not in self._var_dir:
            self._var_dir[name] = {module: var_name}
        else:
            self._var_dir[name][module] = var_name
        return var_name

    def __add_var_head(self, name: str, module: str, var_head: str) -> None:
        if var_head not in self._var_head:
            self._var_head[var_head] = [(name, module)]
        else:
            self._var_head[var_head].append((name, module))

    def get_var(self, name: str, module: str) -> t.Optional[str]:
        if name in self._var_dir and module in self._var_dir[name]:
            return self._var_dir[name][module]
        return None


_MODULE_NAME_MAP: t.List[str] = []
_MODULE_ID = "_TPMDL_"
_RE_TPMDL_DECODE = re.compile(r"(.*?)" + _MODULE_ID + r"(\d+)$")

def _is_moduled_variable(var_name: str):
    return _MODULE_ID in var_name

def _variable_encode(var_name: str, module_name: t.Optional[str]):
    if module_name is None:
        return var_name
    if module_name not in _MODULE_NAME_MAP:
        _MODULE_NAME_MAP.append(module_name)
    return f"{var_name}{_MODULE_ID}{_MODULE_NAME_MAP.index(module_name)}"


def _variable_decode(var_name: str):
    from ._evaluator import _Evaluator

    if result := _RE_TPMDL_DECODE.match(var_name):
        return _Evaluator._expr_decode(str(result[1])), _MODULE_NAME_MAP[int(result[2])]
    return _Evaluator._expr_decode(var_name), None


def _reset_name_map():
    _MODULE_NAME_MAP.clear()
