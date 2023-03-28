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
from ._task_fs_repository import _TaskFSRepository
from ._task_manager import _TaskManager
from ._task_sql_repository import _TaskSQLRepository


class _TaskManagerFactory(_ManagerFactory):

    __REPOSITORY_MAP = {"default": _TaskFSRepository, "sql": _TaskSQLRepository}

    @classmethod
    def _build_manager(cls) -> Type[_TaskManager]:  # type: ignore
        if cls._using_enterprise():
            task_manager = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".task._task_manager", "_TaskManager"
            )  # type: ignore
            build_repository = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".task._task_manager_factory", "_TaskManagerFactory"
            )._build_repository  # type: ignore
        else:
            task_manager = _TaskManager
            build_repository = cls._build_repository
        task_manager._repository = build_repository()  # type: ignore
        return task_manager  # type: ignore

    @classmethod
    def _build_repository(cls):
        return cls._get_repository_with_repo_map(cls.__REPOSITORY_MAP)()
