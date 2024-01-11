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

from collections import UserList


class _ListAttributes(UserList):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent

    def __add_iterable(self, iterable):
        for i in iterable:
            super(_ListAttributes, self).append(i)

    def __set_self(self):
        from ... import core as tp

        if hasattr(self, "_parent"):
            tp.set(self._parent)

    def __add__(self, value):
        if hasattr(value, "__iter__"):
            self.__add_iterable(value)
        else:
            self.append(value)
        return self

    def extend(self, value) -> None:
        super(_ListAttributes, self).extend(value)
        self.__set_self()

    def append(self, value) -> None:
        super(_ListAttributes, self).append(value)
        self.__set_self()

    def remove(self, value):
        super(_ListAttributes, self).remove(value)
        self.__set_self()

    def clear(self) -> None:
        super(_ListAttributes, self).clear()
        self.__set_self()
