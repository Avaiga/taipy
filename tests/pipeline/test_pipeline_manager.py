import pytest

from taipy.data import DataSource
from taipy.data.data_source_entity import DataSourceEntity
from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.data.scope import Scope
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline import Pipeline, PipelineEntity, PipelineId
from taipy.pipeline.manager.pipeline_manager import PipelineManager
from taipy.task import Task, TaskEntity, TaskId
from taipy.task.scheduler import TaskScheduler


def test_register_and_get_pipeline():
    name_1 = "name_1"
    pipeline_1 = Pipeline(name_1, [])

    input_2 = DataSource("foo", "embedded", data="bar")
    output_2 = DataSource("foo", "embedded", data="bar")
    task_2 = Task("task", [input_2], print, [output_2])
    name_2 = "name_2"
    pipeline_2 = Pipeline(name_2, [task_2])

    pipeline_3_with_same_name = Pipeline(name_1, [], description="my description")

    # No existing Pipeline
    pipeline_manager = PipelineManager()
    assert len(pipeline_manager.get_pipelines()) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(name_1)
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(name_2)

    # Save one pipeline. We expect to have only one pipeline stored
    pipeline_manager.register_pipeline(pipeline_1)
    assert len(pipeline_manager.get_pipelines()) == 1
    assert pipeline_manager.get_pipeline(name_1) == pipeline_1
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(name_2)

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    pipeline_manager.register_pipeline(pipeline_2)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(name_1) == pipeline_1
    assert pipeline_manager.get_pipeline(name_2) == pipeline_2

    # We save the first pipeline again. We expect nothing to change
    pipeline_manager.register_pipeline(pipeline_1)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(name_1) == pipeline_1
    assert pipeline_manager.get_pipeline(name_2) == pipeline_2
    assert pipeline_manager.get_pipeline(name_1).properties.get("description") is None

    # We save a third pipeline with same id as the first one. We expect the first pipeline to be updated
    pipeline_manager.register_pipeline(pipeline_3_with_same_name)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(name_1) == pipeline_3_with_same_name
    assert pipeline_manager.get_pipeline(name_2) == pipeline_2
    assert pipeline_manager.get_pipeline(name_1).properties.get(
        "description"
    ) == pipeline_3_with_same_name.properties.get("description")


def test_save_and_get_pipeline_entity():
    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = PipelineEntity("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_2_id", "bar"
    )
    output_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "output_2_id", "bar"
    )
    task_2 = TaskEntity("task", [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_2 = PipelineEntity("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = PipelineEntity("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    pipeline_manager = PipelineManager()
    assert len(pipeline_manager.get_pipeline_entities()) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline_entity(pipeline_id_1)
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline_entity(pipeline_id_2)

    # Save one pipeline. We expect to have only one pipeline stored
    pipeline_manager.save_pipeline_entity(pipeline_1)
    assert len(pipeline_manager.get_pipeline_entities()) == 1
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_1).task_entities) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline_entity(pipeline_id_2)

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    pipeline_manager.save_pipeline_entity(pipeline_2)
    assert len(pipeline_manager.get_pipeline_entities()) == 2
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_1).task_entities) == 0
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_2).task_entities) == 1
    assert pipeline_manager.task_manager.get_task_entity(task_2.id) == task_2

    # We save the first pipeline again. We expect nothing to change
    pipeline_manager.save_pipeline_entity(pipeline_1)
    assert len(pipeline_manager.get_pipeline_entities()) == 2
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_1).task_entities) == 0
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_2).task_entities) == 1
    assert pipeline_manager.task_manager.get_task_entity(task_2.id) == task_2

    # We save a third pipeline with same id as the first one. We expect the first pipeline to be updated
    pipeline_manager.save_pipeline_entity(pipeline_3_with_same_id)
    assert len(pipeline_manager.get_pipeline_entities()) == 2
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).id == pipeline_1.id
    assert (
        pipeline_manager.get_pipeline_entity(pipeline_id_1).name
        == pipeline_3_with_same_id.name
    )
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_1).task_entities) == 0
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_2).task_entities) == 1
    assert pipeline_manager.task_manager.get_task_entity(task_2.id) == task_2


def test_get_pipeline_schema():
    pipeline_manager = PipelineManager()

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = PipelineEntity("name_1", {}, [], pipeline_id_1)
    pipeline_manager.save_pipeline_entity(pipeline_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_id_2", "bar"
    )
    output_2_1 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_id_2_1", "bar"
    )
    output_2_2 = EmbeddedDataSourceEntity.create(
        "foo", Scope.PIPELINE, "input_id_2_2", "bar"
    )
    task_2 = TaskEntity(
        "task", [input_2], print, [output_2_1, output_2_2], TaskId("task_id_2")
    )
    pipeline_2 = PipelineEntity("name_2", {}, [task_2], pipeline_id_2)
    pipeline_manager.save_pipeline_entity(pipeline_2)

    schema_1 = pipeline_manager.get_pipeline_schema(pipeline_id_1)
    assert schema_1.id == pipeline_id_1
    assert schema_1.name == pipeline_1.name
    assert schema_1.properties == pipeline_1.properties
    assert schema_1.dag == {}
    schema_2 = pipeline_manager.get_pipeline_schema(pipeline_id_2)
    assert schema_2.id == pipeline_id_2
    assert schema_2.name == pipeline_2.name
    assert schema_2.properties == pipeline_2.properties
    assert schema_2.dag == {
        input_2.id: [task_2.id],
        task_2.id: [output_2_1.id, output_2_2.id],
    }


def test_submit():
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

    pipeline_manager = PipelineManager()

    class MockTaskScheduler(TaskScheduler):
        submit_calls = []

        def submit(self, task: TaskEntity):
            self.submit_calls.append(task)
            return None

    pipeline_manager.task_scheduler = MockTaskScheduler()

    # pipeline does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.submit(pipeline.id)

    # pipeline does exist. we expect the tasks to be submitted in a specific order
    pipeline_manager.save_pipeline_entity(pipeline)
    pipeline_manager.submit(pipeline.id)
    assert pipeline_manager.task_scheduler.submit_calls == [
        task_1,
        task_2,
        task_4,
        task_3,
    ]
