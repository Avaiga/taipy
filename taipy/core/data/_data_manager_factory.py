# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from functools import lru_cache
from typing import Type

from ...common._modules import EnterpriseEdition
from .._manager._manager_factory import _ManagerFactory
from ..common._utils import _load_fct
from ._data_fs_repository import _DataFSRepository
from ._data_manager import _DataManager


class _DataManagerFactory(_ManagerFactory):
    __REPOSITORY_MAP = {"default": _DataFSRepository}

    @classmethod
    @lru_cache
    def _build_manager(cls) -> Type[_DataManager]:  # type: ignore[reportIncompatibleMethodOverride]
        if EnterpriseEdition._is_installed():
            data_manager = _load_fct(EnterpriseEdition._CORE_MODULE_PATH + ".data._data_manager", "_DataManager")
            build_repository = _load_fct(
                EnterpriseEdition._CORE_MODULE_PATH + ".data._data_manager_factory",
                "_DataManagerFactory",
            )._build_repository  # type: ignore[reportFunctionMemberAccess]
        else:
            data_manager = _DataManager
            build_repository = cls._build_repository
        data_manager._repository = build_repository()  # type: ignore[reportFunctionMemberAccess]
        return data_manager  # type: ignore[return-value]

    @classmethod
    @lru_cache
    def _build_repository(cls):  # type: ignore[reportIncompatibleMethodOverride]
        return cls._get_repository_with_repo_map(cls.__REPOSITORY_MAP)()  # type: ignore[reportOptionalCall]
