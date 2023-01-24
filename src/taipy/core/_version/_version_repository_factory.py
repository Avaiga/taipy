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

from typing import Any, Union

from taipy.config import Config

from .._repository._repository_factory import _RepositoryFactory
from ..common._utils import _load_fct
from ._version_fs_repository import _VersionFSRepository
from ._version_sql_repository import _VersionSQLRepository


class _VersionRepositoryFactory(_RepositoryFactory):
    _REPOSITORY_MAP = {"default": _VersionFSRepository, "sql": _VersionSQLRepository}

    @classmethod
    def _build_repository(cls) -> Union[_VersionFSRepository, Any]:  # type: ignore
        if cls._using_enterprise():
            factory = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + "._version._version_repository_factory", "_VersionRepositoryFactory"
            )
            return factory._build_repository()  # type: ignore
        return cls._REPOSITORY_MAP.get(
            Config.global_config.repository_type, cls._REPOSITORY_MAP.get("default")
        )()  # type: ignore
