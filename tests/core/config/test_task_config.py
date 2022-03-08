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
    Config._applied_config = _Config._default_config()


def test_task_config_creation():
    input_config = Config._add_data_node("input")
    output_config = Config._add_data_node("output")
    task_config = Config._add_task("tasks1", print, input_config, output_config)

    assert list(Config.tasks) == ["default", task_config.id]

    task2 = Config._add_task("tasks2", print, input_config, output_config)
    assert list(Config.tasks) == ["default", task_config.id, task2.id]


def test_task_count():
    input_config = Config._add_data_node("input")
    output_config = Config._add_data_node("output")
    Config._add_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2

    Config._add_task("tasks2", print, input_config, output_config)
    assert len(Config.tasks) == 3

    Config._add_task("tasks3", print, input_config, output_config)
    assert len(Config.tasks) == 4


def test_task_getitem():
    input_config = Config._add_data_node("input")
    output_config = Config._add_data_node("output")
    task_id = "tasks1"
    task_cfg = Config._add_task(task_id, print, input_config, output_config)

    assert Config.tasks[task_id].id == task_cfg.id
    assert Config.tasks[task_id].properties == task_cfg.properties
    assert Config.tasks[task_id].function == task_cfg.function
    assert Config.tasks[task_id].input_configs == task_cfg.input_configs
    assert Config.tasks[task_id].output_configs == task_cfg.output_configs


def test_task_creation_no_duplication():
    input_config = Config._add_data_node("input")
    output_config = Config._add_data_node("output")
    Config._add_task("tasks1", print, input_config, output_config)

    assert len(Config.tasks) == 2

    Config._add_task("tasks1", print, input_config, output_config)
    assert len(Config.tasks) == 2


def test_task_config_with_env_variable_value():
    input_config = Config._add_data_node("input")
    output_config = Config._add_data_node("output")

    with mock.patch.dict(os.environ, {"FOO": "plop", "BAR": "baz"}):
        Config._add_task("task_name", print, input_config, output_config, prop="ENV[BAR]")
        assert Config.tasks["task_name"].prop == "baz"
