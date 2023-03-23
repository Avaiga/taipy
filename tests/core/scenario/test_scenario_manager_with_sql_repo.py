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

from datetime import datetime, timedelta

import pytest

from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import DeletingPrimaryScenario
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def init_managers():
    _CycleManagerFactory._build_manager()._delete_all()
    _ScenarioManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()


def test_set_and_get_scenario(cycle):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()
    _OrchestratorFactory._build_dispatcher()

    scenario_id_1 = ScenarioId("scenario_id_1")
    scenario_1 = Scenario("scenario_name_1", [], {}, scenario_id_1)

    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_name = "task"
    task_2 = Task(task_name, {}, print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_name_2 = "pipeline_name_2"
    pipeline_2 = Pipeline(pipeline_name_2, {}, [task_2], PipelineId("pipeline_id_2"))
    scenario_id_2 = ScenarioId("scenario_id_2")
    scenario_2 = Scenario("scenario_name_2", [pipeline_2], {}, scenario_id_2, datetime.now(), True, cycle)

    pipeline_3 = Pipeline("pipeline_name_3", {}, [], PipelineId("pipeline_id_3"))
    scenario_3_with_same_id = Scenario("scenario_name_3", [pipeline_3], {}, scenario_id_1, datetime.now(), False, cycle)

    # No existing scenario
    assert len(_ScenarioManager._get_all()) == 0
    assert _ScenarioManager._get(scenario_id_1) is None
    assert _ScenarioManager._get(scenario_1) is None
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save one scenario. We expect to have only one scenario stored
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    _TaskManager._set(task_2)
    _PipelineManager._set(pipeline_2)
    _CycleManager._set(cycle)
    _ScenarioManager._set(scenario_2)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _ScenarioManager._get(scenario_id_2).cycle == cycle
    assert _ScenarioManager._get(scenario_2).cycle == cycle
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save the first scenario again. We expect nothing to change
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    _TaskManager._set(scenario_2.pipelines[pipeline_name_2].tasks[task_name])
    _PipelineManager._set(pipeline_3)
    _ScenarioManager._set(scenario_3_with_same_id)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 1
    assert _ScenarioManager._get(scenario_id_1).cycle == cycle
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 1
    assert _ScenarioManager._get(scenario_1).cycle == cycle
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


def test_create_scenario_does_not_modify_config():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    creation_date_1 = datetime.now()
    name_1 = "name_1"
    scenario_config = Config.configure_scenario("sc", [], Frequency.DAILY)

    _OrchestratorFactory._build_dispatcher()

    assert scenario_config.properties.get("name") is None
    assert len(scenario_config.properties) == 0

    scenario = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 1
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario.properties["foo"] = "bar"
    _ScenarioManager._set(scenario)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 2
    assert scenario.properties.get("foo") == "bar"
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1)
    assert scenario_2.name is None


def test_create_and_delete_scenario():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    creation_date_1 = datetime.now()
    creation_date_2 = creation_date_1 + timedelta(minutes=10)

    name_1 = "name_1"

    _ScenarioManager._delete_all()
    assert len(_ScenarioManager._get_all()) == 0

    scenario_config = Config.configure_scenario("sc", [], Frequency.DAILY)

    _OrchestratorFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert scenario_1.config_id == "sc"
    assert scenario_1.pipelines == {}
    assert scenario_1.cycle.frequency == Frequency.DAILY
    assert scenario_1.is_primary
    assert scenario_1.cycle.creation_date == creation_date_1
    assert scenario_1.cycle.start_date.date() == creation_date_1.date()
    assert scenario_1.cycle.end_date.date() == creation_date_1.date()
    assert scenario_1.creation_date == creation_date_1
    assert scenario_1.name == name_1
    assert scenario_1.properties["name"] == name_1
    assert scenario_1.tags == set()

    cycle_id_1 = scenario_1.cycle.id
    assert _CycleManager._get(cycle_id_1).id == cycle_id_1
    _ScenarioManager._delete(scenario_1.id)
    assert _ScenarioManager._get(scenario_1.id) is None
    assert _CycleManager._get(cycle_id_1) is None

    # Recreate scenario_1
    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_2)
    assert scenario_2.config_id == "sc"
    assert scenario_2.pipelines == {}
    assert scenario_2.cycle.frequency == Frequency.DAILY
    assert not scenario_2.is_primary
    assert scenario_2.cycle.creation_date == creation_date_1
    assert scenario_2.cycle.start_date.date() == creation_date_2.date()
    assert scenario_2.cycle.end_date.date() == creation_date_2.date()
    assert scenario_2.properties.get("name") is None
    assert scenario_2.tags == set()

    assert scenario_1 != scenario_2
    assert scenario_1.cycle == scenario_2.cycle

    assert len(_ScenarioManager._get_all()) == 2
    with pytest.raises(DeletingPrimaryScenario):
        _ScenarioManager._delete(
            scenario_1.id,
        )

    _ScenarioManager._delete(
        scenario_2.id,
    )
    assert len(_ScenarioManager._get_all()) == 1
    _ScenarioManager._delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 0


def mult_by_2(nb: int):
    return nb * 2


def test_scenario_manager_only_creates_data_node_once():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_4 = Config.configure_data_node("qux", "in_memory", Scope.PIPELINE, default_data=0)

    task_mult_by_2_config = Config.configure_task("mult_by_2", print, [dn_config_1], dn_config_2)
    task_mult_by_3_config = Config.configure_task("mult_by_3", print, [dn_config_2], dn_config_6)
    task_mult_by_4_config = Config.configure_task("mult_by_4", print, [dn_config_1], dn_config_4)
    pipeline_config_1 = Config.configure_pipeline("by_6", [task_mult_by_2_config, task_mult_by_3_config])
    # dn_1 ---> mult_by_2 ---> dn_2 ---> mult_by_3 ---> dn_6
    pipeline_config_2 = Config.configure_pipeline("by_4", [task_mult_by_4_config])
    # dn_1 ---> mult_by_4 ---> dn_4
    scenario_config = Config.configure_scenario(
        "awesome_scenario", [pipeline_config_1, pipeline_config_2], Frequency.DAILY
    )

    _OrchestratorFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_CycleManager._get_all()) == 0

    scenario = _ScenarioManager._create(scenario_config)

    assert len(_DataManager._get_all()) == 5
    assert len(_TaskManager._get_all()) == 3
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 1
    assert scenario.foo.read() == 1
    assert scenario.bar.read() == 0
    assert scenario.baz.read() == 0
    assert scenario.qux.read() == 0
    assert scenario.by_6._get_sorted_tasks()[0][0].config_id == task_mult_by_2_config.id
    assert scenario.by_6._get_sorted_tasks()[1][0].config_id == task_mult_by_3_config.id
    assert scenario.by_4._get_sorted_tasks()[0][0].config_id == task_mult_by_4_config.id
    assert scenario.cycle.frequency == Frequency.DAILY


def test_scenario_create_from_task_config():
    Config.configure_global_app(repository_type="sql")

    init_managers()

    data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
    data_node_2_config = Config.configure_data_node(
        id="d2", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_3_config = Config.configure_data_node(
        id="d3", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    task_config_1 = Config.configure_task("t1", print, data_node_1_config, data_node_2_config, scope=Scope.GLOBAL)
    task_config_2 = Config.configure_task("t2", print, data_node_2_config, data_node_3_config, scope=Scope.GLOBAL)
    scenario_config_1 = Config.configure_scenario_from_tasks("s1", task_configs=[task_config_1, task_config_2])

    pipeline_name = "p1"
    scenario_config_2 = Config.configure_scenario_from_tasks(
        "s2", task_configs=[task_config_1, task_config_2], pipeline_id=pipeline_name
    )

    _ScenarioManager._submit(_ScenarioManager._create(scenario_config_1))
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(scenario_config_1.pipeline_configs) == 1
    assert len(scenario_config_1.pipeline_configs[0].task_configs) == 2
    # Should create a default pipeline name
    assert isinstance(scenario_config_1.pipeline_configs[0].id, str)
    assert scenario_config_1.pipeline_configs[0].id == f"{scenario_config_1.id}_pipeline"

    _ScenarioManager._submit(_ScenarioManager._create(scenario_config_2))
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert scenario_config_2.pipeline_configs[0].id == pipeline_name
