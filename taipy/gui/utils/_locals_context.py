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

import contextlib
import typing as t

from flask import g


class _LocalsContext:
    __ctx_g_name = "locals_context"

    def __init__(self) -> None:
        self.__default_module: str = ""
        self._lc_stack: t.List[str] = []
        self._locals_map: t.Dict[str, t.Dict[str, t.Any]] = {}

    def set_default(self, default: t.Dict[str, t.Any], default_module_name: str = "") -> None:
        self.__default_module = default_module_name
        self._locals_map[self.__default_module] = default

    def get_default(self) -> t.Dict[str, t.Any]:
        return self._locals_map[self.__default_module]

    def get_all_keys(self) -> t.Set[str]:
        keys = set()
        for v in self._locals_map.values():
            for i in v.keys():
                keys.add(i)
        return keys

    def get_all_context(self):
        return self._locals_map.keys()

    def add(self, context: t.Optional[str], locals_dict: t.Optional[t.Dict[str, t.Any]]):
        if context is not None and locals_dict is not None and context not in self._locals_map:
            self._locals_map[context] = locals_dict

    @contextlib.contextmanager
    def set_locals_context(self, context: t.Optional[str]) -> t.Iterator[None]:
        has_set_context = False
        try:
            if context in self._locals_map:
                if hasattr(g, _LocalsContext.__ctx_g_name):
                    self._lc_stack.append(getattr(g, _LocalsContext.__ctx_g_name))
                setattr(g, _LocalsContext.__ctx_g_name, context)
                has_set_context = True
            yield
        finally:
            if has_set_context and hasattr(g, _LocalsContext.__ctx_g_name):
                if len(self._lc_stack) > 0:
                    setattr(g, _LocalsContext.__ctx_g_name, self._lc_stack.pop())
                else:
                    delattr(g, _LocalsContext.__ctx_g_name)

    def get_locals(self) -> t.Dict[str, t.Any]:
        return self.get_default() if (context := self.get_context()) is None else self._locals_map[context]

    def get_context(self) -> t.Optional[str]:
        return getattr(g, _LocalsContext.__ctx_g_name) if hasattr(g, _LocalsContext.__ctx_g_name) else None

    def is_default(self) -> bool:
        return self.get_default() == self.get_locals()

    def _get_locals_bind_from_context(self, context: t.Optional[str]):
        if context is None:
            context = self.__default_module
        return self._locals_map[context]
