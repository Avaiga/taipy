# Copyright 2022 Avaiga Private Limited
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
from typing import Type

from taipy.core.common._utils import _load_fct
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager import _JobManager
from taipy.core.pipeline._pipeline_manager import _PipelineManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.task._task_manager import _TaskManager


class _ManagerFactory:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core"

    @classmethod
    def _scenario_manager(cls) -> Type[_ScenarioManager]:
        if cls._has_enterprise():
            return _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".scenario._scenario_manager",
                "_ScenarioManager",
            )  # type: ignore
        return _ScenarioManager

    @classmethod
    def _data_manager(cls) -> Type[_DataManager]:
        if cls._has_enterprise():
            return _load_fct(cls._TAIPY_ENTERPRISE_CORE_MODULE + ".data._data_manager", "_DataManager")  # type: ignore
        return _DataManager

    @classmethod
    def _cycle_manager(cls) -> Type[_CycleManager]:
        if cls._has_enterprise():
            return _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".cycle._cycle_manager", "_CycleManager"
            )  # type: ignore
        return _CycleManager

    @classmethod
    def _job_manager(cls) -> Type[_JobManager]:
        if cls._has_enterprise():
            return _load_fct(cls._TAIPY_ENTERPRISE_CORE_MODULE + ".job._job_manager", "_JobManager")  # type: ignore
        return _JobManager

    @classmethod
    def _pipeline_manager(cls) -> Type[_PipelineManager]:
        if cls._has_enterprise():
            return _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".pipeline._pipeline_manager",
                "_PipelineManager",
            )  # type: ignore
        return _PipelineManager

    @classmethod
    def _task_manager(cls) -> Type[_TaskManager]:
        if cls._has_enterprise():
            return _load_fct(cls._TAIPY_ENTERPRISE_CORE_MODULE + ".task._task_manager", "_TaskManager")  # type: ignore
        return _TaskManager

    @classmethod
    def _has_enterprise(cls) -> bool:
        return util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None
