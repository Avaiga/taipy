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

from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory

repositories = {
    "scenario": _ScenarioManagerFactory._build_repository,
    "pipeline": _PipelineManagerFactory._build_repository,
    "task": _TaskManagerFactory._build_repository,
    "data": _DataManagerFactory._build_repository,
    "cycle": _CycleManagerFactory._build_repository,
}


def _to_model(repository, entity, **kwargs):
    return repositories[repository](**kwargs)._to_model(entity)
