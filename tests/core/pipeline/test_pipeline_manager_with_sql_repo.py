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

from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.common.alias import PipelineId, TaskId
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def init_managers():
    _ScenarioManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()


def test_set_and_get_pipeline():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()
    _SchedulerFactory._build_dispatcher()

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
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


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data():
    # only create intermediate data node once
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.configure_pipeline("by_6", [task_config_mult_by_two, task_config_mult_by_3])
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6

    _SchedulerFactory._build_dispatcher()

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


def test_do_not_recreate_existing_pipeline_except_same_config():
    Config.configure_global_app(repository_type="sql")
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

    dn_input_config_scope_pipeline_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_global_4 = Config.configure_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.configure_task(
        "task_config_4", print, dn_input_config_scope_pipeline_4, dn_output_config_scope_global_4
    )
    pipeline_config_4 = Config.configure_pipeline("pipeline_config_4", [task_config_4])

    # Scope is global and pipeline
    pipeline_12 = _PipelineManager._get_or_create(pipeline_config_4)
    assert len(_PipelineManager._get_all()) == 6
    pipeline_13 = _PipelineManager._get_or_create(pipeline_config_4)  # Create a new pipeline because new pipeline ID
    assert len(_PipelineManager._get_all()) == 7
    assert pipeline_12.id != pipeline_13.id
    pipeline_14 = _PipelineManager._get_or_create(pipeline_config_4, None, "another_new_scenario_2")
    assert len(_PipelineManager._get_all()) == 8
    assert pipeline_14.id != pipeline_12.id
    assert pipeline_14.id != pipeline_13.id
    pipeline_15 = _PipelineManager._get_or_create(
        pipeline_config_4, None, "another_new_scenario_2"
    )  # Don't create because scope is pipeline
    assert len(_PipelineManager._get_all()) == 9
    assert pipeline_15.id != pipeline_14.id
    assert pipeline_15.id != pipeline_13.id
    assert pipeline_15.id != pipeline_12.id

    dn_input_config_scope_pipeline_5 = Config.configure_data_node("my_input_5", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_scenario_5 = Config.configure_data_node("my_output_5", "in_memory", scope=Scope.SCENARIO)
    task_config_5 = Config.configure_task(
        "task_config_5", print, dn_input_config_scope_pipeline_5, dn_output_config_scope_scenario_5
    )
    pipeline_config_5 = Config.configure_pipeline("pipeline_config_5", [task_config_5])

    # Scope is scenario and pipeline
    pipeline_16 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 10
    pipeline_17 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 11
    assert pipeline_16.id != pipeline_17.id
    pipeline_18 = _PipelineManager._get_or_create(
        pipeline_config_5, None, "random_scenario"
    )  # Create because scope is pipeline
    assert len(_PipelineManager._get_all()) == 12
    assert pipeline_18.id != pipeline_17.id
    assert pipeline_18.id != pipeline_16.id

    # create a second pipeline from the same config
    dn_input_config_scope_pipeline_6 = Config.configure_data_node("my_input_6", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_pipeline_6 = Config.configure_data_node("my_output_6", "in_memory", scope=Scope.PIPELINE)
    task_config_6 = Config.configure_task(
        "task_config_6", print, dn_input_config_scope_pipeline_6, dn_output_config_scope_pipeline_6
    )
    pipeline_config_6 = Config.configure_pipeline("pipeline_config_6", [task_config_6])

    pipeline_19 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 13
    pipeline_20 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 14
    assert pipeline_19.id != pipeline_20.id

    dn_input_config_scope_pipeline_7 = Config.configure_data_node("my_input_7", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_global_7 = Config.configure_data_node("my_output_7", "in_memory", scope=Scope.GLOBAL)
    task_config_7 = Config.configure_task(
        "task_config_7", print, dn_input_config_scope_pipeline_7, dn_output_config_scope_global_7
    )
    pipeline_config_7 = Config.configure_pipeline("pipeline_config_7", [task_config_7])

    # Scope is global and cycle
    pipeline_21 = _PipelineManager._get_or_create(pipeline_config_7)
    assert len(_PipelineManager._get_all()) == 15
    pipeline_22 = _PipelineManager._get_or_create(pipeline_config_7)
    assert len(_PipelineManager._get_all()) == 15
    assert pipeline_21.id == pipeline_22.id
    pipeline_23 = _PipelineManager._get_or_create(pipeline_config_7, "cycle")
    assert len(_PipelineManager._get_all()) == 16
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_22.id != pipeline_23.id

    pipeline_24 = _PipelineManager._get_or_create(pipeline_config_7, None, "scenario")
    assert len(_PipelineManager._get_all()) == 16
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_22.id != pipeline_23.id
    assert pipeline_22.id == pipeline_24.id

    pipeline_25 = _PipelineManager._get_or_create(pipeline_config_7, "cycle", "scenario")
    assert len(_PipelineManager._get_all()) == 16
    assert pipeline_21.id == pipeline_22.id
    assert pipeline_22.id != pipeline_23.id
    assert pipeline_22.id == pipeline_24.id
    assert pipeline_22.id != pipeline_25.id
    assert pipeline_23.id == pipeline_25.id

    dn_input_config_scope_pipeline_8 = Config.configure_data_node("my_input_8", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_scenario_8 = Config.configure_data_node("my_output_8", "in_memory", scope=Scope.SCENARIO)
    task_config_8 = Config.configure_task(
        "task_config_8", print, dn_input_config_scope_pipeline_8, dn_output_config_scope_scenario_8
    )
    pipeline_config_8 = Config.configure_pipeline("pipeline_config_8", [task_config_8])

    pipeline_26 = _PipelineManager._get_or_create(pipeline_config_8)
    assert len(_PipelineManager._get_all()) == 17
    pipeline_27 = _PipelineManager._get_or_create(pipeline_config_8)
    assert len(_PipelineManager._get_all()) == 17
    assert pipeline_26.id == pipeline_27.id
    pipeline_28 = _PipelineManager._get_or_create(pipeline_config_8, None, "random_scenario")
    assert len(_PipelineManager._get_all()) == 18
    assert pipeline_28.id != pipeline_27.id
    assert pipeline_28.id != pipeline_26.id
    pipeline_29 = _PipelineManager._get_or_create(pipeline_config_8, "a_cycle", "random_scenario")
    assert len(_PipelineManager._get_all()) == 18
    assert pipeline_29.id != pipeline_27.id
    assert pipeline_29.id != pipeline_26.id
    assert pipeline_29.id == pipeline_28.id

    dn_input_config_scope_pipeline_9 = Config.configure_data_node("my_input_9", "in_memory", scope=Scope.CYCLE)
    dn_output_config_scope_pipeline_9 = Config.configure_data_node("my_output_9", "in_memory", scope=Scope.CYCLE)
    task_config_9 = Config.configure_task(
        "task_config_9", print, dn_input_config_scope_pipeline_9, dn_output_config_scope_pipeline_9
    )
    pipeline_config_9 = Config.configure_pipeline("pipeline_config_9", [task_config_9])

    pipeline_30 = _PipelineManager._get_or_create(pipeline_config_9)
    assert len(_PipelineManager._get_all()) == 19
    pipeline_31 = _PipelineManager._get_or_create(pipeline_config_9)
    assert len(_PipelineManager._get_all()) == 19
    assert pipeline_30.id == pipeline_31.id
    pipeline_32 = _PipelineManager._get_or_create(pipeline_config_9, "a_cycle", None)
    assert len(_PipelineManager._get_all()) == 20
    assert pipeline_30.id == pipeline_31.id
    assert pipeline_30.id != pipeline_32.id
    assert pipeline_31.id != pipeline_32.id
    pipeline_33 = _PipelineManager._get_or_create(pipeline_config_9, None, "a_scenario")
    assert len(_PipelineManager._get_all()) == 20
    assert pipeline_30.id == pipeline_31.id
    assert pipeline_30.id != pipeline_32.id
    assert pipeline_31.id != pipeline_32.id
    assert pipeline_33.id != pipeline_32.id
    assert pipeline_30.id == pipeline_33.id
    pipeline_34 = _PipelineManager._get_or_create(pipeline_config_9, "a_cycle", "a_scenario")
    assert len(_PipelineManager._get_all()) == 20
    assert pipeline_30.id == pipeline_31.id
    assert pipeline_30.id != pipeline_32.id
    assert pipeline_31.id != pipeline_32.id
    assert pipeline_33.id != pipeline_32.id
    assert pipeline_32.id == pipeline_34.id
    assert pipeline_33.id != pipeline_34.id

    dn_input_config_scope_pipeline_10 = Config.configure_data_node("my_input_10", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_scenario_10 = Config.configure_data_node("my_output_10", "in_memory", scope=Scope.CYCLE)
    task_config_10 = Config.configure_task(
        "task_config_10", print, dn_input_config_scope_pipeline_10, dn_output_config_scope_scenario_10
    )
    pipeline_config_10 = Config.configure_pipeline("pipeline_config_10", [task_config_10])

    pipeline_35 = _PipelineManager._get_or_create(pipeline_config_10)
    assert len(_PipelineManager._get_all()) == 21
    pipeline_36 = _PipelineManager._get_or_create(pipeline_config_10)
    assert len(_PipelineManager._get_all()) == 22
    assert pipeline_35.id != pipeline_36.id
    pipeline_37 = _PipelineManager._get_or_create(pipeline_config_10, "random_cycle")
    assert len(_PipelineManager._get_all()) == 23
    assert pipeline_35.id != pipeline_36.id
    assert pipeline_36.id != pipeline_37.id
    assert pipeline_35.id != pipeline_37.id


def test_hard_delete_one_single_pipeline_with_pipeline_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node(
        "my_output", "in_memory", scope=Scope.PIPELINE, default_data="works !"
    )
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _SchedulerFactory._build_dispatcher()

    pipeline = _PipelineManager._get_or_create(pipeline_config)
    _PipelineManager._submit(pipeline.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1

    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_single_pipeline_with_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _SchedulerFactory._build_dispatcher()

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


def test_hard_delete_one_single_pipeline_with_cycle_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _SchedulerFactory._build_dispatcher()

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


def test_hard_delete_one_single_pipeline_with_pipeline_and_global_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _SchedulerFactory._build_dispatcher()

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
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_pipeline_among_two_with_pipeline_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])

    _SchedulerFactory._build_dispatcher()

    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
    _PipelineManager._submit(pipeline_1.id)
    _PipelineManager._submit(pipeline_2.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
    assert len(_JobManager._get_all()) == 2
    _PipelineManager._hard_delete(pipeline_1.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_shared_entities():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    Config.configure_global_app(repository_type="sql")

    init_managers()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])

    _SchedulerFactory._build_dispatcher()

    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
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
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
    assert len(_JobManager._get_all()) == 3


def test_data_node_creation_pipeline():
    Config.configure_global_app(repository_type="sql")

    init_managers()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE)
    input_global_dn = Config.configure_data_node("my_global_input", "in_memory", scope=Scope.GLOBAL)
    input_global_dn_2 = Config.configure_data_node("my_global_input_2", "in_memory", scope=Scope.GLOBAL)
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.PIPELINE)
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE)
    task_1 = Config.configure_task("task_1", print, [input_dn, input_global_dn, input_global_dn_2], intermediate_dn)
    task_2 = Config.configure_task("task_2", print, [input_dn, intermediate_dn], output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 8
    assert pipeline_1.my_input.id != pipeline_2.my_input.id
    assert pipeline_1.my_global_input.id == pipeline_2.my_global_input.id
    assert pipeline_1.my_global_input_2.id == pipeline_2.my_global_input_2.id
    assert pipeline_1.my_inter.id != pipeline_2.my_inter.id
    assert pipeline_1.my_output.id != pipeline_2.my_output.id


def test_data_node_creation_scenario():
    Config.configure_global_app(repository_type="sql")

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
