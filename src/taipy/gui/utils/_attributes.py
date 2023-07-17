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
from operator import attrgetter

if t.TYPE_CHECKING:
    from ..gui import Gui


def _getscopeattr(gui: "Gui", name: str, *more) -> t.Any:
    if more:
        return getattr(gui._get_data_scope(), name, more[0])
    return getattr(gui._get_data_scope(), name)


def _getscopeattr_drill(gui: "Gui", name: str) -> t.Any:
    return attrgetter(name)(gui._get_data_scope())


def _setscopeattr(gui: "Gui", name: str, value: t.Any):
    if gui._is_broadcasting():
        for scope in gui._get_all_data_scopes().values():
            setattr(scope, name, value)
    else:
        setattr(gui._get_data_scope(), name, value)


def _setscopeattr_drill(gui: "Gui", name: str, value: t.Any):
    if gui._is_broadcasting():
        for scope in gui._get_all_data_scopes().values():
            _attrsetter(scope, name, value)
    else:
        _attrsetter(gui._get_data_scope(), name, value)


def _hasscopeattr(gui: "Gui", name: str) -> bool:
    return hasattr(gui._get_data_scope(), name)


def _delscopeattr(gui: "Gui", name: str):
    delattr(gui._get_data_scope(), name)


def _attrsetter(obj: object, attr_str: str, value: object) -> None:
    var_name_split = attr_str.split(sep=".")
    for i in range(len(var_name_split) - 1):
        sub_name = var_name_split[i]
        obj = getattr(obj, sub_name)
    setattr(obj, var_name_split[-1], value)
