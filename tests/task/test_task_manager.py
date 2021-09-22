import pytest

from taipy.exceptions.task import NonExistingTask, NonExistingTaskEntity
from taipy.task import Task, TaskEntity, TaskId
from taipy.task.manager.task_manager import TaskManager


def test_register_and_get_task():

    name_1 = "name_1"
    first_task = Task(name_1, [], print, [])
    name_2 = "name_2"
    second_task = Task(name_2, [], print, [])
    third_task_with_same_name_as_first_task = Task(name_1, [], len, [])

    # No task at initialization
    task_manager = TaskManager()
    task_manager.delete_all()
    assert len(task_manager.get_tasks()) == 0
    with pytest.raises(NonExistingTask):
        task_manager.get_task(name_1)
    with pytest.raises(NonExistingTask):
        task_manager.get_task(name_2)

    # Save one task. We expect to have only one task stored
    task_manager.register_task(first_task)
    assert len(task_manager.get_tasks()) == 1
    assert task_manager.get_task(name_1) == first_task
    with pytest.raises(NonExistingTask):
        task_manager.get_task(name_2)

    # Save a second task. Now, we expect to have a total of two tasks stored
    task_manager.register_task(second_task)
    assert len(task_manager.get_tasks()) == 2
    assert task_manager.get_task(name_1) == first_task
    assert task_manager.get_task(name_2) == second_task

    # We save the first task again. We expect nothing to change
    task_manager.register_task(first_task)
    assert len(task_manager.get_tasks()) == 2
    assert task_manager.get_task(name_1) == first_task
    assert task_manager.get_task(name_2) == second_task

    # We save a third task with same name as the first one.
    # We expect the first task to be updated
    task_manager.register_task(third_task_with_same_name_as_first_task)
    assert len(task_manager.get_tasks()) == 2
    assert task_manager.get_task(name_1) == third_task_with_same_name_as_first_task
    assert task_manager.get_task(name_1) != first_task
    assert task_manager.get_task(name_2) == second_task


def test_save_and_get_task_entity():

    task_id_1 = TaskId("id1")
    first_task = TaskEntity("name_1", [], print, [], task_id_1)
    task_id_2 = TaskId("id2")
    second_task = TaskEntity("name_2", [], print, [], task_id_2)
    third_task_with_same_id_as_first_task = TaskEntity(
        "name_is_not_1_anymore", [], print, [], task_id_1
    )

    # No task at initialization
    task_manager = TaskManager()
    task_manager.delete_all()
    assert len(task_manager.task_entities) == 0
    with pytest.raises(NonExistingTaskEntity):
        task_manager.get_task_entity(task_id_1)
    with pytest.raises(NonExistingTaskEntity):
        task_manager.get_task_entity(task_id_2)

    # Save one task. We expect to have only one task stored
    task_manager.save_task_entity(first_task)
    assert len(task_manager.task_entities) == 1
    assert task_manager.get_task_entity(task_id_1) == first_task
    with pytest.raises(NonExistingTaskEntity):
        task_manager.get_task_entity(task_id_2)

    # Save a second task. Now, we expect to have a total of two tasks stored
    task_manager.save_task_entity(second_task)
    assert len(task_manager.task_entities) == 2
    assert task_manager.get_task_entity(task_id_1) == first_task
    assert task_manager.get_task_entity(task_id_2) == second_task

    # We save the first task again. We expect nothing to change
    task_manager.save_task_entity(first_task)
    assert len(task_manager.task_entities) == 2
    assert task_manager.get_task_entity(task_id_1) == first_task
    assert task_manager.get_task_entity(task_id_2) == second_task

    # We save a third task with same id as the first one.
    # We expect the first task to be updated
    task_manager.save_task_entity(third_task_with_same_id_as_first_task)
    assert len(task_manager.task_entities) == 2
    assert (
        task_manager.get_task_entity(task_id_1) == third_task_with_same_id_as_first_task
    )
    assert task_manager.get_task_entity(task_id_1) != first_task
    assert task_manager.get_task_entity(task_id_2) == second_task
