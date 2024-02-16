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
from datetime import datetime
from random import random

from ..data.data_scope import _DataScopes
from ._map_dict import _MapDict

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Bindings:
    def __init__(self, gui: "Gui") -> None:
        self.__gui = gui
        self.__scopes = _DataScopes()

    def _bind(self, name: str, value: t.Any) -> None:
        if hasattr(self, name):
            raise ValueError(f"Variable '{name}' is already bound")
        if not name.isidentifier():
            raise ValueError(f"Variable name '{name}' is invalid")
        if isinstance(value, dict):
            setattr(self._get_data_scope(), name, _MapDict(value))
        else:
            setattr(self._get_data_scope(), name, value)
        # prop = property(self.__value_getter(name), self.__value_setter(name))
        setattr(_Bindings, name, self.__get_property(name))

    def __get_property(self, name):
        def __setter(ud: _Bindings, value: t.Any):
            if isinstance(value, dict):
                value = _MapDict(value, None)
            ud.__gui._update_var(name, value)

        def __getter(ud: _Bindings) -> t.Any:
            value = getattr(ud._get_data_scope(), name)
            if isinstance(value, _MapDict):
                return _MapDict(value._dict, lambda k, v: ud.__gui._update_var(f"{name}.{k}", v))
            else:
                return value

        return property(__getter, __setter)  # Getter, Setter

    def _set_single_client(self, value: bool) -> None:
        self.__scopes.set_single_client(value)

    def _is_single_client(self) -> bool:
        return self.__scopes.is_single_client()

    def _get_or_create_scope(self, id: str):
        create = not id
        if create:
            id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{random()}"
            self.__gui._send_ws_id(id)
        self.__scopes.create_scope(id)
        return id, create

    def _new_scopes(self):
        self.__scopes = _DataScopes()

    def _get_data_scope(self):
        return self.__scopes.get_scope(self.__gui._get_client_id())[0]

    def _get_data_scope_metadata(self):
        return self.__scopes.get_scope(self.__gui._get_client_id())[1]

    def _get_all_scopes(self):
        return self.__scopes.get_all_scopes()
