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

from taipy.core.cycle._cycle_repository_factory import _CycleRepositoryFactory
from taipy.core.data._data_repository_factory import _DataRepositoryFactory
from taipy.core.pipeline._pipeline_repository_factory import _PipelineRepositoryFactory
from taipy.core.scenario._scenario_repository_factory import _ScenarioRepositoryFactory
from taipy.core.task._task_repository_factory import _TaskRepositoryFactory

repositories = {
    "scenario": _ScenarioRepositoryFactory._build_repository,
    "pipeline": _PipelineRepositoryFactory._build_repository,
    "task": _TaskRepositoryFactory._build_repository,
    "data": _DataRepositoryFactory._build_repository,
    "cycle": _CycleRepositoryFactory._build_repository,
}


def _to_model(repository, entity, **kwargs):
    return repositories[repository](**kwargs)._to_model(entity)
