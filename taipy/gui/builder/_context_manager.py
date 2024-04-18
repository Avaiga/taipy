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

from ..utils.singleton import _Singleton

if t.TYPE_CHECKING:
    from ._element import _Block


class _BuilderContextManager(object, metaclass=_Singleton):
    def __init__(self) -> None:
        self.__blocks: t.List["_Block"] = []

    def push(self, element: "_Block") -> None:
        self.__blocks.append(element)

    def pop(self) -> t.Optional["_Block"]:
        return self.__blocks.pop() if self.__blocks else None

    def peek(self) -> t.Optional["_Block"]:
        return self.__blocks[-1] if self.__blocks else None
