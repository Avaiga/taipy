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

import pytest

from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.pipeline.pipeline_id import PipelineId
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task
from src.taipy.core.task.task_id import TaskId
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def init_managers():
    _ScenarioManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()


def test_set_and_get_pipeline(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()
    _OrchestratorFactory._build_dispatcher()

    input_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    output_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    task = Task("task", {}, print, [input_dn], [output_dn], TaskId("task_id"))

    scenario = Scenario("scenario", set([task]), {}, set())
    _ScenarioManager._set(scenario)

    pipeline_name_1 = "p1"
    pipeline_id_1 = PipelineId(f"PIPELINE_{pipeline_name_1}_{scenario.id}")
    pipeline_name_2 = "p2"
    pipeline_id_2 = PipelineId(f"PIPELINE_{pipeline_name_2}_{scenario.id}")

    # No existing Pipeline
    assert _PipelineManager._get(pipeline_id_1) is None
    assert _PipelineManager._get(pipeline_id_2) is None

    scenario.add_pipelines({pipeline_name_1: {"tasks": []}})
    pipeline_1 = scenario.pipelines[pipeline_name_1]

    # Save one pipeline. We expect to have only one pipeline stored
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2) is None

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    _TaskManager._set(task)
    scenario.add_pipelines({pipeline_name_2: {"tasks": [task]}})
    pipeline_2 = scenario.pipelines[pipeline_name_2]
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1

    # We save the first pipeline again. We expect nothing to change
    scenario.add_pipelines({pipeline_name_1: {}})
    pipeline_1 = scenario.pipelines[pipeline_name_1]
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    scenario.add_pipelines({pipeline_name_1: {"tasks": [task]}})
    pipeline_3 = scenario.pipelines[pipeline_name_1]
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_3.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 1
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 1
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task.id).id == task.id


def test_get_all_on_multiple_versions_environment(init_sql_repo):
    init_managers()

    # Create 5 pipelines from Scenario with 2 versions each
    for version in range(1, 3):
        for i in range(5):
            _ScenarioManager._set(
                Scenario(
                    f"config_id_{i+version}",
                    [],
                    {},
                    [],
                    f"id_{i}_v{version}",
                    version=f"{version}.0",
                    pipelines={"pipeline": {}},
                )
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0

    _VersionManager._set_experiment_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v2"}])) == 1

    _VersionManager._set_development_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v2"}])) == 0

    _VersionManager._set_development_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v2"}])) == 1


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_hard_delete_one_single_pipeline_with_scenario_data_nodes(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", tasks, {}, pipelines={"pipeline": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    pipeline = scenario.pipelines["pipeline"]
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_one_single_pipeline_with_cycle_data_nodes(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", tasks, {}, pipelines={"pipeline": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    pipeline = scenario.pipelines["pipeline"]
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_shared_entities(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)

    _OrchestratorFactory._build_dispatcher()

    tasks_scenario_1 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_1")
    tasks_scenario_2 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_2")

    scenario_1 = Scenario("scenario_1", tasks_scenario_1, {}, pipelines={"pipeline": {"tasks": tasks_scenario_1}})
    scenario_2 = Scenario("scenario_2", tasks_scenario_2, {}, pipelines={"pipeline": {"tasks": tasks_scenario_2}})
    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)
    pipeline_1 = scenario_1.pipelines["pipeline"]
    pipeline_2 = scenario_2.pipelines["pipeline"]

    _PipelineManager._submit(pipeline_1.id)
    _PipelineManager._submit(pipeline_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
    _PipelineManager._hard_delete(pipeline_1.id)
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
