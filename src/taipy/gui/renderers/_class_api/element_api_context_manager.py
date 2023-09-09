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

from ...utils.singleton import _Singleton

if t.TYPE_CHECKING:
    from .element_api import BlockElementApi


class _ElementApiContextManager(object, metaclass=_Singleton):
    def __init__(self):
        self.__element_list: t.List["BlockElementApi"] = []

    def push(self, element: "BlockElementApi") -> None:
        self.__element_list.append(element)

    def pop(self) -> t.Optional["BlockElementApi"]:
        return self.__element_list.pop() if self.__element_list else None

    def peek(self) -> t.Optional["BlockElementApi"]:
        return self.__element_list[-1] if self.__element_list else None
