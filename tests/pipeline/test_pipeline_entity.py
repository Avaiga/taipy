from taipy.data.data_source_entity import DataSourceEntity
from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.data.scope import Scope
from taipy.pipeline import PipelineEntity, PipelineId
from taipy.task import TaskEntity, TaskId


def test_create_pipeline_entity():
    pipeline = PipelineEntity("name_1", {}, [])
    assert pipeline.id is not None


def test_check_consistency():
    pipeline_1 = PipelineEntity("name_1", {}, [])
    assert pipeline_1.is_consistent

    input_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_id_2", "bar"
    )
    output_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "output_id_2", "bar"
    )
    task_2 = TaskEntity("foo", [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_2 = PipelineEntity("name_2", {}, [task_2])
    assert pipeline_2.is_consistent

    data_source_3 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "data_source_3_id", "bar"
    )
    task_3 = TaskEntity(
        "foo", [data_source_3], print, [data_source_3], TaskId("task_id_3")
    )
    pipeline_3 = PipelineEntity("name_3", {}, [task_3])
    assert not pipeline_3.is_consistent

    input_4 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_4_id", "bar"
    )
    output_4 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "output_4_id", "bar"
    )
    task_4_1 = TaskEntity("foo", [input_4], print, [output_4], TaskId("task_id_4_1"))
    task_4_2 = TaskEntity("foo", [output_4], print, [input_4], TaskId("task_id_4_2"))
    pipeline_4 = PipelineEntity("name_4", {}, [task_4_1, task_4_2])
    assert not pipeline_4.is_consistent

    input_5 = DataSourceEntity("foo", Scope.PIPELINE, "input_id_5")
    output_5 = DataSourceEntity("foo", Scope.PIPELINE, "output_id_5")
    task_5_1 = TaskEntity("foo", [input_5], print, [output_5], TaskId("task_id_5_1"))
    task_5_2 = TaskEntity("foo", [output_5], print, [task_5_1], TaskId("task_id_5_2"))
    pipeline_2 = PipelineEntity("name_2", {}, [task_5_1, task_5_2])
    assert not pipeline_2.is_consistent


def test_to_model():
    input = EmbeddedDataSourceEntity.create(
        "input", Scope.PIPELINE, "input_id", "this is some data"
    )
    output = EmbeddedDataSourceEntity.create("output", Scope.PIPELINE, "output_id", "")
    task = TaskEntity("task", [input], print, [output], TaskId("task_id"))
    pipeline = PipelineEntity("name", {"foo": "bar"}, [task])
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
    task_1 = TaskEntity(
        "grault",
        [data_source_1, data_source_2],
        print,
        [data_source_3, data_source_4],
        TaskId("t1"),
    )
    task_2 = TaskEntity("garply", [data_source_3], print, [data_source_5], TaskId("t2"))
    task_3 = TaskEntity(
        "waldo", [data_source_5, data_source_4], print, [data_source_6], TaskId("t3")
    )
    task_4 = TaskEntity("fred", [data_source_4], print, [data_source_7], TaskId("t4"))
    pipeline = PipelineEntity(
        "plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1")
    )
    assert pipeline.get_sorted_task_entities() == [[task_1], [task_2, task_4], [task_3]]
