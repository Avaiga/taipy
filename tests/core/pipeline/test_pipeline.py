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

from unittest import mock

import pytest

from src.taipy.core.common._utils import Subscriber
from src.taipy.core.common.alias import PipelineId, TaskId
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config.data_node.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


def test_create_pipeline():
    input = InMemoryDataNode("foo", Scope.PIPELINE)
    output = InMemoryDataNode("bar", Scope.PIPELINE)
    task = Task("baz", print, [input], [output], TaskId("task_id"))
    pipeline = Pipeline("name_1", {"description": "description"}, [task])
    assert pipeline.id is not None
    assert pipeline.parent_id is None
    assert pipeline.config_id == "name_1"
    assert pipeline.description == "description"
    assert pipeline.foo == input
    assert pipeline.bar == output
    assert pipeline.baz == task

    with pytest.raises(AttributeError):
        pipeline.qux

    input_1 = InMemoryDataNode("input", Scope.SCENARIO)
    output_1 = InMemoryDataNode("output", Scope.SCENARIO)
    task_1 = Task("task_1", print, [input_1], [output_1], TaskId("task_id_1"))
    pipeline_1 = Pipeline("name_1", {"description": "description"}, [task_1], parent_id="parent_id")
    assert pipeline_1.id is not None
    assert pipeline_1.parent_id == "parent_id"
    assert pipeline_1.config_id == "name_1"
    assert pipeline_1.description == "description"
    assert pipeline_1.input == input_1
    assert pipeline_1.output == output_1
    assert pipeline_1.task_1 == task_1

    assert pipeline_1.id is not None
    with pytest.raises(InvalidConfigurationId):
        Pipeline("name 1", {"description": "description"}, [task_1], parent_id="parent_id")


def test_check_consistency():
    pipeline_1 = Pipeline("name_1", {}, [])
    assert pipeline_1._is_consistent()

    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_2 = Task("foo", print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2])
    assert pipeline_2._is_consistent()

    data_node_3 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_3 = Task("foo", print, [data_node_3], [data_node_3], TaskId("task_id_3"))
    pipeline_3 = Pipeline("name_3", {}, [task_3])
    assert not pipeline_3._is_consistent()  # Not a dag

    input_4 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_4 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_4_1 = Task("foo", print, [input_4], [output_4], TaskId("task_id_4_1"))
    task_4_2 = Task("bar", print, [output_4], [input_4], TaskId("task_id_4_2"))
    pipeline_4 = Pipeline("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4._is_consistent()  # Not a Dag

    class FakeDataNode:
        config_id = "config_id_of_a_fake_dn"

    input_5 = DataNode("foo", Scope.PIPELINE, "input_id_5")
    output_5 = DataNode("foo", Scope.PIPELINE, "output_id_5")
    task_5_1 = Task("foo", print, [input_5], [output_5], TaskId("task_id_5_1"))
    task_5_2 = Task("bar", print, [output_5], [FakeDataNode()], TaskId("task_id_5_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_5_1, task_5_2])
    assert not pipeline_2._is_consistent()


def test_get_sorted_tasks():
    data_node_1 = DataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = DataNode("bar", Scope.PIPELINE, "s2")
    data_node_3 = DataNode("baz", Scope.PIPELINE, "s3")
    data_node_4 = DataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = DataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = DataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = DataNode("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_3, data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline._get_sorted_tasks() == [[task_1], [task_2, task_4], [task_3]]

    data_node_1 = DataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = DataNode("bar", Scope.PIPELINE, "s2")
    data_node_4 = DataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = DataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = DataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = DataNode("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline._get_sorted_tasks() == [[task_2, task_1], [task_4, task_3]]

    data_node_1 = DataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = DataNode("bar", Scope.PIPELINE, "s2")
    data_node_4 = DataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = DataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = DataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = DataNode("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline._get_sorted_tasks() == [[task_2, task_1], [task_4, task_3]]

    data_node_1 = DataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = DataNode("bar", Scope.PIPELINE, "s2")
    data_node_4 = DataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = DataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = DataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = DataNode("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_5, data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---              t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline._get_sorted_tasks() == [[task_2, task_1], [task_4, task_3]]

    data_node_1 = DataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = DataNode("bar", Scope.PIPELINE, "s2")
    data_node_4 = DataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = DataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = DataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = DataNode("corge", Scope.PIPELINE, "s7")
    data_node_8 = DataNode("hugh", Scope.PIPELINE, "s8")

    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", print, [data_node_8], None, TaskId("t5"))
    pipeline = Pipeline("plugh", {}, [task_5, task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5
    # s8 ---> t5
    assert pipeline._get_sorted_tasks() == [[task_5, task_2, task_1], [task_4, task_3]]


def test_auto_set_and_reload(task):
    pipeline_1 = Pipeline("foo", {}, [], parent_id=None, subscribers=None)

    _TaskManager._set(task)
    _PipelineManager._set(pipeline_1)

    pipeline_2 = _PipelineManager._get(pipeline_1)

    assert pipeline_1.config_id == "foo"
    assert pipeline_2.config_id == "foo"

    assert len(pipeline_1.tasks) == 0
    pipeline_1.tasks = [task]
    assert len(pipeline_1.tasks) == 1
    assert pipeline_1.tasks[task.config_id].id == task.id
    assert len(pipeline_2.tasks) == 1
    assert pipeline_2.tasks[task.config_id].id == task.id

    assert pipeline_1.parent_id is None
    assert pipeline_2.parent_id is None

    assert pipeline_1.properties == {}
    pipeline_1.properties["qux"] = 5
    assert pipeline_1.properties["qux"] == 5
    assert pipeline_2.properties["qux"] == 5

    assert len(pipeline_1.subscribers) == 0
    pipeline_1.subscribers.append(print)
    assert len(pipeline_1.subscribers) == 1
    assert len(pipeline_2.subscribers) == 1

    pipeline_1.subscribers.clear()
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0

    pipeline_1.subscribers.extend([print, map])
    assert len(pipeline_1.subscribers) == 2
    assert len(pipeline_2.subscribers) == 2

    pipeline_1.subscribers.remove(Subscriber(print, []))
    assert len(pipeline_1.subscribers) == 1
    assert len(pipeline_2.subscribers) == 1

    pipeline_1.subscribers + print + len
    assert len(pipeline_1.subscribers) == 3
    assert len(pipeline_2.subscribers) == 3

    pipeline_1.subscribers = []
    assert len(pipeline_1.subscribers) == 0
    assert len(pipeline_2.subscribers) == 0

    with pipeline_1 as pipeline:
        assert pipeline.config_id == "foo"
        assert len(pipeline.tasks) == 1
        assert pipeline.tasks[task.config_id].id == task.id
        assert pipeline.parent_id is None
        assert len(pipeline.subscribers) == 0
        assert pipeline._is_in_context

        pipeline.tasks = []
        pipeline.parent_id = None
        pipeline.subscribers = [print]

        assert pipeline.config_id == "foo"
        assert len(pipeline.tasks) == 1
        assert pipeline.tasks[task.config_id].id == task.id
        assert pipeline.parent_id is None
        assert len(pipeline.subscribers) == 0
        assert pipeline._is_in_context

    assert pipeline_1.config_id == "foo"
    assert len(pipeline_1.tasks) == 0
    assert pipeline_1.parent_id is None
    assert len(pipeline_1.subscribers) == 1
    assert not pipeline_1._is_in_context


def test_subscribe_pipeline():
    with mock.patch("src.taipy.core.subscribe_pipeline") as mck:
        pipeline = Pipeline("id", {}, [])
        pipeline.subscribe(None)
        mck.assert_called_once_with(None, None, pipeline)


def test_unsubscribe_pipeline():
    with mock.patch("src.taipy.core.unsubscribe_pipeline") as mck:
        pipeline = Pipeline("id", {}, [])
        pipeline.unsubscribe(None)
        mck.assert_called_once_with(None, None, pipeline)


def test_submit_pipeline():
    with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
        pipeline = Pipeline("id", {}, [])
        pipeline.submit(None, False)
        mck.assert_called_once_with(pipeline, None, False)
