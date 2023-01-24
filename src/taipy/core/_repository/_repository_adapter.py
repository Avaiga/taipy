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
from importlib import util
from typing import Any, Optional, Union

from taipy.config.config import Config

from ..common import _utils
from ._filesystem_repository import _FileSystemRepository
from ._sql_repository import _SQLRepository


class _RepositoryAdapter:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = f"{_TAIPY_ENTERPRISE_MODULE}.core"

    _REPOSITORY_MAP = {"default": _FileSystemRepository, "sql": _SQLRepository}

    @classmethod
    def select_base_repository(cls) -> Optional[Union[_FileSystemRepository, Any]]:
        if cls._using_enterprise():
            adapter = _utils._load_fct(
                f"{cls._TAIPY_ENTERPRISE_MODULE}.core._repository._repository_adapter", "_RepositoryAdapter"
            )
            return adapter.select_base_repository()  # type: ignore
        return cls._REPOSITORY_MAP.get(Config.global_config.repository_type, cls._REPOSITORY_MAP.get("default"))

    @classmethod
    def _using_enterprise(cls) -> bool:
        return util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None
