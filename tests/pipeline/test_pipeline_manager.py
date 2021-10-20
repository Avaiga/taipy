from unittest import mock

import pytest

from taipy.config import DataSourceConfig, PipelineConfig, TaskConfig
from taipy.data import InMemoryDataSource
from taipy.data.data_source import DataSource
from taipy.data.in_memory import InMemoryDataSource
from taipy.data.scope import Scope
from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipelineConfig, NonExistingPipeline
from taipy.pipeline import Pipeline, PipelineConfig
from taipy.common.alias import PipelineId, TaskId
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline import Pipeline, PipelineId
from taipy.pipeline.manager import PipelineManager
from taipy.task import Task, TaskConfig, TaskManager
from taipy.task import Task, TaskId, TaskManager
from taipy.task.scheduler import TaskScheduler


def test_save_and_get_pipeline_entity():
    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataSource.create("foo", Scope.PIPELINE, None, "bar")
    output_2 = InMemoryDataSource.create("foo", Scope.PIPELINE, None, "bar")
    task_2 = Task("task", [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = Pipeline("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    pipeline_manager = PipelineManager()
    task_manager = TaskManager()
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_1)
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_2)

    # Save one pipeline. We expect to have only one pipeline stored
    pipeline_manager.save(pipeline_1)
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_2)

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    task_manager.save(task_2)
    pipeline_manager.save(pipeline_2)
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get(task_2.id) == task_2

    # We save the first pipeline again. We expect nothing to change
    pipeline_manager.save(pipeline_1)
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get(task_2.id) == task_2

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    pipeline_manager.save(pipeline_3_with_same_id)
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).config_name == pipeline_3_with_same_id.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get(task_2.id) == task_2


def test_submit():
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
    pipeline_entity = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))

    pipeline_manager = PipelineManager()
    task_manager = TaskManager()

    class MockTaskScheduler(TaskScheduler):
        submit_calls = []

        def submit(self, task: Task, callbacks=None):
            self.submit_calls.append(task)
            return None

    pipeline_manager.task_scheduler = MockTaskScheduler()

    # pipeline does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.submit(pipeline_entity.id)

    # pipeline does exist, but tasks does not exist. We expect an exception to be raised
    pipeline_manager.save(pipeline_entity)
    with pytest.raises(NonExistingTask):
        pipeline_manager.submit(pipeline_entity.id)

    # pipeline, and tasks does exist. We expect the tasks to be submitted
    # in a specific order
    task_manager.save(task_1)
    task_manager.save(task_2)
    task_manager.save(task_3)
    task_manager.save(task_4)

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

    ds_1 = DataSourceConfig("foo", "in_memory", Scope.PIPELINE, data=1)
    ds_2 = DataSourceConfig("bar", "in_memory", Scope.PIPELINE, data=0)
    ds_6 = DataSourceConfig("baz", "in_memory", Scope.PIPELINE, data=0)

    task_mult_by_2 = TaskConfig("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = TaskConfig("mult by 3", [ds_2], mult_by_3, ds_6)
    pipeline = PipelineConfig("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6

    assert len(data_manager.get_all()) == 0
    assert len(task_manager.tasks) == 0

    pipeline_entity = pipeline_manager.create(pipeline)

    assert len(data_manager.get_all()) == 3
    assert len(task_manager.tasks) == 2
    assert len(pipeline_entity.get_sorted_tasks()) == 2
    assert pipeline_entity.foo.get() == 1
    assert pipeline_entity.bar.get() == 0
    assert pipeline_entity.baz.get() == 0
    assert pipeline_entity.get_sorted_tasks()[0][0].config_name == task_mult_by_2.name
    assert pipeline_entity.get_sorted_tasks()[1][0].config_name == task_mult_by_3.name


def test_get_set_data():
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = task_manager.data_manager
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSourceConfig("foo", "in_memory", Scope.PIPELINE, data=1)
    ds_2 = DataSourceConfig("bar", "in_memory", Scope.PIPELINE, data=0)
    ds_6 = DataSourceConfig("baz", "in_memory", Scope.PIPELINE, data=0)

    task_mult_by_2 = TaskConfig("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = TaskConfig("mult by 3", [ds_2], mult_by_3, ds_6)
    pipeline = PipelineConfig("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6

    pipeline_entity = pipeline_manager.create(pipeline)

    assert pipeline_entity.foo.get() == 1  # Default values
    assert pipeline_entity.bar.get() == 0  # Default values
    assert pipeline_entity.baz.get() == 0  # Default values

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


def test_subscription():
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = task_manager.data_manager
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    pipeline_config = PipelineConfig(
        "by 6",
        [
            TaskConfig(
                "mult by 2",
                [DataSourceConfig("foo", "in_memory", Scope.PIPELINE, data=1)],
                mult_by_2,
                DataSourceConfig("bar", "in_memory", Scope.PIPELINE, data=0),
            )
        ],
    )

    pipeline = pipeline_manager.create(pipeline_config)

    callback = mock.MagicMock()
    pipeline_manager.submit(pipeline.id, [callback])
    callback.assert_called()
