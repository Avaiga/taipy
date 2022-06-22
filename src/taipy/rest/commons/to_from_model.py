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

from taipy.core.cycle._cycle_repository import _CycleRepository
from taipy.core.data._data_repository import _DataRepository
from taipy.core.pipeline._pipeline_repository import _PipelineRepository
from taipy.core.scenario._scenario_repository import _ScenarioRepository
from taipy.core.task._task_repository import _TaskRepository

repositories = {
    "scenario": _ScenarioRepository,
    "pipeline": _PipelineRepository,
    "task": _TaskRepository,
    "data": _DataRepository,
    "cycle": _CycleRepository,
}


def _to_model(repository, entity, **kwargs):
    return repositories[repository](**kwargs)._to_model(entity)
