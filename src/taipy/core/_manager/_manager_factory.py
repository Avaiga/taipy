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

from abc import abstractmethod
from importlib import util
from typing import Type

from taipy.config import Config

from ._manager import _Manager


class _ManagerFactory:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core"

    @classmethod
    @abstractmethod
    def _build_manager(cls) -> Type[_Manager]:  # type: ignore
        raise NotImplementedError

    @classmethod
    def _build_repository(cls):
        raise NotImplementedError

    @classmethod
    def _using_enterprise(cls) -> bool:
        return util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None

    @staticmethod
    def _get_repository_with_repo_map(repository_map: dict):
        return repository_map.get(Config.core.repository_type, repository_map.get("default"))
