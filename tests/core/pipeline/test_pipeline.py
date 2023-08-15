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

from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.data.pickle import PickleDataNode
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.pipeline.pipeline_id import PipelineId
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task, TaskId
from taipy.config.common.scope import Scope


def test_create_pipeline():
    input = InMemoryDataNode("foo", Scope.SCENARIO)
    output = InMemoryDataNode("bar", Scope.SCENARIO)
    task = Task("baz", {}, print, [input], [output], TaskId("task_id"))

    pipeline = Pipeline({"description": "description"}, [task], pipeline_id=PipelineId("name_1"))
    assert pipeline.id == "name_1"
    assert pipeline.owner_id is None
    assert pipeline.description == "description"
    assert pipeline.foo == input
    assert pipeline.bar == output
    assert pipeline.baz.id == task.id
    assert pipeline.tasks == {task.config_id: task}
    assert pipeline.data_nodes == {"foo": input, "bar": output}
    assert pipeline.parent_ids == set()
    with pytest.raises(AttributeError):
        pipeline.qux
    assert pipeline.get_label() == pipeline.id
    assert pipeline.get_simple_label() == pipeline.id

    input_1 = InMemoryDataNode("input", Scope.SCENARIO)
    output_1 = InMemoryDataNode("output", Scope.SCENARIO)
    task_1 = Task("task_1", {}, print, [input_1], [output_1], TaskId("task_id_1"))
    pipeline_1 = Pipeline(
        {"description": "description"},
        [task_1],
        owner_id="owner_id",
        parent_ids={"scenario_id"},
        pipeline_id=PipelineId("name_1"),
    )
    assert pipeline_1.id == "name_1"
    assert pipeline_1.owner_id == "owner_id"
    assert pipeline_1.description == "description"
    assert pipeline_1.input == input_1
    assert pipeline_1.output == output_1
    assert pipeline_1.task_1 == task_1
    assert pipeline_1.tasks == {task_1.config_id: task_1}
    assert pipeline_1.data_nodes == {"input": input_1, "output": output_1}
    assert pipeline_1.parent_ids == {"scenario_id"}
    assert pipeline_1.id is not None
    with mock.patch("src.taipy.core.get") as get_mck:

        class MockOwner:
            label = "owner_label"

            def get_label(self):
                return self.label

        get_mck.return_value = MockOwner()
        assert pipeline_1.get_label() == "owner_label > " + pipeline_1.id
        assert pipeline_1.get_simple_label() == pipeline_1.id

    pipeline_2 = Pipeline(
        {"description": "description", "name": "Name"},
        [task, task_1],
        owner_id="owner_id",
        parent_ids={"parent_id_1", "parent_id_2"},
        pipeline_id=PipelineId("name_2"),
    )
    assert pipeline_2.owner_id == "owner_id"
    assert pipeline_2.id == "name_2"
    assert pipeline_2.description == "description"
    assert pipeline_2.tasks == {task.config_id: task, task_1.config_id: task_1}
    assert pipeline_2.data_nodes == {"foo": input, "bar": output, "input": input_1, "output": output_1}
    assert pipeline_2.parent_ids == {"parent_id_1", "parent_id_2"}
    with mock.patch("src.taipy.core.get") as get_mck:

        class MockOwner:
            label = "owner_label"

            def get_label(self):
                return self.label

        get_mck.return_value = MockOwner()
        assert pipeline_2.get_label() == "owner_label > " + pipeline_2.name
        assert pipeline_2.get_simple_label() == pipeline_2.name


def test_check_consistency():
    pipeline_1 = Pipeline({}, [], "name_1")
    assert pipeline_1._is_consistent()

    input_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_2 = Task("foo", {}, print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline({}, [task_2], "name_2")
    assert pipeline_2._is_consistent()

    data_node_3 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_3 = Task("foo", {}, print, [data_node_3], [data_node_3], TaskId("task_id_3"))
    pipeline_3 = Pipeline({}, [task_3], "name_3")
    assert not pipeline_3._is_consistent()  # Not a dag

    input_4 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_4 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_4_1 = Task("foo", {}, print, [input_4], [output_4], TaskId("task_id_4_1"))
    task_4_2 = Task("bar", {}, print, [output_4], [input_4], TaskId("task_id_4_2"))
    pipeline_4 = Pipeline({}, [task_4_1, task_4_2], "name_4")
    assert not pipeline_4._is_consistent()  # Not a Dag

    class FakeDataNode:
        config_id = "config_id_of_a_fake_dn"

    input_5 = DataNode("foo", Scope.SCENARIO, "input_id_5")
    output_5 = DataNode("foo", Scope.SCENARIO, "output_id_5")
    task_5_1 = Task("foo", {}, print, [input_5], [output_5], TaskId("task_id_5_1"))
    task_5_2 = Task("bar", {}, print, [output_5], [FakeDataNode()], TaskId("task_id_5_2"))
    pipeline_2 = Pipeline({}, [task_5_1, task_5_2], "name_2")
    assert not pipeline_2._is_consistent()


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
                if any([isinstance(task_b, list) for task_b in tasks_b[i : index_task_b + 1]]):
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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(pipeline._get_sorted_tasks(), [[task_1], [task_2, task_4], [task_3]])

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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(pipeline._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(pipeline._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---              t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert assert_equal(pipeline._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

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
    pipeline = Pipeline({}, [task_5, task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5
    # s8 ---> t5
    assert assert_equal(pipeline._get_sorted_tasks(), [[task_5, task_2, task_1], [task_4, task_3]])


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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline.get_inputs() == {data_node_1, data_node_2}
    assert pipeline.get_outputs() == {data_node_6, data_node_7}
    assert pipeline.get_intermediate() == {data_node_3, data_node_4, data_node_5}

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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline.get_inputs() == {data_node_1, data_node_2}
    assert pipeline.get_outputs() == {data_node_6, data_node_7}
    assert pipeline.get_intermediate() == {data_node_4, data_node_5}

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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline.get_inputs() == {data_node_1, data_node_2, data_node_6}
    assert pipeline.get_outputs() == {data_node_7}
    assert pipeline.get_intermediate() == {data_node_4, data_node_5}

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
    pipeline = Pipeline({}, [task_5, task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5                   |
    # s8 ---> t5              s6 --|
    assert pipeline.get_inputs() == {data_node_1, data_node_2, data_node_8, data_node_6}
    assert pipeline.get_outputs() == {data_node_5, data_node_7}
    assert pipeline.get_intermediate() == {data_node_4}


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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_manager = _DataManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7]:
        data_manager._set(dn)

    assert pipeline.is_ready_to_run()

    data_node_1.edit_in_progress = True
    assert not pipeline.is_ready_to_run()

    data_node_2.edit_in_progress = True
    data_node_6.edit_in_progress = True
    assert not pipeline.is_ready_to_run()

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    assert pipeline.is_ready_to_run()


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
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_manager = _DataManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7]:
        data_manager._set(dn)

    assert len(pipeline.data_nodes_being_edited()) == 0
    assert pipeline.data_nodes_being_edited() == set()

    data_node_1.edit_in_progress = True
    assert len(pipeline.data_nodes_being_edited()) == 1
    assert pipeline.data_nodes_being_edited() == {data_node_1}

    data_node_2.edit_in_progress = True
    data_node_6.edit_in_progress = True
    assert len(pipeline.data_nodes_being_edited()) == 3
    assert pipeline.data_nodes_being_edited() == {data_node_1, data_node_2, data_node_6}

    data_node_4.edit_in_progress = True
    data_node_5.edit_in_progress = True
    assert len(pipeline.data_nodes_being_edited()) == 5
    assert pipeline.data_nodes_being_edited() == {data_node_1, data_node_2, data_node_4, data_node_5, data_node_6}

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    assert len(pipeline.data_nodes_being_edited()) == 2
    assert pipeline.data_nodes_being_edited() == {data_node_4, data_node_5}

    data_node_4.edit_in_progress = False
    data_node_5.edit_in_progress = False
    data_node_7.edit_in_progress = True
    assert len(pipeline.data_nodes_being_edited()) == 1
    assert pipeline.data_nodes_being_edited() == {data_node_7}

    data_node_7.edit_in_progress = False
    assert len(pipeline.data_nodes_being_edited()) == 0
    assert pipeline.data_nodes_being_edited() == set()


def test_get_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    pipeline_1 = Pipeline({}, [task_1, task_2, task_3], PipelineId("p1"))
    assert pipeline_1.tasks == {"grault": task_1, "garply": task_2, "waldo": task_3}


def test_get_set_of_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    pipeline_1 = Pipeline({}, [task_1, task_2, task_3], PipelineId("p1"))
    assert pipeline_1._get_set_of_tasks() == {task_1, task_2, task_3}


def test_auto_set_and_reload(task):
    tmp_task = Task("tmp_task_config_id", {}, print, [], [], TaskId("tmp_task_id"))
    scenario = Scenario("scenario", [task, tmp_task], {}, pipelines={"foo": {}})

    _TaskManager._set(task)
    _TaskManager._set(tmp_task)
    _ScenarioManager._set(scenario)

    pipeline_1 = scenario.pipelines["foo"]
    pipeline_2 = _PipelineManager._get(pipeline_1)

    # auto set & reload on tasks attribute
    assert len(pipeline_1.tasks) == 0
    assert len(pipeline_2.tasks) == 0
    pipeline_1.tasks = [tmp_task]
    assert len(pipeline_1.tasks) == 1
    assert pipeline_1.tasks[tmp_task.config_id].id == tmp_task.id
    assert len(pipeline_2.tasks) == 1
    assert pipeline_2.tasks[tmp_task.config_id].id == tmp_task.id
    pipeline_2.tasks = [task]
    assert len(pipeline_1.tasks) == 1
    assert pipeline_1.tasks[task.config_id].id == task.id
    assert len(pipeline_2.tasks) == 1
    assert pipeline_2.tasks[task.config_id].id == task.id

    assert pipeline_1.owner_id == scenario.id
    assert pipeline_2.owner_id == scenario.id

    # auto set & reload on subscribers attribute
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0
    pipeline_1.subscribers.append(print)
    assert len(pipeline_1.subscribers) == 1
    assert len(pipeline_2.subscribers) == 1
    pipeline_2.subscribers.append(print)
    assert len(pipeline_1.subscribers) == 2
    assert len(pipeline_2.subscribers) == 2

    pipeline_1.subscribers.clear()
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0

    pipeline_1.subscribers.extend([print, map])
    assert len(pipeline_1.subscribers) == 2
    assert len(pipeline_2.subscribers) == 2

    pipeline_1.subscribers.remove(_Subscriber(print, []))
    assert len(pipeline_1.subscribers) == 1
    assert len(pipeline_2.subscribers) == 1

    pipeline_2.subscribers.clear()
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0

    pipeline_1.subscribers + print + len
    assert len(pipeline_1.subscribers) == 2
    assert len(pipeline_2.subscribers) == 2

    pipeline_1.subscribers = []
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0

    # auto set & reload on properties attribute
    assert pipeline_1.properties == {"name": "foo"}
    assert pipeline_2.properties == {"name": "foo"}
    pipeline_1.properties["qux"] = 4
    assert pipeline_1.properties["qux"] == 4
    assert pipeline_2.properties["qux"] == 4
    pipeline_2.properties["qux"] = 5
    assert pipeline_1.properties["qux"] == 5
    assert pipeline_2.properties["qux"] == 5

    pipeline_1.properties["temp_key_1"] = "temp_value_1"
    pipeline_1.properties["temp_key_2"] = "temp_value_2"
    assert pipeline_1.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    assert pipeline_2.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    pipeline_1.properties.pop("temp_key_1")
    assert "temp_key_1" not in pipeline_1.properties.keys()
    assert "temp_key_1" not in pipeline_1.properties.keys()
    assert pipeline_1.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_2": "temp_value_2",
    }
    assert pipeline_2.properties == {
        "qux": 5,
        "name": "foo",
        "temp_key_2": "temp_value_2",
    }
    pipeline_2.properties.pop("temp_key_2")
    assert pipeline_1.properties == {"name": "foo", "qux": 5}
    assert pipeline_2.properties == {"name": "foo", "qux": 5}
    assert "temp_key_2" not in pipeline_1.properties.keys()
    assert "temp_key_2" not in pipeline_2.properties.keys()

    pipeline_1.properties["temp_key_3"] = 0
    assert pipeline_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 0}
    assert pipeline_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 0}
    pipeline_1.properties.update({"temp_key_3": 1})
    assert pipeline_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    assert pipeline_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    pipeline_1.properties.update(dict())
    assert pipeline_1.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    assert pipeline_2.properties == {"name": "foo", "qux": 5, "temp_key_3": 1}
    pipeline_1.properties["temp_key_4"] = 0
    pipeline_1.properties["temp_key_5"] = 0

    with pipeline_1 as pipeline:
        assert len(pipeline.tasks) == 1
        assert pipeline.tasks[task.config_id].id == task.id
        assert len(pipeline.subscribers) == 0
        assert pipeline._is_in_context
        assert pipeline.properties["qux"] == 5
        assert pipeline.properties["temp_key_3"] == 1
        assert pipeline.properties["temp_key_4"] == 0
        assert pipeline.properties["temp_key_5"] == 0

        pipeline.tasks = []
        pipeline.subscribers = [print]
        pipeline.properties["qux"] = 9
        pipeline.properties.pop("temp_key_3")
        pipeline.properties.pop("temp_key_4")
        pipeline.properties.update({"temp_key_4": 1})
        pipeline.properties.update({"temp_key_5": 2})
        pipeline.properties.pop("temp_key_5")
        pipeline.properties.update(dict())

        assert len(pipeline.tasks) == 1
        assert pipeline.tasks[task.config_id].id == task.id
        assert len(pipeline.subscribers) == 0
        assert pipeline._is_in_context
        assert pipeline.properties["qux"] == 5
        assert pipeline.properties["temp_key_3"] == 1
        assert pipeline.properties["temp_key_4"] == 0
        assert pipeline.properties["temp_key_5"] == 0

    assert len(pipeline_1.tasks) == 0
    assert len(pipeline_1.subscribers) == 1
    assert not pipeline_1._is_in_context
    assert pipeline_1.properties["qux"] == 9
    assert "temp_key_3" not in pipeline_1.properties.keys()
    assert pipeline_1.properties["temp_key_4"] == 1
    assert "temp_key_5" not in pipeline_1.properties.keys()


def test_get_parents(pipeline):
    with mock.patch("src.taipy.core.get_parents") as mck:
        pipeline.get_parents()
        mck.assert_called_once_with(pipeline)


def test_subscribe_pipeline():
    with mock.patch("src.taipy.core.subscribe_pipeline") as mck:
        pipeline = Pipeline({}, [], "id")
        pipeline.subscribe(None)
        mck.assert_called_once_with(None, None, pipeline)


def test_unsubscribe_pipeline():
    with mock.patch("src.taipy.core.unsubscribe_pipeline") as mck:
        pipeline = Pipeline({}, [], "id")
        pipeline.unsubscribe(None)
        mck.assert_called_once_with(None, None, pipeline)


def test_submit_pipeline():
    with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
        pipeline = Pipeline({}, [], "id")
        pipeline.submit(None, False)
        mck.assert_called_once_with(pipeline, None, False, False, None)
