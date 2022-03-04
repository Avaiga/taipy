import os
from unittest import mock

import pytest

from taipy.core.config._config import _Config
from taipy.core.config.config import Config


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config.default_config()


def test_task_config_creation():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    task_config = Config.add_task("tasks1", print, input_config, output_config)

    assert list(Config.tasks) == ["default", task_config.id]

    task2 = Config.add_task("tasks2", print, input_config, output_config)
    assert list(Config.tasks) == ["default", task_config.id, task2.id]


def test_task_count():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    Config.add_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2

    Config.add_task("tasks2", print, input_config, output_config)
    assert len(Config.tasks) == 3

    Config.add_task("tasks3", print, input_config, output_config)
    assert len(Config.tasks) == 4


def test_task_getitem():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    task_id = "tasks1"
    task = Config.add_task(task_id, print, input_config, output_config)

    assert Config.tasks[task_id].id == task.id
    assert Config.tasks[task_id].properties == task.properties
    assert Config.tasks[task_id].function == task.function
    assert Config.tasks[task_id].inputs == task.inputs
    assert Config.tasks[task_id].outputs == task.outputs


def test_task_creation_no_duplication():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    Config.add_task("tasks1", print, input_config, output_config)

    assert len(Config.tasks) == 2

    Config.add_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2


def test_task_config_with_env_variable_value():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")

    with mock.patch.dict(os.environ, {"FOO": "plop", "BAR": "baz"}):
        Config.add_task("task_name", print, input_config, output_config, prop="ENV[BAR]")
        assert Config.tasks["task_name"].prop == "baz"
