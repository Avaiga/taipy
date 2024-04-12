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

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Optional
from unittest import mock
from unittest.mock import ANY

import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._version._version_manager import _VersionManager
from taipy.core.common import _utils
from taipy.core.common._utils import _Subscriber
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.exceptions.exceptions import (
    InvalidSequenceId,
    ModelNotFound,
    NonExistingSequence,
    SequenceAlreadyExists,
    SequenceBelongsToNonExistingScenario,
)
from taipy.core.job._job_manager import _JobManager
from taipy.core.notification._submittable_status_cache import SubmittableStatusCache
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.sequence.sequence import Sequence
from taipy.core.sequence.sequence_id import SequenceId
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task
from taipy.core.task.task_id import TaskId
from tests.core.utils.NotifyMock import NotifyMock


def test_breakdown_sequence_id():
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("scenario_id")
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("sequence_id")
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("SEQUENCE_sequence_id")
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("SCENARIO_scenario_id")
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("sequence_SCENARIO_scenario_id")
    with pytest.raises(InvalidSequenceId):
        _SequenceManager._breakdown_sequence_id("SEQUENCE_sequence_scenario_id")
    sequence_name, scenario_id = _SequenceManager._breakdown_sequence_id("SEQUENCE_sequence_SCENARIO_scenario")
    assert sequence_name == "sequence" and scenario_id == "SCENARIO_scenario"
    sequence_name, scenario_id = _SequenceManager._breakdown_sequence_id("SEQUENCEsequenceSCENARIO_scenario")
    assert sequence_name == "sequence" and scenario_id == "SCENARIO_scenario"


def test_raise_sequence_does_not_belong_to_scenario():
    with pytest.raises(SequenceBelongsToNonExistingScenario):
        sequence = Sequence({"name": "sequence_name"}, [], "SEQUENCE_sequence_name_SCENARIO_scenario_id")
        _SequenceManager._set(sequence)


def __init():
    input_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    output_dn = InMemoryDataNode("foo", Scope.SCENARIO)
    task = Task("task", {}, print, [input_dn], [output_dn], TaskId("task_id"))
    scenario = Scenario("scenario", {task}, {}, set())
    _ScenarioManager._set(scenario)
    return scenario, task


def test_set_and_get_sequence_no_existing_sequence():
    scenario, task = __init()
    sequence_name_1 = "p1"
    sequence_id_1 = SequenceId(f"SEQUENCE_{sequence_name_1}_{scenario.id}")
    sequence_name_2 = "p2"
    sequence_id_2 = SequenceId(f"SEQUENCE_{sequence_name_2}_{scenario.id}")

    assert _SequenceManager._get(sequence_id_1) is None
    assert _SequenceManager._get(sequence_id_2) is None
    assert _SequenceManager._get("sequence") is None


def test_set_and_get():
    scenario, task = __init()
    sequence_name_1 = "p1"
    sequence_id_1 = SequenceId(f"SEQUENCE_{sequence_name_1}_{scenario.id}")
    sequence_name_2 = "p2"
    sequence_id_2 = SequenceId(f"SEQUENCE_{sequence_name_2}_{scenario.id}")

    scenario.add_sequences({sequence_name_1: []})
    sequence_1 = scenario.sequences[sequence_name_1]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2) is None

    # Save a second sequence. Now, we expect to have a total of two sequences stored
    _TaskManager._set(task)
    scenario.add_sequences({sequence_name_2: [task]})
    sequence_2 = scenario.sequences[sequence_name_2]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_id_2).tasks) == 1
    assert _SequenceManager._get(sequence_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_2).tasks) == 1
    assert _TaskManager._get(task.id).id == task.id

    # We save the first sequence again. We expect an exception and nothing to change
    with pytest.raises(SequenceAlreadyExists):
        scenario.add_sequence(sequence_name_1, [])
    sequence_1 = scenario.sequences[sequence_name_1]
    assert _SequenceManager._get(sequence_id_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_id_1).tasks) == 0
    assert _SequenceManager._get(sequence_1).id == sequence_1.id
    assert len(_SequenceManager._get(sequence_1).tasks) == 0
    assert _SequenceManager._get(sequence_id_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_id_2).tasks) == 1
    assert _SequenceManager._get(sequence_2).id == sequence_2.id
    assert len(_SequenceManager._get(sequence_2).tasks) == 1
    assert _TaskManager._get(task.id).id == task.id


def test_get_all_on_multiple_versions_environment():
    # Create 5 sequences from Scenario with 2 versions each
    for version in range(1, 3):
        for i in range(5):
            _ScenarioManager._set(
                Scenario(
                    f"config_id_{i+version}",
                    [],
                    {},
                    [],
                    f"SCENARIO_id_{i}_v{version}",
                    version=f"{version}.0",
                    sequences={"sequence": {}},
                )
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 1
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )

    _VersionManager._set_experiment_version("2.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 1
    )

    _VersionManager._set_development_version("1.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 1
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "1.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 0
    )

    _VersionManager._set_development_version("2.0")
    assert len(_SequenceManager._get_all()) == 5
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v1"}])) == 0
    )
    assert (
        len(_SequenceManager._get_all_by(filters=[{"version": "2.0", "id": "SEQUENCE_sequence_SCENARIO_id_1_v2"}])) == 1
    )


def test_is_submittable():
    task_id = "TASK_task_id"
    scenario_id = "SCENARIO_scenario_id"
    dn_1 = PickleDataNode("dn_1", Scope.SCENARIO, parent_ids={task_id, scenario_id}, properties={"default_data": 10})
    dn_2 = PickleDataNode("dn_2", Scope.SCENARIO, parent_ids={task_id, scenario_id}, properties={"default_data": 10})
    task = Task("task", {}, print, [dn_1, dn_2], id=task_id, parent_ids={scenario_id})
    scenario = Scenario("scenario", {task}, {}, set(), scenario_id=scenario_id)
    _DataManager._set(dn_1)
    _DataManager._set(dn_2)
    _TaskManager._set(task)
    _ScenarioManager._set(scenario)

    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2

    scenario.add_sequences({"sequence": [task]})
    sequence = scenario.sequences["sequence"]
    assert len(_SequenceManager._get_all()) == 1
    assert sequence.id not in SubmittableStatusCache._submittable_id_datanodes
    assert scenario.id not in SubmittableStatusCache._submittable_id_datanodes
    assert _SequenceManager._is_submittable(sequence)
    assert _SequenceManager._is_submittable(sequence.id)
    assert _ScenarioManager._is_submittable(scenario)
    assert not _SequenceManager._is_submittable("Sequence_temp")
    assert not _SequenceManager._is_submittable("SEQUENCE_temp_SCENARIO_scenario")

    dn_1.edit_in_progress = True
    assert scenario.id in SubmittableStatusCache._submittable_id_datanodes
    assert sequence.id in SubmittableStatusCache._submittable_id_datanodes
    assert dn_1.id in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_1.id in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_1.id in SubmittableStatusCache._datanode_id_submittables
    assert scenario.id in SubmittableStatusCache._datanode_id_submittables[dn_1.id]
    assert sequence.id in SubmittableStatusCache._datanode_id_submittables[dn_1.id]
    assert (
        SubmittableStatusCache._submittable_id_datanodes[scenario.id][dn_1.id] == f"DataNode {dn_1.id} is being edited"
    )
    assert (
        SubmittableStatusCache._submittable_id_datanodes[sequence.id][dn_1.id] == f"DataNode {dn_1.id} is being edited"
    )
    assert not _ScenarioManager._is_submittable(scenario)
    assert not _SequenceManager._is_submittable(sequence)
    assert not _SequenceManager._is_submittable(sequence.id)

    dn_1.edit_in_progress = False
    assert scenario.id not in SubmittableStatusCache._submittable_id_datanodes
    assert sequence.id not in SubmittableStatusCache._submittable_id_datanodes
    assert dn_1.id not in SubmittableStatusCache._datanode_id_submittables
    assert _SequenceManager._is_submittable(sequence)
    assert _SequenceManager._is_submittable(sequence.id)
    assert _ScenarioManager._is_submittable(scenario)

    dn_1.last_edit_date = None
    dn_2.edit_in_progress = True
    assert scenario.id in SubmittableStatusCache._submittable_id_datanodes
    assert sequence.id in SubmittableStatusCache._submittable_id_datanodes
    assert dn_1.id in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_1.id in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_2.id in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_2.id in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_1.id in SubmittableStatusCache._datanode_id_submittables
    assert scenario.id in SubmittableStatusCache._datanode_id_submittables[dn_1.id]
    assert sequence.id in SubmittableStatusCache._datanode_id_submittables[dn_1.id]
    assert dn_2.id in SubmittableStatusCache._datanode_id_submittables
    assert scenario.id in SubmittableStatusCache._datanode_id_submittables[dn_2.id]
    assert sequence.id in SubmittableStatusCache._datanode_id_submittables[dn_2.id]
    assert (
        SubmittableStatusCache._submittable_id_datanodes[scenario.id][dn_1.id] == f"DataNode {dn_1.id} is not written"
    )
    assert (
        SubmittableStatusCache._submittable_id_datanodes[sequence.id][dn_1.id] == f"DataNode {dn_1.id} is not written"
    )
    assert (
        SubmittableStatusCache._submittable_id_datanodes[scenario.id][dn_2.id] == f"DataNode {dn_2.id} is being edited"
    )
    assert (
        SubmittableStatusCache._submittable_id_datanodes[sequence.id][dn_2.id] == f"DataNode {dn_2.id} is being edited"
    )
    assert not _ScenarioManager._is_submittable(scenario)
    assert not _SequenceManager._is_submittable(sequence)
    assert not _SequenceManager._is_submittable(sequence.id)

    dn_1.last_edit_date = datetime.now()
    assert scenario.id in SubmittableStatusCache._submittable_id_datanodes
    assert sequence.id in SubmittableStatusCache._submittable_id_datanodes
    assert dn_1.id not in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_1.id not in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_2.id in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_2.id in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_1.id not in SubmittableStatusCache._datanode_id_submittables
    assert dn_2.id in SubmittableStatusCache._datanode_id_submittables
    assert scenario.id in SubmittableStatusCache._datanode_id_submittables[dn_2.id]
    assert sequence.id in SubmittableStatusCache._datanode_id_submittables[dn_2.id]
    assert (
        SubmittableStatusCache._submittable_id_datanodes[scenario.id][dn_2.id] == f"DataNode {dn_2.id} is being edited"
    )
    assert (
        SubmittableStatusCache._submittable_id_datanodes[sequence.id][dn_2.id] == f"DataNode {dn_2.id} is being edited"
    )
    assert not _ScenarioManager._is_submittable(scenario)
    assert not _SequenceManager._is_submittable(sequence)
    assert not _SequenceManager._is_submittable(sequence.id)

    dn_2.edit_in_progress = False
    assert scenario.id not in SubmittableStatusCache._submittable_id_datanodes
    assert sequence.id not in SubmittableStatusCache._submittable_id_datanodes
    assert dn_2.id not in SubmittableStatusCache._submittable_id_datanodes[scenario.id]
    assert dn_2.id not in SubmittableStatusCache._submittable_id_datanodes[sequence.id]
    assert dn_2.id not in SubmittableStatusCache._datanode_id_submittables
    assert _ScenarioManager._is_submittable(scenario)
    assert _SequenceManager._is_submittable(sequence)
    assert _SequenceManager._is_submittable(sequence.id)


def test_submit():
    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_3, data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario = Scenario("sce", {task_1, task_2, task_3, task_4}, {})

    sequence_name = "sequence"
    sequence_id = Sequence._new_id(sequence_name, scenario.id)

    class MockOrchestrator(_Orchestrator):
        submit_calls = []

        @classmethod
        def _lock_dn_output_and_create_job(
            cls,
            task: Task,
            submit_id: str,
            submit_entity_id: str,
            callbacks: Optional[Iterable[Callable]] = None,
            force: bool = False,
        ):
            cls.submit_calls.append(task)
            return super()._lock_dn_output_and_create_job(task, submit_id, submit_entity_id, callbacks, force)

    with mock.patch("taipy.core.task._task_manager._TaskManager._orchestrator", new=MockOrchestrator):
        # sequence does not exist. We expect an exception to be raised
        with pytest.raises(NonExistingSequence):
            _SequenceManager._submit(sequence_id)

        _ScenarioManager._set(scenario)
        scenario.add_sequences({sequence_name: [task_4, task_2, task_1, task_3]})

        # sequence, and tasks does exist. We expect the tasks to be submitted
        # in a specific order
        _TaskManager._set(task_1)
        _TaskManager._set(task_2)
        _TaskManager._set(task_3)
        _TaskManager._set(task_4)
        sequence = scenario.sequences[sequence_name]

        _SequenceManager._submit(sequence.id)
        calls_ids = [t.id for t in _TaskManager._orchestrator().submit_calls]
        tasks_ids = [task_1.id, task_2.id, task_4.id, task_3.id]
        assert calls_ids == tasks_ids

        _SequenceManager._submit(sequence)
        calls_ids = [t.id for t in _TaskManager._orchestrator().submit_calls]
        tasks_ids = tasks_ids * 2
        assert set(calls_ids) == set(tasks_ids)


def test_assign_sequence_as_parent_of_task():
    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.SCENARIO)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.SCENARIO)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])

    tasks = _TaskManager._bulk_get_or_create([task_config_1, task_config_2, task_config_3], "scenario_id")
    sequence_1 = _SequenceManager._create("sequence_1", [tasks[0], tasks[1]], scenario_id="scenario_id")
    sequence_2 = _SequenceManager._create("sequence_2", [tasks[0], tasks[2]], scenario_id="scenario_id")

    tasks_1 = list(sequence_1.tasks.values())
    tasks_2 = list(sequence_2.tasks.values())

    assert len(tasks_1) == 2
    assert len(tasks_2) == 2

    assert tasks_1[0].parent_ids == {sequence_1.id, sequence_2.id}
    assert tasks_2[0].parent_ids == {sequence_1.id, sequence_2.id}
    assert tasks_1[1].parent_ids == {sequence_1.id}
    assert tasks_2[1].parent_ids == {sequence_2.id}


g = 0


def mock_function_no_input_no_output():
    global g
    g += 1


def mock_function_one_input_no_output(inp):
    global g
    g += inp


def mock_function_no_input_one_output():
    global g
    return g


def test_submit_sequence_from_tasks_with_one_or_no_input_output():
    # test no input and no output Task
    task_no_input_no_output = Task("task_no_input_no_output", {}, mock_function_no_input_no_output)
    scenario_1 = Scenario("scenario_1", {task_no_input_no_output}, {})

    _TaskManager._set(task_no_input_no_output)
    _ScenarioManager._set(scenario_1)

    scenario_1.add_sequences({"my_sequence_1": [task_no_input_no_output]})
    sequence_1 = scenario_1.sequences["my_sequence_1"]

    assert len(sequence_1._get_sorted_tasks()) == 1

    _SequenceManager._submit(sequence_1)
    assert g == 1

    # test one input and no output Task
    data_node_input = InMemoryDataNode("input_dn", Scope.SCENARIO, properties={"default_data": 2})
    task_one_input_no_output = Task(
        "task_one_input_no_output", {}, mock_function_one_input_no_output, input=[data_node_input]
    )
    scenario_2 = Scenario("scenario_2", {task_one_input_no_output}, {})

    _DataManager._set(data_node_input)
    data_node_input.unlock_edit()

    _TaskManager._set(task_one_input_no_output)
    _ScenarioManager._set(scenario_2)

    scenario_2.add_sequences({"my_sequence_2": [task_one_input_no_output]})
    sequence_2 = scenario_2.sequences["my_sequence_2"]
    assert len(sequence_2._get_sorted_tasks()) == 1

    _SequenceManager._submit(sequence_2)
    assert g == 3

    # test no input and one output Task
    data_node_output = InMemoryDataNode("output_dn", Scope.SCENARIO, properties={"default_data": None})
    task_no_input_one_output = Task(
        "task_no_input_one_output", {}, mock_function_no_input_one_output, output=[data_node_output]
    )
    scenario_3 = Scenario("scenario_3", {task_no_input_one_output}, {})

    _DataManager._set(data_node_output)
    assert data_node_output.read() is None
    _TaskManager._set(task_no_input_one_output)
    _ScenarioManager._set(scenario_3)

    scenario_3.add_sequences({"my_sequence_3": [task_no_input_one_output]})
    sequence_3 = scenario_3.sequences["my_sequence_3"]

    assert len(sequence_2._get_sorted_tasks()) == 1

    _SequenceManager._submit(sequence_3)
    assert data_node_output.read() == 3


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data():
    # only create intermediate data node once
    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.SCENARIO, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6
    scenario_config = Config.configure_scenario("scenario", [task_config_mult_by_two, task_config_mult_by_3])

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0

    scenario = _ScenarioManager._create(scenario_config)
    scenario.add_sequences({"by_6": list(scenario.tasks.values())})
    sequence = scenario.sequences["by_6"]

    assert sequence.name == "by_6"

    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 2
    assert len(sequence._get_sorted_tasks()) == 2
    assert sequence.foo.read() == 1
    assert sequence.bar.read() == 0
    assert sequence.baz.read() == 0
    assert sequence._get_sorted_tasks()[0][0].config_id == task_config_mult_by_two.id
    assert sequence._get_sorted_tasks()[1][0].config_id == task_config_mult_by_3.id

    _SequenceManager._submit(sequence.id)
    assert sequence.foo.read() == 1
    assert sequence.bar.read() == 2
    assert sequence.baz.read() == 6

    sequence.foo.write("new data value")
    assert sequence.foo.read() == "new data value"
    assert sequence.bar.read() == 2
    assert sequence.baz.read() == 6

    sequence.bar.write(7)
    assert sequence.foo.read() == "new data value"
    assert sequence.bar.read() == 7
    assert sequence.baz.read() == 6

    with pytest.raises(AttributeError):
        sequence.WRONG.write(7)


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def notify_multi_param(*args, **kwargs):
    ...


def test_sequence_notification_subscribe(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    tasks = _TaskManager._bulk_get_or_create(task_configs=task_configs)
    scenario = Scenario("scenario", set(tasks), {}, sequences={"by_1": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["by_1"]

    notify_1 = NotifyMock(sequence)
    notify_1.__name__ = "notify_1"
    notify_1.__module__ = "notify_1"
    notify_2 = NotifyMock(sequence)
    notify_2.__name__ = "notify_2"
    notify_2.__module__ = "notify_2"
    # Mocking this because NotifyMock is a class that does not loads correctly when getting the sequence
    # from the storage.
    mocker.patch.object(
        _utils,
        "_load_fct",
        side_effect=[notify_1, notify_1, notify_1, notify_2, notify_2, notify_2, notify_2, notify_2],
    )

    # test subscription
    callback = mock.MagicMock()
    _SequenceManager._submit(sequence.id, [callback])
    callback.assert_called()

    # test sequence subscribe notification
    _SequenceManager._subscribe(callback=notify_1, sequence=sequence)
    _SequenceManager._submit(sequence.id)

    notify_1.assert_called_3_times()
    notify_1.reset()

    # test sequence unsubscribe notification
    # test subscribe notification only on new job
    _SequenceManager._unsubscribe(callback=notify_1, sequence=sequence)
    _SequenceManager._subscribe(callback=notify_2, sequence=sequence)
    _SequenceManager._submit(sequence)

    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


def test_sequence_notification_subscribe_multi_param(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    scenario = Scenario("scenario", set(tasks), {}, sequences={"by_6": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["by_6"]
    notify = mocker.Mock()

    # test sequence subscribe notification
    _SequenceManager._subscribe(callback=notify, params=["foobar", 123, 1.2], sequence=sequence)
    mocker.patch.object(_SequenceManager, "_get", return_value=sequence)

    _SequenceManager._submit(sequence.id)

    # as the callback is called with Sequence/Scenario and Job objects
    # we can assert that is called with params plus a sequence object that we know
    # of and a job object that is represented by ANY in this case
    notify.assert_called_with("foobar", 123, 1.2, sequence, ANY)


def test_sequence_notification_unsubscribe(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    scenario = Scenario("scenario", set(tasks), {}, sequences={"by_6": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["by_6"]

    notify_1 = notify1
    notify_2 = notify2

    _SequenceManager._subscribe(callback=notify_1, sequence=sequence)
    _SequenceManager._unsubscribe(callback=notify_1, sequence=sequence)
    _SequenceManager._subscribe(callback=notify_2, sequence=sequence)
    _SequenceManager._submit(sequence.id)

    with pytest.raises(ValueError):
        _SequenceManager._unsubscribe(callback=notify_1, sequence=sequence)
        _SequenceManager._unsubscribe(callback=notify_2, sequence=sequence)


def test_sequence_notification_unsubscribe_multi_param():
    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    scenario = Scenario("scenario", tasks, {}, sequences={"by_6": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["by_6"]

    _SequenceManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 0], sequence=sequence)
    _SequenceManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 1], sequence=sequence)
    _SequenceManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 2], sequence=sequence)

    assert len(sequence.subscribers) == 3

    sequence.unsubscribe(notify_multi_param)
    assert len(sequence.subscribers) == 2
    assert _Subscriber(notify_multi_param, ["foobar", 123, 0]) not in sequence.subscribers

    sequence.unsubscribe(notify_multi_param, ["foobar", 123, 2])
    assert len(sequence.subscribers) == 1
    assert _Subscriber(notify_multi_param, ["foobar", 123, 2]) not in sequence.subscribers

    with pytest.raises(ValueError):
        sequence.unsubscribe(notify_multi_param, ["foobar", 123, 10000])


def test_sequence_notification_subscribe_all():
    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    scenario = Scenario("scenario", tasks, {}, sequences={"by_6": {"tasks": tasks}, "other_sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["by_6"]
    other_sequence = scenario.sequences["other_sequence"]

    notify_1 = NotifyMock(sequence)

    _SequenceManager._subscribe(notify_1)

    assert len(_SequenceManager._get(sequence.id).subscribers) == 1
    assert len(_SequenceManager._get(other_sequence.id).subscribers) == 1


def test_delete():
    sequence_id = "SEQUENCE_sequence_SCENARIO_scenario_id_1"
    with pytest.raises(ModelNotFound):
        _SequenceManager._delete(sequence_id)

    scenario_1 = Scenario("scenario_1", set(), {}, scenario_id="SCENARIO_scenario_id_1")
    scenario_2 = Scenario("scenario_2", set(), {}, scenario_id="SCENARIO_scenario_id_2")
    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)
    with pytest.raises(ModelNotFound):
        _SequenceManager._delete(SequenceId(sequence_id))

    scenario_1.add_sequences({"sequence": []})
    assert len(_SequenceManager._get_all()) == 1
    _SequenceManager._delete(SequenceId(sequence_id))
    assert len(_SequenceManager._get_all()) == 0

    scenario_1.add_sequences({"sequence": [], "sequence_1": []})
    assert len(_SequenceManager._get_all()) == 2
    _SequenceManager._delete(SequenceId(sequence_id))
    assert len(_SequenceManager._get_all()) == 1

    with pytest.raises(SequenceAlreadyExists):
        scenario_1.add_sequences({"sequence_1": [], "sequence_2": [], "sequence_3": []})
    scenario_1.add_sequences({"sequence_2": [], "sequence_3": []})
    scenario_2.add_sequences({"sequence_1_2": [], "sequence_2_2": []})
    assert len(_SequenceManager._get_all()) == 5
    _SequenceManager._delete_all()
    assert len(_SequenceManager._get_all()) == 0

    scenario_1.add_sequences({"sequence_1": [], "sequence_2": [], "sequence_3": [], "sequence_4": []})
    scenario_2.add_sequences({"sequence_1_2": [], "sequence_2_2": []})
    assert len(_SequenceManager._get_all()) == 6
    _SequenceManager._delete_many(
        [
            "SEQUENCE_sequence_1_SCENARIO_scenario_id_1",
            "SEQUENCE_sequence_2_SCENARIO_scenario_id_1",
            "SEQUENCE_sequence_1_2_SCENARIO_scenario_id_2",
        ]
    )
    assert len(_SequenceManager._get_all()) == 3

    with pytest.raises(ModelNotFound):
        _SequenceManager._delete_many(
            ["SEQUENCE_sequence_1_SCENARIO_scenario_id_1", "SEQUENCE_sequence_2_SCENARIO_scenario_id_1"]
        )


def test_delete_version():
    scenario_1_0 = Scenario(
        "scenario_config",
        [],
        {},
        scenario_id="SCENARIO_id_1_v1_0",
        version="1.0",
        sequences={"sequence_1": {}, "sequence_2": {}},
    )
    scenario_1_1 = Scenario(
        "scenario_config",
        [],
        {},
        scenario_id="SCENARIO_id_1_v1_1",
        version="1.1",
        sequences={"sequence_1": {}, "sequence_2": {}},
    )
    _ScenarioManager._set(scenario_1_0)
    _ScenarioManager._set(scenario_1_1)

    _VersionManager._set_experiment_version("1.1")
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 2

    _VersionManager._set_experiment_version("1.0")
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 2

    _SequenceManager._delete_by_version("1.0")
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0
    assert len(scenario_1_0.sequences) == 0
    assert len(scenario_1_1.sequences) == 2

    _VersionManager._set_experiment_version("1.1")
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 2
    assert len(scenario_1_0.sequences) == 0
    assert len(scenario_1_1.sequences) == 2
    _SequenceManager._delete_by_version("1.1")
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0


def test_exists():
    scenario = Scenario("scenario", [], {}, scenario_id="SCENARIO_scenario", sequences={"sequence": {}})
    _ScenarioManager._set(scenario)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert not _SequenceManager._exists("SEQUENCE_sequence_not_exist_SCENARIO_scenario")
    assert not _SequenceManager._exists("SEQUENCE_sequence_SCENARIO_scenario_id")
    assert _SequenceManager._exists("SEQUENCE_sequence_SCENARIO_scenario")
    assert _SequenceManager._exists(scenario.sequences["sequence"])


def test_export(tmpdir_factory):
    path = tmpdir_factory.mktemp("data")
    task = Task("task", {}, print, id=TaskId("task_id"))
    scenario = Scenario(
        "scenario",
        {task},
        {},
        set(),
        version="1.0",
        sequences={"sequence_1": {}, "sequence_2": {"tasks": [task], "properties": {"xyz": "acb"}}},
    )
    _TaskManager._set(task)
    _ScenarioManager._set(scenario)

    sequence_1 = scenario.sequences["sequence_1"]
    sequence_2 = scenario.sequences["sequence_2"]

    _SequenceManager._export(sequence_1.id, Path(path))
    export_sequence_json_file_path = f"{path}/sequences/{sequence_1.id}.json"
    with open(export_sequence_json_file_path, "rb") as f:
        sequence_json_file = json.load(f)
        expected_json = {
            "id": sequence_1.id,
            "owner_id": scenario.id,
            "parent_ids": [scenario.id],
            "name": "sequence_1",
            "tasks": [],
            "properties": {},
            "subscribers": [],
        }
        assert expected_json == sequence_json_file

    _SequenceManager._export(sequence_2.id, Path(path))
    export_sequence_json_file_path = f"{path}/sequences/{sequence_2.id}.json"
    with open(export_sequence_json_file_path, "rb") as f:
        sequence_json_file = json.load(f)
        expected_json = {
            "id": sequence_2.id,
            "owner_id": scenario.id,
            "parent_ids": [scenario.id],
            "name": "sequence_2",
            "tasks": [task.id],
            "properties": {"xyz": "acb"},
            "subscribers": [],
        }
        assert expected_json == sequence_json_file


def test_hard_delete_one_single_sequence_with_scenario_data_nodes():
    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", tasks, {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["sequence"]
    sequence.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _SequenceManager._hard_delete(sequence.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_one_single_sequence_with_cycle_data_nodes():
    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    tasks = _TaskManager._bulk_get_or_create([task_config])
    scenario = Scenario("scenario", tasks, {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)

    sequence = scenario.sequences["sequence"]
    sequence.submit()

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _SequenceManager._hard_delete(sequence.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_shared_entities():
    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)

    tasks_scenario_1 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_1")
    tasks_scenario_2 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_2")

    scenario_1 = Scenario("scenario_1", tasks_scenario_1, {}, sequences={"sequence": {"tasks": tasks_scenario_1}})
    scenario_2 = Scenario("scenario_2", tasks_scenario_2, {}, sequences={"sequence": {"tasks": tasks_scenario_2}})
    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)
    sequence_1 = scenario_1.sequences["sequence"]
    sequence_2 = scenario_2.sequences["sequence"]

    _SequenceManager._submit(sequence_1.id)
    _SequenceManager._submit(sequence_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
    _SequenceManager._hard_delete(sequence_1.id)
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4


def my_print(a, b):
    print(a + b)  # noqa: T201


def test_submit_task_with_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_path="wrong_path.pickle")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)

    tasks = _TaskManager._bulk_get_or_create([task_cfg, task_2_cfg])
    scenario = Scenario("scenario", tasks, {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)
    sequence = scenario.sequences["sequence"]

    pip_manager = _SequenceManagerFactory._build_manager()
    pip_manager._submit(sequence)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in sequence.get_inputs()
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in sequence.data_nodes.values()
        if input_dn not in sequence.get_inputs()
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_submit_task_with_one_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_data="value")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)

    tasks = _TaskManager._bulk_get_or_create([task_cfg, task_2_cfg])
    scenario = Scenario("scenario", tasks, {}, sequences={"sequence": {"tasks": tasks}})
    _ScenarioManager._set(scenario)
    sequence = scenario.sequences["sequence"]

    pip_manager = _SequenceManagerFactory._build_manager()
    pip_manager._submit(sequence)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in sequence.get_inputs()
        if input_dn.config_id == "wrong_csv_file_path"
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in sequence.data_nodes.values()
        if input_dn.config_id != "wrong_csv_file_path"
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)
