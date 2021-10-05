import pytest

from taipy.data import DataSource
from taipy.data.data_source_entity import DataSourceEntity
from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.data.scope import Scope
from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.pipeline import (
    NonExistingPipeline,
    NonExistingPipelineEntity,
)
from taipy.pipeline import Pipeline, PipelineEntity, PipelineId
from taipy.pipeline.manager import PipelineManager
from taipy.task import Task, TaskEntity, TaskId, TaskManager
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

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
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
    input_2 = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, "bar")
    output_2 = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, "bar")
    task_2 = TaskEntity("task", [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_2 = PipelineEntity("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = PipelineEntity("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    pipeline_manager = PipelineManager()
    task_manager = TaskManager()
    assert len(pipeline_manager.get_pipeline_entities()) == 0
    with pytest.raises(NonExistingPipelineEntity):
        pipeline_manager.get_pipeline_entity(pipeline_id_1)
    with pytest.raises(NonExistingPipelineEntity):
        pipeline_manager.get_pipeline_entity(pipeline_id_2)

    # Save one pipeline. We expect to have only one pipeline stored
    pipeline_manager.save_pipeline_entity(pipeline_1)
    assert len(pipeline_manager.get_pipeline_entities()) == 1
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline_entity(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline_entity(pipeline_id_1).task_entities) == 0
    with pytest.raises(NonExistingPipelineEntity):
        pipeline_manager.get_pipeline_entity(pipeline_id_2)

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    task_manager.save_task_entity(task_2)
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

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
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
    pipeline_entity = PipelineEntity(
        "plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1")
    )

    pipeline_manager = PipelineManager()
    task_manager = TaskManager()

    class MockTaskScheduler(TaskScheduler):
        submit_calls = []

        def submit(self, task: TaskEntity):
            self.submit_calls.append(task)
            return None

    pipeline_manager.task_scheduler = MockTaskScheduler()

    # pipeline does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingPipelineEntity):
        pipeline_manager.submit(pipeline_entity.id)

    # pipeline does exist, but tasks does not exist. We expect an exception to be raised
    pipeline_manager.save_pipeline_entity(pipeline_entity)
    with pytest.raises(NonExistingTaskEntity):
        pipeline_manager.submit(pipeline_entity.id)

    # pipeline, and tasks does exist. We expect the tasks to be submitted
    # in a specific order
    task_manager.save_task_entity(task_1)
    task_manager.save_task_entity(task_2)
    task_manager.save_task_entity(task_3)
    task_manager.save_task_entity(task_4)

    pipeline_manager.submit(pipeline_entity.id)
    assert pipeline_manager.task_scheduler.submit_calls == [
        task_1,
        task_2,
        task_4,
        task_3,
    ]


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_pipeline_manager_only_creates_intermediate_data_source_entity_once():
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = task_manager.data_manager
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSource("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSource("bar", "embedded", Scope.PIPELINE, data=0)
    ds_6 = DataSource("baz", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = Task("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = Task("mult by 3", [ds_2], mult_by_3, ds_6)
    pipeline = Pipeline("by 6", [task_mult_by_2, task_mult_by_3])
    pipeline_manager.register_pipeline(pipeline)
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6

    assert len(data_manager.get_data_source_entities()) == 0
    assert len(task_manager.task_entities) == 0

    pipeline_entity = pipeline_manager.create_pipeline_entity(pipeline)

    assert len(data_manager.get_data_source_entities()) == 3
    assert len(task_manager.task_entities) == 2
    assert len(pipeline_entity.get_sorted_task_entities()) == 2
    assert pipeline_entity.foo.get() == 1
    assert pipeline_entity.bar.get() == 0
    assert pipeline_entity.baz.get() == 0
    assert pipeline_entity.get_sorted_task_entities()[0][0].name == task_mult_by_2.name
    assert pipeline_entity.get_sorted_task_entities()[1][0].name == task_mult_by_3.name


def test_get_set_data():
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = task_manager.data_manager
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSource("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSource("bar", "embedded", Scope.PIPELINE, data=0)
    ds_6 = DataSource("baz", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = Task("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = Task("mult by 3", [ds_2], mult_by_3, ds_6)
    pipeline = Pipeline("by 6", [task_mult_by_2, task_mult_by_3])
    pipeline_manager.register_pipeline(pipeline)
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6

    pipeline_entity = pipeline_manager.create_pipeline_entity(pipeline)

    assert pipeline_entity.foo.get() == 1
    assert pipeline_entity.bar.get() == 0
    assert pipeline_entity.baz.get() == 0

    pipeline_manager.submit(pipeline_entity.id)
    assert pipeline_entity.foo.get() == 1
    assert pipeline_entity.bar.get() == 2
    assert pipeline_entity.baz.get() == 6

    pipeline_entity.foo.write("new data value")
    assert pipeline_entity.foo.get() == "new data value"
    assert pipeline_entity.bar.get() == 2
    assert pipeline_entity.baz.get() == 6

    pipeline_entity.bar.write(7)
    assert pipeline_entity.foo.get() == "new data value"
    assert pipeline_entity.bar.get() == 7
    assert pipeline_entity.baz.get() == 6

    with pytest.raises(AttributeError):
        pipeline_entity.WRONG.write(7)
