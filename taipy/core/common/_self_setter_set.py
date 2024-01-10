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

from collections.abc import MutableSet
from typing import Any, Iterable, Iterator


class _SelfSetterSet(MutableSet):
    def __init__(self, parent, data: Iterable):
        self._parent = parent
        self.data = set(data)

    def __set_self(self):
        from ... import core as tp

        if hasattr(self, "_parent"):
            tp.set(self._parent)

    def __contains__(self, value: Any) -> bool:
        return value in self.data

    def __repr__(self) -> str:
        return repr(self.data)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def add(self, value: Any):
        self.data.add(value)
        self.__set_self()

    def remove(self, value: Any):
        self.data.remove(value)
        self.__set_self()

    def discard(self, value: Any):
        self.data.discard(value)
        self.__set_self()

    def pop(self):
        item = self.data.pop()
        self.__set_self()
        return item

    def clear(self) -> None:
        self.data.clear()
        self.__set_self()
