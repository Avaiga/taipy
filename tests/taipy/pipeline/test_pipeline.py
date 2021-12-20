import pytest

from taipy.common.alias import PipelineId, TaskId
from taipy.data import InMemoryDataSource
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope
from taipy.pipeline import Pipeline
from taipy.task import Task


def test_create_pipeline():
    input = InMemoryDataSource("foo", Scope.PIPELINE)
    output = InMemoryDataSource("bar", Scope.PIPELINE)
    task = Task("baz", [input], print, [output], TaskId("task_id"))
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

    input_1 = InMemoryDataSource("inξ", Scope.SCENARIO)
    output_1 = InMemoryDataSource("outξ", Scope.SCENARIO)
    task_1 = Task("task_ξ", [input_1], print, [output_1], TaskId("task_id_1"))
    pipeline_1 = Pipeline("nAmE 1 ", {"description": "description"}, [task_1], parent_id="parent_id")
    assert pipeline_1.id is not None
    assert pipeline_1.parent_id == "parent_id"
    assert pipeline_1.config_name == "name_1"
    assert pipeline_1.description == "description"
    assert pipeline_1.inx == input_1
    assert pipeline_1.outx == output_1
    assert pipeline_1.task_x == task_1


def test_check_consistency():
    pipeline_1 = Pipeline("name_1", {}, [])
    assert pipeline_1.is_consistent

    input_2 = InMemoryDataSource("foo", Scope.PIPELINE)
    output_2 = InMemoryDataSource("foo", Scope.PIPELINE)
    task_2 = Task("foo", [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2])
    assert pipeline_2.is_consistent

    data_source_3 = InMemoryDataSource("foo", Scope.PIPELINE)
    task_3 = Task("foo", [data_source_3], print, [data_source_3], TaskId("task_id_3"))
    pipeline_3 = Pipeline("name_3", {}, [task_3])
    assert not pipeline_3.is_consistent  # Not a dag

    input_4 = InMemoryDataSource("foo", Scope.PIPELINE)
    output_4 = InMemoryDataSource("foo", Scope.PIPELINE)
    task_4_1 = Task("foo", [input_4], print, [output_4], TaskId("task_id_4_1"))
    task_4_2 = Task("bar", [output_4], print, [input_4], TaskId("task_id_4_2"))
    pipeline_4 = Pipeline("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4.is_consistent  # Not a Dag

    class FakeDataSource:
        config_name = "config_name_of_a_fake_DS"

    input_5 = DataSource("foo", Scope.PIPELINE, "input_id_5")
    output_5 = DataSource("foo", Scope.PIPELINE, "output_id_5")
    task_5_1 = Task("foo", [input_5], print, [output_5], TaskId("task_id_5_1"))
    task_5_2 = Task("bar", [output_5], print, [FakeDataSource()], TaskId("task_id_5_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_5_1, task_5_2])
    assert not pipeline_2.is_consistent


def test_to_model():
    input = InMemoryDataSource("input", Scope.PIPELINE)
    output = InMemoryDataSource("output", Scope.PIPELINE)
    task = Task("task", [input], print, [output], TaskId("task_id"))
    pipeline = Pipeline("name", {"foo": "bar"}, [task])
    model = pipeline.to_model()
    assert model.name == "name"
    assert model.id == pipeline.id
    assert len(model.properties) == 1
    assert model.properties["foo"] == "bar"
    assert model.source_task_edges[input.id] == [task.id]
    assert model.task_source_edges[task.id] == [output.id]


def test_get_sorted_tasks():
    data_source_1 = DataSource("foo", Scope.PIPELINE, "s1")
    data_source_2 = DataSource("bar", Scope.PIPELINE, "s2")
    data_source_3 = DataSource("baz", Scope.PIPELINE, "s3")
    data_source_4 = DataSource("qux", Scope.PIPELINE, "s4")
    data_source_5 = DataSource("quux", Scope.PIPELINE, "s5")
    data_source_6 = DataSource("quuz", Scope.PIPELINE, "s6")
    data_source_7 = DataSource("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        [data_source_1, data_source_2],
        print,
        [data_source_3, data_source_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", [data_source_3], print, [data_source_5], TaskId("t2"))
    task_3 = Task("waldo", [data_source_5, data_source_4], print, [data_source_6], TaskId("t3"))
    task_4 = Task("fred", [data_source_4], print, [data_source_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert pipeline.get_sorted_tasks() == [[task_1], [task_2, task_4], [task_3]]
