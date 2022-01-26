import pytest

from taipy.config._config import _Config
from taipy.config.config import Config


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_config = _Config()
    Config._applied_config = _Config.default_config()


def test_task_config_creation():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    task_config = Config.add_task("tasks1", input_config, print, output_config)

    assert list(Config.tasks()) == ["default", task_config.name]

    task2 = Config.add_task("tasks2", input_config, print, output_config)
    assert list(Config.tasks()) == ["default", task_config.name, task2.name]


def test_task_count():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    Config.add_task("tasks1", input_config, print, output_config)
    assert len(Config.tasks()) == 2

    Config.add_task("tasks2", input_config, print, output_config)
    assert len(Config.tasks()) == 3

    Config.add_task("tasks3", input_config, print, output_config)
    assert len(Config.tasks()) == 4


def test_task_getitem():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    task_name = "tasks1"
    task = Config.add_task(task_name, input_config, print, output_config)

    assert Config.tasks()[task_name].name == task.name
    assert Config.tasks()[task_name].properties == task.properties
    assert Config.tasks()[task_name].function == task.function
    assert Config.tasks()[task_name].inputs == task.inputs
    assert Config.tasks()[task_name].outputs == task.outputs


def test_task_creation_no_duplication():
    input_config = Config.add_data_node("input")
    output_config = Config.add_data_node("output")
    Config.add_task("tasks1", input_config, print, output_config)

    assert len(Config.tasks()) == 2

    Config.add_task("tasks1", input_config, print, output_config)
    assert len(Config.tasks()) == 2
