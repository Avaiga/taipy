import pytest

from taipy.config import Config
from taipy.config.task import TaskConfigs


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config.task_configs = TaskConfigs()


def test_task_creation():
    task = Config.task_configs.create("tasks1", "input", print, "output")

    assert list(Config.task_configs) == [task]

    task2 = Config.task_configs.create("tasks2", "input", print, "output")
    assert list(Config.task_configs) == [task, task2]


def test_task_count():
    Config.task_configs.create("tasks1", "input", print, "output")
    assert len(Config.task_configs) == 1

    Config.task_configs.create("tasks2", "input", print, "output")
    assert len(Config.task_configs) == 2

    Config.task_configs.create("tasks3", "input", print, "output")
    assert len(Config.task_configs) == 3


def test_task_getitem():
    task_name = "tasks1"
    task = Config.task_configs.create(task_name, "input", print, "output")

    assert Config.task_configs[task_name] == task


def test_task_creation_no_duplication():
    Config.task_configs.create("tasks1", "input", print, "output")

    assert len(Config.task_configs) == 1

    Config.task_configs.create("tasks1", "input", print, "output")
    assert len(Config.task_configs) == 1
