import pytest

from taipy.core import Taipy as tp
from taipy.core.common.alias import PipelineId, TaskId
from taipy.core.data.data_node import DataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task.task import Task


def test_create_pipeline():
    input = InMemoryDataNode("foo", Scope.PIPELINE)
    output = InMemoryDataNode("bar", Scope.PIPELINE)
    task = Task("baz", print, [input], [output], TaskId("task_id"))
    pipeline = Pipeline("nAmE 1 ", {"description": "description"}, [task])
    assert pipeline.id is not None
    assert pipeline.parent_id is None
    assert pipeline.config_name == "name_1"
    assert pipeline.description == "description"
    assert pipeline.foo == input
    assert pipeline.bar == output
    assert pipeline.baz == task

    with pytest.raises(AttributeError):
        pipeline.qux

    input_1 = InMemoryDataNode("inξ", Scope.SCENARIO)
    output_1 = InMemoryDataNode("outξ", Scope.SCENARIO)
    task_1 = Task("task_ξ", print, [input_1], [output_1], TaskId("task_id_1"))
    pipeline_1 = Pipeline("nAmE 1 ", {"description": "description"}, [task_1], parent_id="parent_id")
    assert pipeline_1.id is not None
    assert pipeline_1.parent_id == "parent_id"
    assert pipeline_1.config_name == "name_1"
    assert pipeline_1.description == "description"
    assert pipeline_1.inx == input_1
    assert pipeline_1.outx == output_1
    assert pipeline_1.task_x == task_1


def test_add_property_to_pipeline():
    pipeline = Pipeline("qux", {}, [])

    tp.set(pipeline)
    pipeline.properties["abc"] = 5
    same_pipeline = tp.get(pipeline.id)

    assert pipeline.properties["abc"] == 5
    assert same_pipeline.properties["abc"] == 5


def test_check_consistency():
    pipeline_1 = Pipeline("name_1", {}, [])
    assert pipeline_1.is_consistent

    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_2 = Task("foo", print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2])
    assert pipeline_2.is_consistent

    data_node_3 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_3 = Task("foo", print, [data_node_3], [data_node_3], TaskId("task_id_3"))
    pipeline_3 = Pipeline("name_3", {}, [task_3])
    assert not pipeline_3.is_consistent  # Not a dag

    input_4 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_4 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_4_1 = Task("foo", print, [input_4], [output_4], TaskId("task_id_4_1"))
    task_4_2 = Task("bar", print, [output_4], [input_4], TaskId("task_id_4_2"))
    pipeline_4 = Pipeline("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4.is_consistent  # Not a Dag

    class FakeDataNode:
        config_name = "config_name_of_a_fake_dn"

    input_5 = DataNode("foo", Scope.PIPELINE, "input_id_5")
    output_5 = DataNode("foo", Scope.PIPELINE, "output_id_5")
    task_5_1 = Task("foo", print, [input_5], [output_5], TaskId("task_id_5_1"))
    task_5_2 = Task("bar", print, [output_5], [FakeDataNode()], TaskId("task_id_5_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_5_1, task_5_2])
    assert not pipeline_2.is_consistent


def test_to_model():
    input = InMemoryDataNode("input", Scope.PIPELINE)
    output = InMemoryDataNode("output", Scope.PIPELINE)
    task = Task("task", print, [input], [output], TaskId("task_id"))
    pipeline = Pipeline("name", {"foo": "bar"}, [task])
    model = pipeline.to_model()
    assert model.name == "name"
    assert model.id == pipeline.id
    assert len(model.properties) == 1
    assert model.properties["foo"] == "bar"
    assert model.datanode_task_edges[input.id] == [task.id]
    assert model.task_datanode_edges[task.id] == [output.id]


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
    assert pipeline.get_sorted_tasks() == [[task_1], [task_2, task_4], [task_3]]
