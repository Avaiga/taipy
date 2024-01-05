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

import typing as t


class _MapDict(object):
    """
    Provide class binding, can utilize getattr, setattr functionality
    Also perform update operation
    """

    __local_vars = ("_dict", "_update_var")

    def __init__(self, dict_import: dict, app_update_var=None):
        self._dict = dict_import
        # Bind app update var function
        self._update_var = app_update_var

    def __len__(self):
        return self._dict.__len__()

    def __length_hint__(self):
        return self._dict.__length_hint__()

    def __getitem__(self, key):
        value = self._dict.__getitem__(key)
        if isinstance(value, dict):
            if self._update_var:
                return _MapDict(value, lambda s, v: self._update_var(f"{key}.{s}", v))
            else:
                return _MapDict(value)
        return value

    def __setitem__(self, key, value):
        if self._update_var:
            self._update_var(key, value)
        else:
            self._dict.__setitem__(key, value)

    def __delitem__(self, key):
        self._dict.__delitem__(key)

    def __missing__(self, key):
        return self._dict.__missing__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __reversed__(self):
        return self._dict.__reversed__()

    def __contains__(self, item):
        return self._dict.__contains__(item)

    # to be able to use getattr
    def __getattr__(self, attr):
        value = self._dict.__getitem__(attr)
        if isinstance(value, dict):
            if self._update_var:
                return _MapDict(value, lambda s, v: self._update_var(f"{attr}.{s}", v))
            else:
                return _MapDict(value)
        return value

    def __setattr__(self, attr, value):
        if attr in _MapDict.__local_vars:
            super().__setattr__(attr, value)
        else:
            self.__setitem__(attr, value)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def get(self, key: t.Any, default_value: t.Optional[str] = None) -> t.Optional[t.Any]:
        return self._dict.get(key, default_value)

    def clear(self) -> None:
        self._dict.clear()

    def setdefault(self, key, value=None) -> t.Optional[t.Any]:
        return self._dict.setdefault(key, value)

    def pop(self, key, default=None) -> t.Any:
        return self._dict.pop(key, default)

    def popitem(self) -> tuple:
        return self._dict.popitem()

    def copy(self) -> _MapDict:
        return _MapDict(self._dict.copy(), self._update_var)

    def update(self, d: dict) -> None:
        current_keys = self.keys()
        for k, v in d.items():
            if k not in current_keys or self[k] != v:
                self.__setitem__(k, v)
