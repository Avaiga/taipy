import pytest

from taipy.config import DataSourceConfig, TaskConfig
from taipy.data import EmbeddedDataSource, Scope
from taipy.exceptions.task import NonExistingTask
from taipy.task import Task, TaskId
from taipy.task.manager.task_manager import TaskManager


def test_save_and_get_task_entity():

    task_id_1 = TaskId("id1")
    first_task = Task("name_1", [], print, [], task_id_1)
    task_id_2 = TaskId("id2")
    second_task = Task("name_2", [], print, [], task_id_2)
    third_task_with_same_id_as_first_task = Task("name_is_not_1_anymore", [], print, [], task_id_1)

    # No task at initialization
    task_manager = TaskManager()
    task_manager.delete_all()
    assert len(task_manager.tasks) == 0
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_1)
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_2)

    # Save one task. We expect to have only one task stored
    task_manager.save(first_task)
    assert len(task_manager.tasks) == 1
    assert task_manager.get_task(task_id_1) == first_task
    with pytest.raises(NonExistingTask):
        task_manager.get_task(task_id_2)

    # Save a second task. Now, we expect to have a total of two tasks stored
    task_manager.save(second_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == first_task
    assert task_manager.get_task(task_id_2) == second_task

    # We save the first task again. We expect nothing to change
    task_manager.save(first_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == first_task
    assert task_manager.get_task(task_id_2) == second_task

    # We save a third task with same id as the first one.
    # We expect the first task to be updated
    task_manager.save(third_task_with_same_id_as_first_task)
    assert len(task_manager.tasks) == 2
    assert task_manager.get_task(task_id_1) == third_task_with_same_id_as_first_task
    assert task_manager.get_task(task_id_1) != first_task
    assert task_manager.get_task(task_id_2) == second_task


def test_ensure_conservation_of_order_of_data_sources_on_task_entity_creation():
    task_manager = TaskManager()
    task_manager.delete_all()

    embedded_1 = DataSourceConfig("embedded_1", "embedded")
    embedded_2 = DataSourceConfig("embedded_2", "embedded")
    embedded_3 = DataSourceConfig("a_embedded_3", "embedded")
    embedded_4 = DataSourceConfig("embedded_4", "embedded")
    embedded_5 = DataSourceConfig("1_embedded_4", "embedded")

    input = [embedded_1, embedded_2, embedded_3]
    output = [embedded_4, embedded_5]
    task = TaskConfig("name_1", input, print, output)
    task_entity = task_manager.create(task, None)

    assert [i.config_name for i in task_entity.input.values()] == [embedded_1.name, embedded_2.name, embedded_3.name]
    assert [o.config_name for o in task_entity.output.values()] == [embedded_4.name, embedded_5.name]

    data_source_entities = {
        embedded_1: EmbeddedDataSource(embedded_1.name, Scope.PIPELINE),
        embedded_2: EmbeddedDataSource(embedded_2.name, Scope.PIPELINE),
        embedded_3: EmbeddedDataSource(embedded_3.name, Scope.PIPELINE),
        embedded_4: EmbeddedDataSource(embedded_4.name, Scope.PIPELINE),
        embedded_5: EmbeddedDataSource(embedded_5.name, Scope.PIPELINE),
    }

    task = TaskConfig("name_2", input, print, output)
    task_entity = task_manager.create(task, data_source_entities)

    assert [i.config_name for i in task_entity.input.values()] == [embedded_1.name, embedded_2.name, embedded_3.name]
    assert [o.config_name for o in task_entity.output.values()] == [embedded_4.name, embedded_5.name]
