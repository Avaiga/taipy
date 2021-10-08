import copy
import os
import tempfile

import pytest

from taipy.configuration import ConfigurationManager
from taipy.configuration.data_manager_configuration import DataManagerConfiguration
from taipy.configuration.task_scheduler_configuration import TaskSchedulerConfiguration
from taipy.exceptions.configuration import LoadingError


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    _env = copy.deepcopy(os.environ)
    yield
    ConfigurationManager.data_manager_configuration = DataManagerConfiguration()
    ConfigurationManager.task_scheduler_configuration = TaskSchedulerConfiguration()
    os.environ = _env


def test_default_configuration():
    tf = NamedTemporaryFile()

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    # Load an empty file
    ConfigurationManager.load(tf.filename)

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None


def test_override_default_configuration():
    tf = NamedTemporaryFile(
        """
[TASK]
parallel_execution = true
[DATA_MANAGER.default]
"""
    )

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    ConfigurationManager.load(tf.filename)

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is True
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None


def test_override_default_configuration_with_multiple_configuration():
    config = NamedTemporaryFile(
        """
[DATA_MANAGER.default]
has_header = true
[DATA_MANAGER.my_datasource]
path = "/data/csv"

[TASK]
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    ConfigurationManager.load(config.filename)

    assert ConfigurationManager.data_manager_configuration["my_datasource"]["has_header"] is True
    assert ConfigurationManager.data_manager_configuration["my_datasource"]["path"] == "/data/csv"
    with pytest.raises(KeyError):
        assert ConfigurationManager.data_manager_configuration["my_datasource"]["not_defined"]
    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is True
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution == 10


def test_node_can_not_appears_twice():
    config = NamedTemporaryFile(
        """
[TASK]
parallel_execution = false
max_number_of_parallel_execution = 40

[TASK]
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    with pytest.raises(LoadingError, match="Can not load configuration"):
        ConfigurationManager.load(config.filename)


def test_write_configuration_file():
    default_config = """
[TASK]
parallel_execution = false
max_number_of_parallel_execution = -1

[DATA_MANAGER.default]
""".strip()
    tf = NamedTemporaryFile()

    ConfigurationManager.export(tf.filename)
    assert tf.read().strip() == default_config

    updated_config = """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = -1

[DATA_MANAGER.my_datasource]
has_header = true
""".strip()

    updated_config_exported = """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = -1

[DATA_MANAGER.default]

[DATA_MANAGER.my_datasource]
has_header = true
    """.strip()

    ConfigurationManager.load(NamedTemporaryFile(updated_config))
    ConfigurationManager.export(tf.filename)

    assert tf.read().strip() == updated_config_exported


def test_configuration_should_be_in_a_node():
    config = NamedTemporaryFile(
        """
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    ConfigurationManager.load(config.filename)

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None


def test_load_from_environment_overwrite_load_from_filename():
    config_from_filename = NamedTemporaryFile(
        """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )
    config_from_environment = NamedTemporaryFile(
        """
[TASK]
max_number_of_parallel_execution = 21
    """
    )

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    os.environ[ConfigurationManager.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    ConfigurationManager.load(config_from_filename.filename)

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is True
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution == 21


class NamedTemporaryFile:
    def __init__(self, content=None):
        with tempfile.NamedTemporaryFile("w", delete=False) as fd:
            if content:
                fd.write(content)
            self.filename = fd.name

    def read(self):
        with open(self.filename, "r") as fp:
            return fp.read()

    def __del__(self):
        os.unlink(self.filename)
