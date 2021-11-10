import pytest

from taipy.common.alias import TaskId
from taipy.config import Config, DataSourceConfig, TaskConfig
from taipy.data import InMemoryDataSource, Scope
from taipy.data.manager import DataManager
from taipy.exceptions.task import NonExistingTask
from taipy.task import Task
from taipy.task.manager.task_manager import TaskManager


def test_create_and_persist():
    tm = TaskManager()
    dm = DataManager()
    input_configs = [Config.data_source_configs.create("my_input", "in_memory")]
    output_configs = Config.data_source_configs.create("my_output", "in_memory")
    task_config = Config.task_configs.create("foo", input_configs, print, output_configs)
    task = tm.create(task_config)
    assert task.id is not None
    assert task.config_name == "foo"
    assert len(task.input) == 1
    assert len(dm.get_all()) == 2
    assert task.my_input.id is not None
    assert task.my_input.config_name == "my_input"
    assert task.my_output.id is not None
    assert task.my_output.config_name == "my_output"
    assert task.function == print

    task_retrieved_from_manager = TaskManager().get(task.id)
    assert task_retrieved_from_manager.id == task.id
    assert task_retrieved_from_manager.config_name == task.config_name
    assert len(task_retrieved_from_manager.input) == len(task.input)
    assert task_retrieved_from_manager.my_input.id is not None
    assert task_retrieved_from_manager.my_input.config_name == task.my_input.config_name
    assert task_retrieved_from_manager.my_output.id is not None
    assert task_retrieved_from_manager.my_output.config_name == task.my_output.config_name
    assert task_retrieved_from_manager.function == task.function


def test_do_not_recreate_existing_data_source():
    tm = TaskManager()
    dm = DataManager()
    input_config = Config.data_source_configs.create("my_input", "in_memory")
    output_config = Config.data_source_configs.create("my_output", "in_memory")

    dm._create_and_save_data_source(input_config, "pipeline_id")
    assert len(dm.get_all()) == 1

    task_config = Config.task_configs.create("foo", input_config, print, output_config)
    tm.create(task_config, pipeline_id="pipeline_id")
    assert len(dm.get_all()) == 2


def test_do_not_recreate_existing_task():
    tm = TaskManager()
    input_config_scope_pipeline = Config.data_source_configs.create("my_input", "in_memory")
    output_config_scope_pipeline = Config.data_source_configs.create("my_output", "in_memory")
    task_config = Config.task_configs.create("foo", input_config_scope_pipeline, print, output_config_scope_pipeline)
    task_1 = tm.create(task_config)
    task_2 = tm.create(task_config)
    assert task_1.id != task_2.id
    assert len(tm.get_all()) == 2
    task_3 = tm.create(task_config, "whatever_scenario", "pipeline_1")
    # task_4 = tm.create(task_config, "other_scenario", "pipeline_1")  # Do not recreate a task since it already exists
    task_5 = tm.create(task_config, "pipeline_2")
    # assert task_3.id == task_4.id
    assert task_3.id != task_5.id
    # assert len(tm.get_all()) == 4

    input_config_scope_scenario = Config.data_source_configs.create("my_input", "in_memory", Scope.SCENARIO)
    output_config_scope_scenario = Config.data_source_configs.create("my_output", "in_memory", Scope.SCENARIO)
    task_config_2 = Config.task_configs.create("bar", input_config_scope_scenario, print, output_config_scope_scenario)
    # task_6 = tm.create(task_config_2)
    # task_7 = tm.create(task_config_2)
    # assert task_6.id == task_7.id
    # assert len(tm.get_all()) == 6
    task_8 = tm.create(task_config_2, "scenario_1", "pipeline")
    # task_9 = tm.create(task_config_2, "scenario_1", "pipeline_2")  # Do not recreate a task since it already exists
    task_10 = tm.create(task_config_2, "scenario_2", "pipeline_3")
    # assert task_8.id == task_9.id
    assert task_8.id != task_10.id
    # assert len(tm.get_all()) == 8


def test_set_and_get_task():
    task_id_1 = TaskId("id1")
    first_task = Task("name_1", [], print, [], task_id_1)
    task_id_2 = TaskId("id2")
    second_task = Task("name_2", [], print, [], task_id_2)
    third_task_with_same_id_as_first_task = Task("name_is_not_1_anymore", [], print, [], task_id_1)

    # No task at initialization
    task_manager = TaskManager()
    task_manager.delete_all()
    assert len(task_manager.get_all()) == 0
    with pytest.raises(NonExistingTask):
        task_manager.get(task_id_1)
    with pytest.raises(NonExistingTask):
        task_manager.get(task_id_2)

    # Save one task. We expect to have only one task stored
    task_manager.set(first_task)
    assert len(task_manager.get_all()) == 1
    assert task_manager.get(task_id_1).id == first_task.id
    with pytest.raises(NonExistingTask):
        task_manager.get(task_id_2)

    # Save a second task. Now, we expect to have a total of two tasks stored
    task_manager.set(second_task)
    assert len(task_manager.get_all()) == 2
    assert task_manager.get(task_id_1).id == first_task.id
    assert task_manager.get(task_id_2).id == second_task.id

    # We save the first task again. We expect nothing to change
    task_manager.set(first_task)
    assert len(task_manager.get_all()) == 2
    assert task_manager.get(task_id_1).id == first_task.id
    assert task_manager.get(task_id_2).id == second_task.id

    # We save a third task with same id as the first one.
    # We expect the first task to be updated
    task_manager.set(third_task_with_same_id_as_first_task)
    assert len(task_manager.get_all()) == 2
    assert task_manager.get(task_id_1).id == third_task_with_same_id_as_first_task.id
    assert task_manager.get(task_id_1).config_name != first_task.config_name
    assert task_manager.get(task_id_2).id == second_task.id


def test_ensure_conservation_of_order_of_data_sources_on_task_creation():
    task_manager = TaskManager()
    task_manager.delete_all()

    embedded_1 = DataSourceConfig("ds_1", "in_memory")
    embedded_2 = DataSourceConfig("ds_2", "in_memory")
    embedded_3 = DataSourceConfig("a_ds_3", "in_memory")
    embedded_4 = DataSourceConfig("ds_4", "in_memory")
    embedded_5 = DataSourceConfig("1_ds_4", "in_memory")

    input = [embedded_1, embedded_2, embedded_3]
    output = [embedded_4, embedded_5]
    task_config = TaskConfig("name_1", input, print, output)
    task = task_manager.create(task_config)

    assert [i.config_name for i in task.input.values()] == [embedded_1.name, embedded_2.name, embedded_3.name]
    assert [o.config_name for o in task.output.values()] == [embedded_4.name, embedded_5.name]

    data_sources = {
        embedded_1: InMemoryDataSource(embedded_1.name, Scope.PIPELINE),
        embedded_2: InMemoryDataSource(embedded_2.name, Scope.PIPELINE),
        embedded_3: InMemoryDataSource(embedded_3.name, Scope.PIPELINE),
        embedded_4: InMemoryDataSource(embedded_4.name, Scope.PIPELINE),
        embedded_5: InMemoryDataSource(embedded_5.name, Scope.PIPELINE),
    }

    task_config = TaskConfig("name_2", input, print, output)
    task = task_manager.create(task_config, data_sources)

    assert [i.config_name for i in task.input.values()] == [embedded_1.name, embedded_2.name, embedded_3.name]
    assert [o.config_name for o in task.output.values()] == [embedded_4.name, embedded_5.name]
