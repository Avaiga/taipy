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

from unittest import mock

import pytest

from taipy.config.common.scope import Scope
from taipy.core.common._utils import _Subscriber
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node import DataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.sequence.sequence import Sequence
from taipy.core.sequence.sequence_id import SequenceId
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task, TaskId


def test_create_sequence():
    input = InMemoryDataNode("foo", Scope.SCENARIO)
    output = InMemoryDataNode("bar", Scope.SCENARIO)
    task = Task("baz", {}, print, [input], [output], TaskId("task_id"))

    sequence = Sequence({"description": "description"}, [task], sequence_id=SequenceId("name_1"))
    assert sequence.id == "name_1"
    assert sequence.owner_id is None
    assert sequence.description == "description"
    assert sequence.foo == input
    assert sequence.bar == output
    assert sequence.baz.id == task.id
    assert sequence.tasks == {task.config_id: task}
    assert sequence.data_nodes == {"foo": input, "bar": output}
    assert sequence.parent_ids == set()
    with pytest.raises(AttributeError):
        _ = sequence.qux
    assert sequence.get_label() == sequence.id
    assert sequence.get_simple_label() == sequence.id

    input_1 = InMemoryDataNode("input", Scope.SCENARIO)
    output_1 = InMemoryDataNode("output", Scope.SCENARIO)
    task_1 = Task("task_1", {}, print, [input_1], [output_1], TaskId("task_id_1"))
    sequence_1 = Sequence(
        {"description": "description"},
        [task_1],
        owner_id="owner_id",
        parent_ids={"scenario_id"},
        sequence_id=SequenceId("name_1"),
    )
    assert sequence_1.id == "name_1"
    assert sequence_1.owner_id == "owner_id"
    assert sequence_1.description == "description"
    assert sequence_1.input == input_1
    assert sequence_1.output == output_1
    assert sequence_1.task_1 == task_1
    assert sequence_1.tasks == {task_1.config_id: task_1}
    assert sequence_1.data_nodes == {"input": input_1, "output": output_1}
    assert sequence_1.parent_ids == {"scenario_id"}
    assert sequence_1.id is not None
    with mock.patch("taipy.core.get") as get_mck:

        class MockOwner:
            label = "owner_label"

            def get_label(self):
                return self.label

        get_mck.return_value = MockOwner()
        assert sequence_1.get_label() == "owner_label > " + sequence_1.id
        assert sequence_1.get_simple_label() == sequence_1.id

    sequence_2 = Sequence(
        {"description": "description", "name": "Name"},
        [task, task_1],
        owner_id="owner_id",
        parent_ids={"parent_id_1", "parent_id_2"},
        sequence_id=SequenceId("name_2"),
    )
    assert sequence_2.owner_id == "owner_id"
    assert sequence_2.id == "name_2"
    assert sequence_2.description == "description"
    assert sequence_2.tasks == {task.config_id: task, task_1.config_id: task_1}
    assert sequence_2.data_nodes == {"foo": input, "bar": output, "input": input_1, "output": output_1}
    assert sequence_2.parent_ids == {"parent_id_1", "parent_id_2"}
    with mock.patch("taipy.core.get") as get_mck:

        class MockOwner:
            label = "owner_label"

            def get_label(self):
                return self.label

        get_mck.return_value = MockOwner()
        assert sequence_2.get_label() == "owner_label > " + sequence_2.name
        assert sequence_2.get_simple_label() == sequence_2.name


def test_check_consistency():
    sequence_1 = Sequence({}, [], "name_1")
    assert sequence_1._is_consistent()

    input_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_2 = InMemoryDataNode("bar", Scope.SCENARIO)
    task_2 = Task("tfoo", {}, print, [input_2], [output_2], TaskId("task_id_2"))
    sequence_2 = Sequence({}, [task_2], "name_2")
    assert sequence_2._is_consistent()

    data_node_3 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_3 = Task("tfoo", {}, print, [data_node_3], [data_node_3], TaskId("task_id_3"))
    sequence_3 = Sequence({}, [task_3], "name_3")
    assert not sequence_3._is_consistent()  # Not a dag

    input_4 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_4 = InMemoryDataNode("bar", Scope.SCENARIO)
    task_4_1 = Task("tfoo", {}, print, [input_4], [output_4], TaskId("task_id_4_1"))
    task_4_2 = Task("tbar", {}, print, [output_4], [input_4], TaskId("task_id_4_2"))
    sequence_4 = Sequence({}, [task_4_1, task_4_2], "name_4")
    assert not sequence_4._is_consistent()  # Not a Dag

    class FakeDataNode:
        config_id = "config_id_of_a_fake_dn"

    input_6 = DataNode("foo", Scope.SCENARIO, "input_id_5")
    output_6 = DataNode("bar", Scope.SCENARIO, "output_id_5")
    task_6_1 = Task("tfoo", {}, print, [input_6], [output_6], TaskId("task_id_5_1"))
    task_6_2 = Task("tbar", {}, print, [output_6], [FakeDataNode()], TaskId("task_id_5_2"))
    sequence_6 = Sequence({}, [task_6_1, task_6_2], "name_5")
    assert not sequence_6._is_consistent()  # Not a DataNode

    intermediate_7 = DataNode("foo", Scope.SCENARIO, "intermediate_id_7")
    output_7 = DataNode("bar", Scope.SCENARIO, "output_id_7")
    task_7_1 = Task("tfoo", {}, print, [], [intermediate_7], TaskId("task_id_7_1"))
    task_7_2 = Task("tbar", {}, print, [intermediate_7], [output_7], TaskId("task_id_7_2"))
    sequence_7 = Sequence({}, [task_7_1, task_7_2], "name_7")
    assert sequence_7._is_consistent()

    input_8 = DataNode("foo", Scope.SCENARIO, "output_id_8")
    intermediate_8 = DataNode("bar", Scope.SCENARIO, "intermediate_id_8")
    task_8_1 = Task("tfoo", {}, print, [input_8], [intermediate_8], TaskId("task_id_8_1"))
    task_8_2 = Task("tbar", {}, print, [intermediate_8], [], TaskId("task_id_8_2"))
    sequence_8 = Sequence({}, [task_8_1, task_8_2], "name_8")
    assert sequence_8._is_consistent()

    input_9_1 = DataNode("foo", Scope.SCENARIO, "input_id_9_1")
    output_9_1 = DataNode("bar", Scope.SCENARIO, "output_id_9_1")
    input_9_2 = DataNode("baz", Scope.SCENARIO, "input_id_9_2")
    output_9_2 = DataNode("qux", Scope.SCENARIO, "output_id_9_2")
    task_9_1 = Task("tfoo", {}, print, [input_9_1], [output_9_1], TaskId("task_id_9_1"))
    task_9_2 = Task("tbar", {}, print, [input_9_2], [output_9_2], TaskId("task_id_9_2"))
    sequence_9 = Sequence({}, [task_9_1, task_9_2], "name_9")
    assert not sequence_9._is_consistent()  # Not connected

    input_10_1 = DataNode("foo", Scope.SCENARIO, "output_id_10_1")
    intermediate_10_1 = DataNode("bar", Scope.SCENARIO, "intermediate_id_10_1")
    intermediate_10_2 = DataNode("baz", Scope.SCENARIO, "intermediate_id_10_2")
    output_10 = DataNode("qux", Scope.SCENARIO, "output_id_10")
    post_10 = DataNode("quux", Scope.SCENARIO, "post_id_10")
    task_10_1 = Task("tfoo", {}, print, [input_10_1], [intermediate_10_1], TaskId("task_id_10_1"))
    task_10_2 = Task("tbar", {}, print, [], [intermediate_10_2], TaskId("task_id_10_2"))
    task_10_3 = Task("tbaz", {}, print, [intermediate_10_1, intermediate_10_2], [output_10], TaskId("task_id_10_3"))
    task_10_4 = Task("tqux", {}, print, [output_10], [post_10], TaskId("task_id_10_4"))
    task_10_5 = Task("tquux", {}, print, [output_10], [], TaskId("task_id_10_5"))
    sequence_10 = Sequence({}, [task_10_1, task_10_2, task_10_3, task_10_4, task_10_5], "name_10")
    assert sequence_10._is_consistent()


def test_get_sorted_tasks():
    def assert_equal(tasks_a, tasks_b) -> bool:
        if len(tasks_a) != len(tasks_b):
            return False
        for i in range(len(tasks_a)):
            task_a, task_b = tasks_a[i], tasks_b[i]
            if isinstance(task_a, list) and isinstance(task_b, list):
                if not assert_equal(task_a, task_b):
                    return False
            elif isinstance(task_a, list) or isinstance(task_b, list):
                return False
            else:
                index_task_b = tasks_b.index(task_a)
                if any(isinstance(task_b, list) for task_b in tasks_b[i : index_task_b + 1]):
                    return False
        return True

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = DataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
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
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(sequence._get_sorted_tasks(), [[task_1], [task_2, task_4], [task_3]])

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(sequence._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(sequence._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---              t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(sequence._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = DataNode("hugh", Scope.SCENARIO, "s8")

    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_8], None, TaskId("t5"))
    sequence = Sequence({}, [task_5, task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5
    # s8 ---> t5
    assert assert_equal(sequence._get_sorted_tasks(), [[task_5, task_2, task_1], [task_4, task_3]])


def test_get_inputs():
    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = DataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3, data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert sequence.get_inputs() == {data_node_1, data_node_2}
    assert sequence.get_outputs() == {data_node_6, data_node_7}
    assert sequence.get_intermediate() == {data_node_3, data_node_4, data_node_5}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert sequence.get_inputs() == {data_node_1, data_node_2}
    assert sequence.get_outputs() == {data_node_6, data_node_7}
    assert sequence.get_intermediate() == {data_node_4, data_node_5}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert sequence.get_inputs() == {data_node_1, data_node_2, data_node_6}
    assert sequence.get_outputs() == {data_node_7}
    assert sequence.get_intermediate() == {data_node_4, data_node_5}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = DataNode("hugh", Scope.SCENARIO, "s8")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4, data_node_6], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_8], None, TaskId("t5"))
    sequence = Sequence({}, [task_5, task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5                   |
    # s8 ---> t5              s6 --|
    assert sequence.get_inputs() == {data_node_1, data_node_2, data_node_8, data_node_6}
    assert sequence.get_outputs() == {data_node_5, data_node_7}
    assert sequence.get_intermediate() == {data_node_4}


def test_is_ready_to_run():
    data_node_1 = PickleDataNode("foo", Scope.SCENARIO, "s1", properties={"default_data": 1})
    data_node_2 = PickleDataNode("bar", Scope.SCENARIO, "s2", properties={"default_data": 2})
    data_node_4 = PickleDataNode("qux", Scope.SCENARIO, "s4", properties={"default_data": 4})
    data_node_5 = PickleDataNode("quux", Scope.SCENARIO, "s5", properties={"default_data": 5})
    data_node_6 = PickleDataNode("quuz", Scope.SCENARIO, "s6", properties={"default_data": 6})
    data_node_7 = PickleDataNode("corge", Scope.SCENARIO, "s7", properties={"default_data": 7})
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_manager = _DataManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7]:
        data_manager._set(dn)

    assert sequence.is_ready_to_run()

    data_node_1.edit_in_progress = True
    assert not sequence.is_ready_to_run()

    data_node_2.edit_in_progress = True
    data_node_6.edit_in_progress = True
    assert not sequence.is_ready_to_run()

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    assert sequence.is_ready_to_run()


def test_data_nodes_being_edited():
    data_node_1 = PickleDataNode("foo", Scope.SCENARIO, "s1", properties={"default_data": 1})
    data_node_2 = PickleDataNode("bar", Scope.SCENARIO, "s2", properties={"default_data": 2})
    data_node_4 = PickleDataNode("qux", Scope.SCENARIO, "s4", properties={"default_data": 4})
    data_node_5 = PickleDataNode("quux", Scope.SCENARIO, "s5", properties={"default_data": 5})
    data_node_6 = PickleDataNode("quuz", Scope.SCENARIO, "s6", properties={"default_data": 6})
    data_node_7 = PickleDataNode("corge", Scope.SCENARIO, "s7", properties={"default_data": 7})
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_manager = _DataManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7]:
        data_manager._set(dn)

    assert len(sequence.data_nodes_being_edited()) == 0
    assert sequence.data_nodes_being_edited() == set()

    data_node_1.edit_in_progress = True
    assert len(sequence.data_nodes_being_edited()) == 1
    assert sequence.data_nodes_being_edited() == {data_node_1}

    data_node_2.edit_in_progress = True
    data_node_6.edit_in_progress = True
    assert len(sequence.data_nodes_being_edited()) == 3
    assert sequence.data_nodes_being_edited() == {data_node_1, data_node_2, data_node_6}

    data_node_4.edit_in_progress = True
    data_node_5.edit_in_progress = True
    assert len(sequence.data_nodes_being_edited()) == 5
    assert sequence.data_nodes_being_edited() == {data_node_1, data_node_2, data_node_4, data_node_5, data_node_6}

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    assert len(sequence.data_nodes_being_edited()) == 2
    assert sequence.data_nodes_being_edited() == {data_node_4, data_node_5}

    data_node_4.edit_in_progress = False
    data_node_5.edit_in_progress = False
    data_node_7.edit_in_progress = True
    assert len(sequence.data_nodes_being_edited()) == 1
    assert sequence.data_nodes_being_edited() == {data_node_7}

    data_node_7.edit_in_progress = False
    assert len(sequence.data_nodes_being_edited()) == 0
    assert sequence.data_nodes_being_edited() == set()


def test_get_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    sequence_1 = Sequence({}, [task_1, task_2, task_3], SequenceId("p1"))
    assert sequence_1.tasks == {"grault": task_1, "garply": task_2, "waldo": task_3}


def test_get_set_of_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    sequence_1 = Sequence({}, [task_1, task_2, task_3], SequenceId("p1"))
    assert sequence_1._get_set_of_tasks() == {task_1, task_2, task_3}


def test_auto_set_and_reload(task):
    tmp_task = Task("tmp_task_config_id", {}, print, list(task.output.values()), [], TaskId("tmp_task_id"))
    scenario = Scenario("scenario", [task, tmp_task], {}, sequences={"foo": {}})

    _TaskManager._set(task)
    _TaskManager._set(tmp_task)
    _ScenarioManager._set(scenario)

    sequence_1 = scenario.sequences["foo"]
    sequence_2 = _SequenceManager._get(sequence_1)

    # auto set & reload on tasks attribute
    assert len(sequence_1.tasks) == 0
    assert len(sequence_2.tasks) == 0
    sequence_1.tasks = [tmp_task]
    assert len(sequence_1.tasks) == 1
    assert sequence_1.tasks[tmp_task.config_id].id == tmp_task.id
    assert len(sequence_2.tasks) == 1
    assert sequence_2.tasks[tmp_task.config_id].id == tmp_task.id
    sequence_2.tasks = [task]
    assert len(sequence_1.tasks) == 1
    assert sequence_1.tasks[task.config_id].id == task.id
    assert len(sequence_2.tasks) == 1
    assert sequence_2.tasks[task.config_id].id == task.id

    assert sequence_1.owner_id == scenario.id
    assert sequence_2.owner_id == scenario.id

    # auto set & reload on subscribers attribute
    assert len(sequence_1.subscribers) == 0
    assert len(sequence_2.subscribers) == 0
    sequence_1.subscribers.append(print)
    assert len(sequence_1.subscribers) == 1
    assert len(sequence_2.subscribers) == 1
    sequence_2.subscribers.append(print)
    assert len(sequence_1.subscribers) == 2
    assert len(sequence_2.subscribers) == 2

    sequence_1.subscribers.clear()
    assert len(sequence_1.subscribers) == 0
    assert len(sequence_2.subscribers) == 0

    sequence_1.subscribers.extend([print, map])
    assert len(sequence_1.subscribers) == 2
    assert len(sequence_2.subscribers) == 2

    sequence_1.subscribers.remove(_Subscriber(print, []))
    assert len(sequence_1.subscribers) == 1
    assert len(sequence_2.subscribers) == 1

    sequence_2.subscribers.clear()
    assert len(sequence_1.subscribers) == 0
    assert len(sequence_2.subscribers) == 0

    sequence_1.subscribers + print + len
    assert len(sequence_1.subscribers) == 2
    assert len(sequence_2.subscribers) == 2

    sequence_1.subscribers = []
    assert len(sequence_1.subscribers) == 0
    assert len(sequence_2.subscribers) == 0

    # auto set & reload on properties attribute
    assert sequence_1.properties == {"name": "foo"}
    assert sequence_2.properties == {"name": "foo"}
    sequence_1.properties["qux"] = 4
    assert sequence_1.properties["qux"] == 4
    assert sequence_2.properties["qux"] == 4
    sequence_2.properties["qux"] = 5
    assert sequence_1.properties["qux"] == 5
    assert sequence_2.properties["qux"] == 5

    sequence_1.properties["temp_key_1"] = "temp_value_1"
    sequence_1.properties["temp_key_2"] = "temp_value_2"
    assert sequence_1.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    assert sequence_2.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    sequence_1.properties.pop("temp_key_1")
    assert "temp_key_1" not in sequence_1.properties.keys()
    assert "temp_key_1" not in sequence_1.properties.keys()
    assert sequence_1.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_2": "temp_value_2",
    }
    assert sequence_2.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_2": "temp_value_2",
    }
    sequence_2.properties.pop("temp_key_2")
    assert sequence_1.properties == {"name": "foo", "qux": 5}
    assert sequence_2.properties == {"name": "foo", "qux": 5}
    assert "temp_key_2" not in sequence_1.properties.keys()
    assert "temp_key_2" not in sequence_2.properties.keys()

    sequence_1.properties["temp_key_3"] = 0
    assert sequence_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 0}
    assert sequence_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 0}
    sequence_1.properties.update({"temp_key_3": 1})
    assert sequence_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    assert sequence_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    sequence_1.properties.update(dict())
    assert sequence_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    assert sequence_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    sequence_1.properties["temp_key_4"] = 0
    sequence_1.properties["temp_key_5"] = 0

    with sequence_1 as sequence:
        assert len(sequence.tasks) == 1
        assert sequence.tasks[task.config_id].id == task.id
        assert len(sequence.subscribers) == 0
        assert sequence._is_in_context
        assert sequence.properties["qux"] == 5
        assert sequence.properties["temp_key_3"] == 1
        assert sequence.properties["temp_key_4"] == 0
        assert sequence.properties["temp_key_5"] == 0

        sequence.tasks = []
        sequence.subscribers = [print]
        sequence.properties["qux"] = 9
        sequence.properties.pop("temp_key_3")
        sequence.properties.pop("temp_key_4")
        sequence.properties.update({"temp_key_4": 1})
        sequence.properties.update({"temp_key_5": 2})
        sequence.properties.pop("temp_key_5")
        sequence.properties.update(dict())

        assert len(sequence.tasks) == 1
        assert sequence.tasks[task.config_id].id == task.id
        assert len(sequence.subscribers) == 0
        assert sequence._is_in_context
        assert sequence.properties["qux"] == 5
        assert sequence.properties["temp_key_3"] == 1
        assert sequence.properties["temp_key_4"] == 0
        assert sequence.properties["temp_key_5"] == 0

    assert len(sequence_1.tasks) == 0
    assert len(sequence_1.subscribers) == 1
    assert not sequence_1._is_in_context
    assert sequence_1.properties["qux"] == 9
    assert "temp_key_3" not in sequence_1.properties.keys()
    assert sequence_1.properties["temp_key_4"] == 1
    assert "temp_key_5" not in sequence_1.properties.keys()


def test_get_parents(sequence):
    with mock.patch("taipy.core.get_parents") as mck:
        sequence.get_parents()
        mck.assert_called_once_with(sequence)


def test_subscribe_sequence():
    with mock.patch("taipy.core.subscribe_sequence") as mck:
        sequence = Sequence({}, [], "id")
        sequence.subscribe(None)
        mck.assert_called_once_with(None, None, sequence)


def test_unsubscribe_sequence():
    with mock.patch("taipy.core.unsubscribe_sequence") as mck:
        sequence = Sequence({}, [], "id")
        sequence.unsubscribe(None)
        mck.assert_called_once_with(None, None, sequence)


def test_submit_sequence():
    with mock.patch("taipy.core.sequence._sequence_manager._SequenceManager._submit") as mck:
        sequence = Sequence({}, [], "id")
        sequence.submit(None, False)
        mck.assert_called_once_with(sequence, None, False, False, None)
