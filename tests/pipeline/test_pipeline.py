from taipy.data.data_source import EmbeddedDataSource
from taipy.data.data_source.models import Scope
from taipy.pipeline import Pipeline
from taipy.task import Task, TaskId


def test_create_pipeline():
    pipeline = Pipeline.create_pipeline("name_1", {}, [])
    assert pipeline.id is not None


def test_check_consistency():
    pipeline_1 = Pipeline.create_pipeline("name_1", {}, [])
    assert pipeline_1.is_acyclic

    input_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "input_id_2", "bar")
    output_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "output_id_2", "bar")
    task_2 = Task(TaskId("task_id_2"), "foo", [input_2], print, [output_2])
    pipeline_2 = Pipeline.create_pipeline("name_2", {}, [task_2])
    assert pipeline_2.is_acyclic

    data_source_3 = EmbeddedDataSource.create(
        "foo", Scope.PIPELINE, "data_source_3_id", "bar"
    )
    task_3 = Task(TaskId("task_id_3"), "foo", [data_source_3], print, [data_source_3])
    pipeline_3 = Pipeline.create_pipeline("name_3", {}, [task_3])
    assert not pipeline_3.is_acyclic

    input_4 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "input_4_id", "bar")
    output_4 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "output_4_id", "bar")
    task_4_1 = Task(TaskId("task_id_4_1"), "foo", [input_4], print, [output_4])
    task_4_2 = Task(TaskId("task_id_4_2"), "foo", [output_4], print, [input_4])
    pipeline_4 = Pipeline.create_pipeline("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4.is_acyclic


def test_to_model():
    input = EmbeddedDataSource.create(
        "input", Scope.PIPELINE, "input_id", "this is some data"
    )
    output = EmbeddedDataSource.create("output", Scope.PIPELINE, "output_id", "")
    task = Task(TaskId("task_id"), "task", [input], print, [output])
    pipeline = Pipeline.create_pipeline("name", {"foo": "bar"}, [task])
    model = pipeline.to_model()
    assert model.name == "name"
    assert model.id == pipeline.id
    assert len(model.properties) == 1
    assert model.properties["foo"] == "bar"
    assert model.source_task_edges[input.id] == [task.id]
    assert model.task_source_edges[task.id] == [output.id]
