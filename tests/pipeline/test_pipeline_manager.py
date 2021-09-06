import pytest

from taipy.data.data_source import EmbeddedDataSource
from taipy.data.data_source.models import Scope
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline import Pipeline, PipelineId
from taipy.pipeline.pipeline_manager import PipelineManager
from taipy.task import Task, TaskId
from taipy.task.task_manager import TaskManager


@pytest.fixture(scope="function", autouse=True)
def run_before_and_after_tests():
    pipeline_manager = PipelineManager()
    task_manager = TaskManager()
    task_manager.delete_all()
    pipeline_manager.delete_all()
    yield
    pipeline_manager = PipelineManager()
    pipeline_manager.delete_all()
    task_manager = TaskManager()
    task_manager.delete_all()


def test_save_and_get_pipeline():
    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline(pipeline_id_1, "name_1", {}, [])

    pipeline_id_2 = PipelineId("id2")
    input_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "bar")
    output_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "bar")
    task_2 = Task(TaskId("task_id_2"), "task", [input_2], print, [output_2])
    pipeline_2 = Pipeline(pipeline_id_2, "name_2", {}, [task_2])

    pipeline_3_with_same_id = Pipeline(pipeline_id_1, "name_3", {}, [])

    # No existing Pipeline
    pipeline_manager = PipelineManager()
    assert len(pipeline_manager.get_pipelines()) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_1)
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_2)

    # Save one pipeline. We expect to have only one pipeline stored
    pipeline_manager.save_pipeline(pipeline_1)
    assert len(pipeline_manager.get_pipelines()) == 1
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    with pytest.raises(NonExistingPipeline):
        pipeline_manager.get_pipeline(pipeline_id_2)

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    pipeline_manager.save_pipeline(pipeline_2)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get_task(task_2.id) == task_2

    # We save the first pipeline again. We expect nothing to change
    pipeline_manager.save_pipeline(pipeline_1)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).name == pipeline_1.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get_task(task_2.id) == task_2

    # We save a third pipeline with same id as the first one. We expect the first pipeline to be updated
    pipeline_manager.save_pipeline(pipeline_3_with_same_id)
    assert len(pipeline_manager.get_pipelines()) == 2
    assert pipeline_manager.get_pipeline(pipeline_id_1).id == pipeline_1.id
    assert pipeline_manager.get_pipeline(pipeline_id_1).name == pipeline_3_with_same_id.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_1).tasks) == 0
    assert pipeline_manager.get_pipeline(pipeline_id_2).id == pipeline_2.id
    assert pipeline_manager.get_pipeline(pipeline_id_2).name == pipeline_2.name
    assert len(pipeline_manager.get_pipeline(pipeline_id_2).tasks) == 1
    assert pipeline_manager.task_manager.get_task(task_2.id) == task_2


def test_get_pipeline_schema():
    pipeline_manager = PipelineManager()

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline(pipeline_id_1, "name_1", {}, [])
    pipeline_manager.save_pipeline(pipeline_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = EmbeddedDataSource("input_id_2", "foo", Scope.PIPELINE, {"data": "bar"})
    output_2_1 = EmbeddedDataSource("input_id_2_1", "foo", Scope.PIPELINE, {"data": "bar"})
    output_2_2 = EmbeddedDataSource("input_id_2_2", "foo", Scope.PIPELINE, {"data": "bar"})
    task_2 = Task(TaskId("task_id_2"), "task", [input_2], print, [output_2_1, output_2_2])
    pipeline_2 = Pipeline(pipeline_id_2, "name_2", {}, [task_2])
    pipeline_manager.save_pipeline(pipeline_2)

    schema_1 = pipeline_manager.get_pipeline_schema(pipeline_id_1)
    assert schema_1.id == pipeline_id_1
    assert schema_1.name == pipeline_1.name
    assert schema_1.properties == pipeline_1.properties
    assert schema_1.dag == {}
    schema_2 = pipeline_manager.get_pipeline_schema(pipeline_id_2)
    assert schema_2.id == pipeline_id_2
    assert schema_2.name == pipeline_2.name
    assert schema_2.properties == pipeline_2.properties
    assert schema_2.dag == {input_2.id: [task_2.id], task_2.id: [output_2_1.id, output_2_2.id]}
