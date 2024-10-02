# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import uuid
from unittest import mock

import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._version._version_manager import _VersionManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.exceptions.exceptions import ModelNotFound, NonExistingTask
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_id import TaskId


def test_create_and_save():
    input_configs = [Config.configure_data_node("my_input", "in_memory")]
    output_configs = Config.configure_data_node("my_output", "in_memory")
    task_config = Config.configure_task("foo", print, input_configs, output_configs)
    task = _create_task_from_config(task_config)
    assert task.id is not None
    assert task.config_id == "foo"
    assert len(task.input) == 1
    assert len(_DataManager._get_all()) == 2
    assert task.my_input.id is not None
    assert task.my_input.config_id == "my_input"
    assert task.my_output.id is not None
    assert task.my_output.config_id == "my_output"
    assert task.function == print
    assert task.parent_ids == set()

    task_retrieved_from_manager = _TaskManager._get(task.id)
    assert task_retrieved_from_manager.id == task.id
    assert task_retrieved_from_manager.config_id == task.config_id
    assert len(task_retrieved_from_manager.input) == len(task.input)
    assert task_retrieved_from_manager.my_input.id is not None
    assert task_retrieved_from_manager.my_input.config_id == task.my_input.config_id
    assert task_retrieved_from_manager.my_output.id is not None
    assert task_retrieved_from_manager.my_output.config_id == task.my_output.config_id
    assert task_retrieved_from_manager.function == task.function
    assert task_retrieved_from_manager.parent_ids == set()


def test_do_not_recreate_existing_data_node():
    input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)

    _DataManager._create_and_set(input_config, "scenario_id", "task_id")
    assert len(_DataManager._get_all()) == 1

    task_config = Config.configure_task("foo", print, input_config, output_config)
    _create_task_from_config(task_config, scenario_id="scenario_id")
    assert len(_DataManager._get_all()) == 2


def test_assign_task_as_parent_of_datanode():
    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.SCENARIO)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.SCENARIO)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("task_1", print, dn_config_1, dn_config_2)
    task_config_2 = Config.configure_task("task_2", print, dn_config_2, dn_config_3)
    tasks = _TaskManager._bulk_get_or_create([task_config_1, task_config_2], "cycle_id", "scenario_id")

    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 2
    assert len(tasks) == 2

    dns = {dn.config_id: dn for dn in _DataManager._get_all()}
    assert dns["dn_1"].parent_ids == {tasks[0].id}
    assert dns["dn_2"].parent_ids == {tasks[0].id, tasks[1].id}
    assert dns["dn_3"].parent_ids == {tasks[1].id}


def test_do_not_recreate_existing_task():
    input_config_scope_scenario = Config.configure_data_node("my_input_1", "in_memory", Scope.SCENARIO)
    output_config_scope_scenario = Config.configure_data_node("my_output_1", "in_memory", Scope.SCENARIO)
    task_config_1 = Config.configure_task("bar", print, input_config_scope_scenario, output_config_scope_scenario)
    # task_config_2 scope is Scenario

    task_1 = _create_task_from_config(task_config_1)
    assert len(_TaskManager._get_all()) == 1
    task_2 = _create_task_from_config(task_config_1)  # Do not create. It already exists for None scenario
    assert len(_TaskManager._get_all()) == 1
    assert task_1.id == task_2.id
    task_3 = _create_task_from_config(task_config_1, None, None)  # Do not create. It already exists for None scenario
    assert len(_TaskManager._get_all()) == 1
    assert task_1.id == task_2.id
    assert task_2.id == task_3.id
    task_4 = _create_task_from_config(task_config_1, None, "scenario_1")  # Create even if sequence is the same.
    assert len(_TaskManager._get_all()) == 2
    assert task_1.id == task_2.id
    assert task_2.id == task_3.id
    assert task_3.id != task_4.id
    task_5 = _create_task_from_config(
        task_config_1, None, "scenario_1"
    )  # Do not create. It already exists for scenario_1
    assert len(_TaskManager._get_all()) == 2
    assert task_1.id == task_2.id
    assert task_2.id == task_3.id
    assert task_3.id != task_4.id
    assert task_4.id == task_5.id
    task_6 = _create_task_from_config(task_config_1, None, "scenario_2")
    assert len(_TaskManager._get_all()) == 3
    assert task_1.id == task_2.id
    assert task_2.id == task_3.id
    assert task_3.id != task_4.id
    assert task_4.id == task_5.id
    assert task_5.id != task_6.id
    assert task_3.id != task_6.id

    input_config_scope_cycle = Config.configure_data_node("my_input_2", "in_memory", Scope.CYCLE)
    output_config_scope_cycle = Config.configure_data_node("my_output_2", "in_memory", Scope.CYCLE)
    task_config_2 = Config.configure_task("xyz", print, input_config_scope_cycle, output_config_scope_cycle)
    # task_config_3 scope is Cycle

    task_7 = _create_task_from_config(task_config_2)
    assert len(_TaskManager._get_all()) == 4
    task_8 = _create_task_from_config(task_config_2)  # Do not create. It already exists for None cycle
    assert len(_TaskManager._get_all()) == 4
    assert task_7.id == task_8.id
    task_9 = _create_task_from_config(task_config_2, None, None)  # Do not create. It already exists for None cycle
    assert len(_TaskManager._get_all()) == 4
    assert task_7.id == task_8.id
    assert task_8.id == task_9.id
    task_10 = _create_task_from_config(
        task_config_2, None, "scenario"
    )  # Do not create. It already exists for None cycle
    assert len(_TaskManager._get_all()) == 4
    assert task_7.id == task_8.id
    assert task_8.id == task_9.id
    assert task_9.id == task_10.id
    task_11 = _create_task_from_config(
        task_config_2, None, "scenario"
    )  # Do not create. It already exists for None cycle
    assert len(_TaskManager._get_all()) == 4
    assert task_7.id == task_8.id
    assert task_8.id == task_9.id
    assert task_9.id == task_10.id
    assert task_10.id == task_11.id
    task_12 = _create_task_from_config(task_config_2, "cycle", None)
    assert len(_TaskManager._get_all()) == 5
    assert task_7.id == task_8.id
    assert task_8.id == task_9.id
    assert task_9.id == task_10.id
    assert task_10.id == task_11.id
    assert task_11.id != task_12.id
    task_13 = _create_task_from_config(task_config_2, "cycle", None)
    assert len(_TaskManager._get_all()) == 5
    assert task_7.id == task_8.id
    assert task_8.id == task_9.id
    assert task_9.id == task_10.id
    assert task_10.id == task_11.id
    assert task_11.id != task_12.id
    assert task_12.id == task_13.id


def test_set_and_get_task():
    task_id_1 = TaskId("id1")
    first_task = Task("name_1", {}, print, [], [], task_id_1)
    task_id_2 = TaskId("id2")
    second_task = Task("name_2", {}, print, [], [], task_id_2)
    third_task_with_same_id_as_first_task = Task("name_is_not_1_anymore", {}, print, [], [], task_id_1)

    # No task at initialization

    assert len(_TaskManager._get_all()) == 0
    assert _TaskManager._get(task_id_1) is None
    assert _TaskManager._get(first_task) is None
    assert _TaskManager._get(task_id_2) is None
    assert _TaskManager._get(second_task) is None

    # Save one task. We expect to have only one task stored
    _TaskManager._set(first_task)
    assert len(_TaskManager._get_all()) == 1
    assert _TaskManager._get(task_id_1).id == first_task.id
    assert _TaskManager._get(first_task).id == first_task.id
    assert _TaskManager._get(task_id_2) is None
    assert _TaskManager._get(second_task) is None

    # Save a second task. Now, we expect to have a total of two tasks stored
    _TaskManager._set(second_task)
    assert len(_TaskManager._get_all()) == 2
    assert _TaskManager._get(task_id_1).id == first_task.id
    assert _TaskManager._get(first_task).id == first_task.id
    assert _TaskManager._get(task_id_2).id == second_task.id
    assert _TaskManager._get(second_task).id == second_task.id

    # We save the first task again. We expect nothing to change
    _TaskManager._set(first_task)
    assert len(_TaskManager._get_all()) == 2
    assert _TaskManager._get(task_id_1).id == first_task.id
    assert _TaskManager._get(first_task).id == first_task.id
    assert _TaskManager._get(task_id_2).id == second_task.id
    assert _TaskManager._get(second_task).id == second_task.id

    # We save a third task with same id as the first one.
    # We expect the first task to be updated
    _TaskManager._set(third_task_with_same_id_as_first_task)
    assert len(_TaskManager._get_all()) == 2
    assert _TaskManager._get(task_id_1).id == third_task_with_same_id_as_first_task.id
    assert _TaskManager._get(task_id_1).config_id == third_task_with_same_id_as_first_task.config_id
    assert _TaskManager._get(first_task).id == third_task_with_same_id_as_first_task.id
    assert _TaskManager._get(task_id_2).id == second_task.id
    assert _TaskManager._get(second_task).id == second_task.id


def test_get_all_on_multiple_versions_environment():
    # Create 5 tasks with 2 versions each
    # Only version 1.0 has the task with config_id = "config_id_1"
    # Only version 2.0 has the task with config_id = "config_id_6"
    for version in range(1, 3):
        for i in range(5):
            _TaskManager._set(
                Task(
                    f"config_id_{i+version}", {}, print, [], [], id=TaskId(f"id{i}_v{version}"), version=f"{version}.0"
                )
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_TaskManager._get_all()) == 5
    assert len(_TaskManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_TaskManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_experiment_version("2.0")
    assert len(_TaskManager._get_all()) == 5
    assert len(_TaskManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_TaskManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1

    _VersionManager._set_development_version("1.0")
    assert len(_TaskManager._get_all()) == 5
    assert len(_TaskManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_TaskManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_development_version("2.0")
    assert len(_TaskManager._get_all()) == 5
    assert len(_TaskManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_TaskManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1


def test_ensure_conservation_of_order_of_data_nodes_on_task_creation():
    embedded_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.SCENARIO)
    embedded_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.SCENARIO)
    embedded_3 = Config.configure_data_node("a_dn_3", "in_memory", scope=Scope.SCENARIO)
    embedded_4 = Config.configure_data_node("dn_4", "in_memory", scope=Scope.SCENARIO)
    embedded_5 = Config.configure_data_node("dn_5", "in_memory", scope=Scope.SCENARIO)

    input = [embedded_1, embedded_2, embedded_3]
    output = [embedded_4, embedded_5]

    task_config_1 = Config.configure_task("name_1", print, input, output)
    task_config_2 = Config.configure_task("name_2", print, input, output)

    task_1, task_2 = _TaskManager._bulk_get_or_create([task_config_1, task_config_2])

    assert [i.config_id for i in task_1.input.values()] == [embedded_1.id, embedded_2.id, embedded_3.id]
    assert [o.config_id for o in task_1.output.values()] == [embedded_4.id, embedded_5.id]

    assert [i.config_id for i in task_2.input.values()] == [embedded_1.id, embedded_2.id, embedded_3.id]
    assert [o.config_id for o in task_2.output.values()] == [embedded_4.id, embedded_5.id]


def test_delete_raise_exception():
    dn_input_config_1 = Config.configure_data_node(
        "my_input_1", "in_memory", scope=Scope.SCENARIO, default_data="testing"
    )
    dn_output_config_1 = Config.configure_data_node("my_output_1", "in_memory")
    task_config_1 = Config.configure_task("task_config_1", print, dn_input_config_1, dn_output_config_1)
    task_1 = _create_task_from_config(task_config_1)
    _TaskManager._delete(task_1.id)

    with pytest.raises(ModelNotFound):
        _TaskManager._delete(task_1.id)


def test_hard_delete():
    dn_input_config_1 = Config.configure_data_node(
        "my_input_1", "in_memory", scope=Scope.SCENARIO, default_data="testing"
    )
    dn_output_config_1 = Config.configure_data_node("my_output_1", "in_memory")
    task_config_1 = Config.configure_task("task_config_1", print, dn_input_config_1, dn_output_config_1)
    task_1 = _create_task_from_config(task_config_1)

    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    _TaskManager._hard_delete(task_1.id)
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 2


def test_is_submittable():
    assert len(_TaskManager._get_all()) == 0
    dn_config = Config.configure_in_memory_data_node("dn", 10)
    task_config = Config.configure_task("task", print, [dn_config])
    task = _TaskManager._bulk_get_or_create([task_config])[0]

    rc = _TaskManager._is_submittable("some_task")
    assert not rc
    assert "Entity some_task does not exist in the repository" in rc.reasons

    assert len(_TaskManager._get_all()) == 1
    assert _TaskManager._is_submittable(task)
    assert _TaskManager._is_submittable(task.id)
    assert not _TaskManager._is_submittable("Task_temp")

    task.input["dn"].edit_in_progress = True
    assert not _TaskManager._is_submittable(task)
    assert not _TaskManager._is_submittable(task.id)

    task.input["dn"].edit_in_progress = False
    assert _TaskManager._is_submittable(task)
    assert _TaskManager._is_submittable(task.id)


def test_submit_task():
    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1],
        [data_node_2],
        TaskId("t1"),
    )

    class MockOrchestrator(_Orchestrator):
        submit_calls = []
        submit_ids = []

        def submit_task(self, task, callbacks=None, force=False, wait=False, timeout=None):
            submit_id = f"SUBMISSION_{str(uuid.uuid4())}"
            self.submit_calls.append(task)
            self.submit_ids.append(submit_id)
            return None

    with mock.patch("taipy.core.task._task_manager._TaskManager._orchestrator", new=MockOrchestrator):
        # Task does not exist, we expect an exception
        with pytest.raises(NonExistingTask):
            _TaskManager._submit(task_1)
        with pytest.raises(NonExistingTask):
            _TaskManager._submit(task_1.id)

        _TaskManager._set(task_1)
        _TaskManager._submit(task_1)
        call_ids = [call.id for call in MockOrchestrator.submit_calls]
        assert call_ids == [task_1.id]
        assert len(MockOrchestrator.submit_ids) == 1

        _TaskManager._submit(task_1)
        assert len(MockOrchestrator.submit_ids) == 2
        assert len(MockOrchestrator.submit_ids) == len(set(MockOrchestrator.submit_ids))

        _TaskManager._submit(task_1)
        assert len(MockOrchestrator.submit_ids) == 3
        assert len(MockOrchestrator.submit_ids) == len(set(MockOrchestrator.submit_ids))


def my_print(a, b):
    print(a + b)  # noqa: T201


def test_submit_task_with_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_path="wrong_path.pickle")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_manager = _TaskManagerFactory._build_manager()
    tasks = task_manager._bulk_get_or_create([task_cfg])
    task = tasks[0]
    taipy.submit(task)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in task.input.values()
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in task.output.values()
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_submit_task_with_one_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("pickle_file_path", default_data="value")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_manager = _TaskManagerFactory._build_manager()
    tasks = task_manager._bulk_get_or_create([task_cfg])
    task = tasks[0]
    taipy.submit(task)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in [task.input["wrong_csv_file_path"]]
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in [task.input["pickle_file_path"], task.output["wrong_parquet_file_path"]]
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_get_tasks_by_config_id():
    dn_config = Config.configure_data_node("dn", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("t1", print, dn_config)
    task_config_2 = Config.configure_task("t2", print, dn_config)
    task_config_3 = Config.configure_task("t3", print, dn_config)

    t_1_1 = _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_1")[0]
    t_1_2 = _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_2")[0]
    t_1_3 = _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_3")[0]
    assert len(_TaskManager._get_all()) == 3

    t_2_1 = _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_4")[0]
    t_2_2 = _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_5")[0]
    assert len(_TaskManager._get_all()) == 5

    t_3_1 = _TaskManager._bulk_get_or_create([task_config_3], scenario_id="scenario_6")[0]
    assert len(_TaskManager._get_all()) == 6

    t1_tasks = _TaskManager._get_by_config_id(task_config_1.id)
    assert len(t1_tasks) == 3
    assert sorted([t_1_1.id, t_1_2.id, t_1_3.id]) == sorted([task.id for task in t1_tasks])

    t2_tasks = _TaskManager._get_by_config_id(task_config_2.id)
    assert len(t2_tasks) == 2
    assert sorted([t_2_1.id, t_2_2.id]) == sorted([task.id for task in t2_tasks])

    t3_tasks = _TaskManager._get_by_config_id(task_config_3.id)
    assert len(t3_tasks) == 1
    assert sorted([t_3_1.id]) == sorted([task.id for task in t3_tasks])


def test_get_scenarios_by_config_id_in_multiple_versions_environment():
    dn_config = Config.configure_data_node("dn", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("t1", print, dn_config)
    task_config_2 = Config.configure_task("t2", print, dn_config)

    _VersionManager._set_experiment_version("1.0")
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_1")[0]
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_2")[0]
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_3")[0]
    _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_4")[0]
    _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_5")[0]

    assert len(_TaskManager._get_by_config_id(task_config_1.id)) == 3
    assert len(_TaskManager._get_by_config_id(task_config_2.id)) == 2

    _VersionManager._set_experiment_version("2.0")
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_1")[0]
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_2")[0]
    _TaskManager._bulk_get_or_create([task_config_1], scenario_id="scenario_3")[0]
    _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_4")[0]
    _TaskManager._bulk_get_or_create([task_config_2], scenario_id="scenario_5")[0]

    assert len(_TaskManager._get_by_config_id(task_config_1.id)) == 3
    assert len(_TaskManager._get_by_config_id(task_config_2.id)) == 2


def _create_task_from_config(task_config, *args, **kwargs):
    return _TaskManager._bulk_get_or_create([task_config], *args, **kwargs)[0]
