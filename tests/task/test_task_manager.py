import pytest

from taipy.exceptions.task import NonExistingTask
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
    task_manager = TaskManager()
    task_manager.delete_all()
    pipeline_manager.delete_all()


def test_save_and_get_task():

    task_id_1 = TaskId("id1")
    first_task = Task(task_id_1, "name_1", [], print, [])
    task_id_2 = TaskId("id2")
    second_task = Task(task_id_2, "name_2", [], print, [])
    third_task_with_same_id_as_first_task = Task(task_id_1, "name_is_not_1_anymore", [], print, [])

    # No task at initialization
    task_manager = TaskManager()
    task_manager.delete_all()
    assert len(task_manager.tasks) == 0
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_1)
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_2)

    # Save one task. We expect to have only one task stored
    task_manager.save_task(first_task)
    assert len(task_manager.tasks) == 1
    assert task_manager.get_task(task_id_1) == first_task
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_2)

    # Save a second task. Now, we expect to have a total of two tasks stored
    task_manager.save_task(second_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == first_task
    assert task_manager.get_task(task_id_2) == second_task

    # We save the first task again. We expect nothing to change
    task_manager.save_task(first_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == first_task
    assert task_manager.get_task(task_id_2) == second_task

    # We save a third task with same id as the first one. We expect the first task to be updated
    task_manager.save_task(third_task_with_same_id_as_first_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == third_task_with_same_id_as_first_task
    assert task_manager.get_task(task_id_2) == second_task
