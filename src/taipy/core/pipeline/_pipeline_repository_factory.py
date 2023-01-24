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

from taipy.config.config import Config

from .._repository._repository_factory import _RepositoryFactory
from ..common._utils import _load_fct
from ._pipeline_fs_repository import _PipelineFSRepository
from ._pipeline_sql_repository import _PipelineSQLRepository


class _PipelineRepositoryFactory(_RepositoryFactory):
    _REPOSITORY_MAP = {"default": _PipelineFSRepository, "sql": _PipelineSQLRepository}

    @classmethod
    def _build_repository(cls) -> Union[_PipelineFSRepository, Any]:  # type: ignore
        if cls._using_enterprise():
            factory = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".pipeline._pipeline_repository_factory",
                "_PipelineRepositoryFactory",
            )
            return factory._build_repository()  # type: ignore
        return cls._REPOSITORY_MAP.get(
            Config.global_config.repository_type, cls._REPOSITORY_MAP.get("default")
        )()  # type: ignore
