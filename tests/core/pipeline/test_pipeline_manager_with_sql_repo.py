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

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_2 = Task("task", {}, print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = Pipeline("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    assert _PipelineManager._get(pipeline_id_1) is None
    assert _PipelineManager._get(pipeline_1) is None
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save one pipeline. We expect to have only one pipeline stored
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    _TaskManager._set(task_2)
    _PipelineManager._set(pipeline_2)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save the first pipeline again. We expect nothing to change
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    _PipelineManager._set(pipeline_3_with_same_id)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_3_with_same_id.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_3_with_same_id.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


def test_get_all_on_multiple_versions_environment(init_sql_repo):
    init_managers()

    # Create 5 pipelines with 2 versions each
    # Only version 1.0 has the pipeline with config_id = "config_id_1"
    # Only version 2.0 has the pipeline with config_id = "config_id_6"
    for version in range(1, 3):
        for i in range(5):
            _PipelineManager._set(
                Pipeline(f"config_id_{i+version}", {}, [], PipelineId(f"id{i}_v{version}"), version=f"{version}.0")
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_experiment_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1

    _VersionManager._set_development_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_development_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data(init_sql_repo):
    # only create intermediate data node once
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.SCENARIO, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.configure_pipeline("by_6", [task_config_mult_by_two, task_config_mult_by_3])
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6

    _OrchestratorFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0

    pipeline = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 2
    assert len(pipeline._get_sorted_tasks()) == 2
    assert pipeline.foo.read() == 1
    assert pipeline.bar.read() == 0
    assert pipeline.baz.read() == 0
    assert pipeline._get_sorted_tasks()[0][0].config_id == task_config_mult_by_two.id
    assert pipeline._get_sorted_tasks()[1][0].config_id == task_config_mult_by_3.id

    _PipelineManager._submit(pipeline.id)
    assert pipeline.foo.read() == 1
    assert pipeline.bar.read() == 2
    assert pipeline.baz.read() == 6

    pipeline.foo.write("new data value")
    assert pipeline.foo.read() == "new data value"
    assert pipeline.bar.read() == 2
    assert pipeline.baz.read() == 6

    pipeline.bar.write(7)
    assert pipeline.foo.read() == "new data value"
    assert pipeline.bar.read() == 7
    assert pipeline.baz.read() == 6

    with pytest.raises(AttributeError):
        pipeline.WRONG.write(7)


def test_do_not_recreate_existing_pipeline_except_same_config(init_sql_repo):
    init_managers()

    dn_input_config_scope_scenario = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_scenario = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task(
        "task_config", print, dn_input_config_scope_scenario, dn_output_config_scope_scenario
    )
    pipeline_config = Config.configure_pipeline("pipeline_config_1", [task_config])

    # Scope is scenario
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    print(_PipelineManager._repository)
    print(_TaskManager._repository)
    print(_DataManager._repository)
    assert len(_PipelineManager._get_all()) == 1
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
    assert len(_PipelineManager._get_all()) == 1
    assert pipeline_1.id == pipeline_2.id
    pipeline_3 = _PipelineManager._get_or_create(
        pipeline_config, None, "a_scenario"
    )  # Create even if the config is the same
    assert len(_PipelineManager._get_all()) == 2
    assert pipeline_1.id == pipeline_2.id
    assert pipeline_3.id != pipeline_1.id
    assert pipeline_3.id != pipeline_2.id
    pipeline_4 = _PipelineManager._get_or_create(
        pipeline_config, None, "a_scenario"
    )  # Do not create because existed pipeline
    assert len(_PipelineManager._get_all()) == 2
    assert pipeline_3.id == pipeline_4.id

    dn_input_config_scope_scenario_2 = Config.configure_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_global_2 = Config.configure_data_node("my_output_2", "in_memory", scope=Scope.GLOBAL)
    task_config_2 = Config.configure_task(
        "task_config_2", print, dn_input_config_scope_scenario_2, dn_output_config_scope_global_2
    )
    pipeline_config_2 = Config.configure_pipeline("pipeline_config_2", [task_config_2])

    # Scope is scenario and global
    pipeline_5 = _PipelineManager._get_or_create(pipeline_config_2)
    assert len(_PipelineManager._get_all()) == 3
    pipeline_6 = _PipelineManager._get_or_create(pipeline_config_2)
    assert len(_PipelineManager._get_all()) == 3
    assert pipeline_5.id == pipeline_6.id
    pipeline_7 = _PipelineManager._get_or_create(pipeline_config_2, None, "another_scenario")
    assert len(_PipelineManager._get_all()) == 4
    assert pipeline_7.id != pipeline_6.id
    assert pipeline_7.id != pipeline_5.id
    pipeline_8 = _PipelineManager._get_or_create(pipeline_config_2, None, "another_scenario")
    assert len(_PipelineManager._get_all()) == 4
    assert pipeline_7.id == pipeline_8.id

    dn_input_config_scope_global_3 = Config.configure_data_node("my_input_3", "in_memory", scope=Scope.GLOBAL)
    dn_output_config_scope_global_3 = Config.configure_data_node("my_output_3", "in_memory", scope=Scope.GLOBAL)
    task_config_3 = Config.configure_task(
        "task_config_3", print, dn_input_config_scope_global_3, dn_output_config_scope_global_3
    )
    pipeline_config_3 = Config.configure_pipeline("pipeline_config_3", [task_config_3])

    # Scope is global
    pipeline_9 = _PipelineManager._get_or_create(pipeline_config_3)
    assert len(_PipelineManager._get_all()) == 5
    pipeline_10 = _PipelineManager._get_or_create(pipeline_config_3)
    assert len(_PipelineManager._get_all()) == 5
    assert pipeline_9.id == pipeline_10.id
    pipeline_11 = _PipelineManager._get_or_create(
        pipeline_config_3, None, "another_new_scenario"
    )  # Do not create because scope is global
    assert len(_PipelineManager._get_all()) == 5
    assert pipeline_11.id == pipeline_10.id
    assert pipeline_11.id == pipeline_9.id

    dn_input_config_scope_pipeline_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_global_4 = Config.configure_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.configure_task(
        "task_config_4", print, dn_input_config_scope_pipeline_4, dn_output_config_scope_global_4
    )
    pipeline_config_4 = Config.configure_pipeline("pipeline_config_4", [task_config_4])

    # Scope is global and cycle
    pipeline_12 = _PipelineManager._get_or_create(pipeline_config_4)
    assert len(_PipelineManager._get_all()) == 6
    pipeline_13 = _PipelineManager._get_or_create(pipeline_config_4)
    assert len(_PipelineManager._get_all()) == 6
    assert pipeline_12.id == pipeline_13.id
    pipeline_14 = _PipelineManager._get_or_create(pipeline_config_4, "cycle")
    assert len(_PipelineManager._get_all()) == 7
    assert pipeline_12.id == pipeline_13.id
    assert pipeline_13.id != pipeline_14.id

    pipeline_15 = _PipelineManager._get_or_create(pipeline_config_4, None, "scenario")
    assert len(_PipelineManager._get_all()) == 7
    assert pipeline_12.id == pipeline_13.id
    assert pipeline_13.id != pipeline_14.id
    assert pipeline_13.id == pipeline_15.id

    pipeline_16 = _PipelineManager._get_or_create(pipeline_config_4, "cycle", "scenario")
    assert len(_PipelineManager._get_all()) == 7
    assert pipeline_12.id == pipeline_13.id
    assert pipeline_13.id != pipeline_14.id
    assert pipeline_13.id == pipeline_15.id
    assert pipeline_13.id != pipeline_16.id
    assert pipeline_14.id == pipeline_16.id

    dn_input_config_scope_pipeline_5 = Config.configure_data_node("my_input_5", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_scenario_5 = Config.configure_data_node("my_output_5", "in_memory", scope=Scope.SCENARIO)
    task_config_5 = Config.configure_task(
        "task_config_5", print, dn_input_config_scope_pipeline_5, dn_output_config_scope_scenario_5
    )
    pipeline_config_5 = Config.configure_pipeline("pipeline_config_8", [task_config_5])

    pipeline_17 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 8
    pipeline_18 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 8
    assert pipeline_17.id == pipeline_18.id
    pipeline_19 = _PipelineManager._get_or_create(pipeline_config_5, None, "random_scenario")
    assert len(_PipelineManager._get_all()) == 9
    assert pipeline_19.id != pipeline_18.id
    assert pipeline_19.id != pipeline_17.id
    pipeline_20 = _PipelineManager._get_or_create(pipeline_config_5, "a_cycle", "random_scenario")
    assert len(_PipelineManager._get_all()) == 9
    assert pipeline_20.id != pipeline_18.id
    assert pipeline_20.id != pipeline_17.id
    assert pipeline_20.id == pipeline_19.id

    dn_input_config_scope_pipeline_6 = Config.configure_data_node("my_input_6", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_pipeline_6 = Config.configure_data_node("my_output_6", "in_memory", scope=Scope.CYCLE)
    task_config_6 = Config.configure_task(
        "task_config_9", print, dn_input_config_scope_pipeline_6, dn_output_config_scope_pipeline_6
    )
    pipeline_config_6 = Config.configure_pipeline("pipeline_config_9", [task_config_6])

    pipeline_21 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 10
    pipeline_22 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 10
    assert pipeline_21.id == pipeline_22.id
    pipeline_23 = _PipelineManager._get_or_create(pipeline_config_6, "a_cycle", None)
    assert len(_PipelineManager._get_all()) == 11
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_21.id != pipeline_23.id
    assert pipeline_22.id != pipeline_23.id
    pipeline_24 = _PipelineManager._get_or_create(pipeline_config_6, None, "a_scenario")
    assert len(_PipelineManager._get_all()) == 11
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_21.id != pipeline_23.id
    assert pipeline_22.id != pipeline_23.id
    assert pipeline_24.id != pipeline_23.id
    assert pipeline_21.id == pipeline_24.id
    pipeline_25 = _PipelineManager._get_or_create(pipeline_config_6, "a_cycle", "a_scenario")
    assert len(_PipelineManager._get_all()) == 11
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_21.id != pipeline_23.id
    assert pipeline_22.id != pipeline_23.id
    assert pipeline_24.id != pipeline_23.id
    assert pipeline_23.id == pipeline_25.id
    assert pipeline_24.id != pipeline_25.id


def test_hard_delete_one_single_pipeline_with_scenario_data_nodes(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _OrchestratorFactory._build_dispatcher()

    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
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
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _OrchestratorFactory._build_dispatcher()

    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
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
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])

    _OrchestratorFactory._build_dispatcher()

    pipeline_1 = _PipelineManager._get_or_create(pipeline_config, scenario_id="scenario_id_1")
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config, scenario_id="scenario_id_2")
    _PipelineManager._submit(pipeline_1.id)
    _PipelineManager._submit(pipeline_2.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
    _PipelineManager._hard_delete(pipeline_1.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4


def test_data_node_creation_scenario(init_sql_repo):
    init_managers()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    input_global_dn = Config.configure_data_node("my_global_input", "in_memory", scope=Scope.GLOBAL)
    input_global_dn_2 = Config.configure_data_node("my_global_input_2", "in_memory", scope=Scope.GLOBAL)
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.SCENARIO)
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_1 = Config.configure_task("task_1", print, [input_dn, input_global_dn, input_global_dn_2], intermediate_dn)
    task_2 = Config.configure_task("task_2", print, [input_dn, intermediate_dn], output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 5
    assert pipeline_1.my_input.id == pipeline_2.my_input.id
    assert pipeline_1.my_global_input.id == pipeline_2.my_global_input.id
    assert pipeline_1.my_global_input_2.id == pipeline_2.my_global_input_2.id
    assert pipeline_1.my_inter.id == pipeline_2.my_inter.id
    assert pipeline_1.my_output.id == pipeline_2.my_output.id


def test_get_pipelines_by_config_id(init_sql_repo):
    init_managers()

    dn_config = Config.configure_data_node("dn", scope=Scope.SCENARIO)
    task_config = Config.configure_task("t", print, dn_config)
    pipeline_config_1 = Config.configure_pipeline("p1", task_configs=task_config)
    pipeline_config_2 = Config.configure_pipeline("p2", task_configs=task_config)
    pipeline_config_3 = Config.configure_pipeline("p3", task_configs=task_config)

    p_1_1 = _PipelineManager._get_or_create(pipeline_config_1, scenario_id="scenario_1")
    p_1_2 = _PipelineManager._get_or_create(pipeline_config_1, scenario_id="scenario_2")
    p_1_3 = _PipelineManager._get_or_create(pipeline_config_1, scenario_id="scenario_3")
    assert len(_PipelineManager._get_all()) == 3

    p_2_1 = _PipelineManager._get_or_create(pipeline_config_2, scenario_id="scenario_4")
    p_2_2 = _PipelineManager._get_or_create(pipeline_config_2, scenario_id="scenario_5")
    assert len(_PipelineManager._get_all()) == 5

    p_3_1 = _PipelineManager._get_or_create(pipeline_config_3, scenario_id="scenario_6")
    assert len(_PipelineManager._get_all()) == 6

    p1_pipelines = _PipelineManager._get_by_config_id(pipeline_config_1.id)
    assert len(p1_pipelines) == 3
    assert sorted([p_1_1.id, p_1_2.id, p_1_3.id]) == sorted([pipeline.id for pipeline in p1_pipelines])

    p2_pipelines = _PipelineManager._get_by_config_id(pipeline_config_2.id)
    assert len(p2_pipelines) == 2
    assert sorted([p_2_1.id, p_2_2.id]) == sorted([pipeline.id for pipeline in p2_pipelines])

    p3_pipelines = _PipelineManager._get_by_config_id(pipeline_config_3.id)
    assert len(p3_pipelines) == 1
    assert sorted([p_3_1.id]) == sorted([pipeline.id for pipeline in p3_pipelines])
