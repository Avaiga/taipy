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

from typing import Type

from .._manager._manager_factory import _ManagerFactory
from ..common._utils import _load_fct
from ._job_fs_repository import _JobFSRepository
from ._job_manager import _JobManager
from ._job_sql_repository import _JobSQLRepository


class _JobManagerFactory(_ManagerFactory):

    __REPOSITORY_MAP = {"default": _JobFSRepository, "sql": _JobSQLRepository}

    @classmethod
    def _build_manager(cls) -> Type[_JobManager]:  # type: ignore
        if cls._using_enterprise():
            job_manager = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".job._job_manager", "_JobManager"
            )  # type: ignore
            build_repository = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".job._job_manager_factory", "_JobManagerFactory"
            )._build_repository  # type: ignore
        else:
            job_manager = _JobManager
            build_repository = cls._build_repository
        job_manager._repository = build_repository()  # type: ignore
        return job_manager  # type: ignore

    @classmethod
    def _build_repository(cls):
        return cls._get_repository_with_repo_map(cls.__REPOSITORY_MAP)()
