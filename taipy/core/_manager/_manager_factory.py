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

from abc import abstractmethod
from typing import Type

from taipy.common.config import Config

from ._manager import _Manager


class _ManagerFactory:
    @classmethod
    @abstractmethod
    def _build_manager(cls) -> Type[_Manager]:  # type: ignore
        raise NotImplementedError

    @classmethod
    def _build_repository(cls):
        raise NotImplementedError

    @staticmethod
    def _get_repository_with_repo_map(repository_map: dict):
        return repository_map.get(Config.core.repository_type, repository_map.get("default"))
