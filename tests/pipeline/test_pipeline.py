from taipy.data.data_source import DataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.pipeline import Pipeline, PipelineId
from taipy.task import Task, TaskId


def test_create_pipeline():
    pipeline = Pipeline.create_pipeline("name_1", {}, [])
    assert pipeline.id is not None


def test_check_consistency():
    pipeline_1 = Pipeline.create_pipeline("name_1", {}, [])
    assert pipeline_1.is_consistent

    input_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_id_2", "bar"
    )
    output_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "output_id_2", "bar"
    )
    task_2 = Task(TaskId("task_id_2"), "foo", [input_2], print, [output_2])
    pipeline_2 = Pipeline.create_pipeline("name_2", {}, [task_2])
    assert pipeline_2.is_consistent

    data_source_3 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "data_source_3_id", "bar"
    )
    task_3 = Task(TaskId("task_id_3"), "foo", [data_source_3], print, [data_source_3])
    pipeline_3 = Pipeline.create_pipeline("name_3", {}, [task_3])
    assert not pipeline_3.is_consistent

    input_4 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_4_id", "bar"
    )
    output_4 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "output_4_id", "bar"
    )
    task_4_1 = Task(TaskId("task_id_4_1"), "foo", [input_4], print, [output_4])
    task_4_2 = Task(TaskId("task_id_4_2"), "foo", [output_4], print, [input_4])
    pipeline_4 = Pipeline.create_pipeline("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4.is_consistent

    input_5 = DataSourceEntity("foo", Scope.PIPELINE, "input_id_5")
    output_5 = DataSourceEntity("foo", Scope.PIPELINE, "output_id_5")
    task_5_1 = Task(TaskId("task_id_5_1"), "foo", [input_5], print, [output_5])
    task_5_2 = Task(TaskId("task_id_5_2"), "foo", [output_5], print, [task_5_1])
    pipeline_2 = Pipeline.create_pipeline("name_2", {}, [task_5_1, task_5_2])
    assert not pipeline_2.is_consistent


def test_to_model():
    input = EmbeddedDataSourceEntity.create(
        "input", Scope.PIPELINE, "input_id", "this is some data"
    )
    output = EmbeddedDataSourceEntity.create("output", Scope.PIPELINE, "output_id", "")
    task = Task(TaskId("task_id"), "task", [input], print, [output])
    pipeline = Pipeline.create_pipeline("name", {"foo": "bar"}, [task])
    model = pipeline.to_model()
    assert model.name == "name"
    assert model.id == pipeline.id
    assert len(model.properties) == 1
    assert model.properties["foo"] == "bar"
    assert model.source_task_edges[input.id] == [task.id]
    assert model.task_source_edges[task.id] == [output.id]


def test_get_sorted_tasks():
    data_source_1 = DataSourceEntity("foo", Scope.PIPELINE, "s1")
    data_source_2 = DataSourceEntity("bar", Scope.PIPELINE, "s2")
    data_source_3 = DataSourceEntity("baz", Scope.PIPELINE, "s3")
    data_source_4 = DataSourceEntity("qux", Scope.PIPELINE, "s4")
    data_source_5 = DataSourceEntity("quux", Scope.PIPELINE, "s5")
    data_source_6 = DataSourceEntity("quuz", Scope.PIPELINE, "s6")
    data_source_7 = DataSourceEntity("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        TaskId("t1"),
        "grault",
        [data_source_1, data_source_2],
        print,
        [data_source_3, data_source_4],
    )
    task_2 = Task(TaskId("t2"), "garply", [data_source_3], print, [data_source_5])
    task_3 = Task(
        TaskId("t3"), "waldo", [data_source_5, data_source_4], print, [data_source_6]
    )
    task_4 = Task(TaskId("t4"), "fred", [data_source_4], print, [data_source_7])
    pipeline = Pipeline(PipelineId("p1"), "plugh", {}, [task_4, task_2, task_1, task_3])
    assert pipeline.get_sorted_tasks() == [[task_1], [task_2, task_4], [task_3]]
