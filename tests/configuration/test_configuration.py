import copy
import os
import tempfile

import pytest

from taipy.config import Config
from taipy.config.data_source_serializer import DataSourceSerializer
from taipy.config.scenario import ScenariosRepository
from taipy.config.task_scheduler import TaskScheduler
from taipy.exceptions.configuration import LoadingError


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    _env = copy.deepcopy(os.environ)
    yield
    Config._data_source_serializer = DataSourceSerializer()
    Config.task_scheduler_configs = TaskScheduler()
    Config.scenario_configs = ScenariosRepository()
    os.environ = _env


def test_default_configuration():
    tf = NamedTemporaryFile()

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None

    # Load an empty file
    Config.load(tf.filename)

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None


def test_override_default_configuration():
    tf = NamedTemporaryFile(
        """
[TASK]
parallel_execution = true
[DATA_SOURCE.default]
"""
    )

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None

    Config.load(tf.filename)

    assert Config.task_scheduler_configs.parallel_execution is True
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None


def test_override_default_configuration_with_multiple_configuration():
    config = NamedTemporaryFile(
        """
[DATA_SOURCE.default]
has_header = true
[DATA_SOURCE.my_datasource]
path = "/data/csv"

[TASK]
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None

    Config.load(config.filename)

    assert Config._data_source_serializer["my_datasource"]["has_header"] is True
    assert Config._data_source_serializer["my_datasource"]["path"] == "/data/csv"
    with pytest.raises(KeyError):
        assert Config._data_source_serializer["my_datasource"]["not_defined"]
    assert Config.task_scheduler_configs.parallel_execution is True
    assert Config.task_scheduler_configs.max_number_of_parallel_execution == 10


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
        Config.load(config.filename)


def test_write_configuration_file():
    default_config = """
[TASK]
parallel_execution = false
max_number_of_parallel_execution = -1

[DATA_SOURCE.default]
""".strip()
    tf = NamedTemporaryFile()

    Config.export(tf.filename)
    assert tf.read().strip() == default_config

    updated_config = """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = -1

[DATA_SOURCE.my_datasource]
has_header = true
""".strip()

    updated_config_exported = """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = -1

[DATA_SOURCE.default]

[DATA_SOURCE.my_datasource]
has_header = true
    """.strip()

    Config.load(NamedTemporaryFile(updated_config))
    Config.export(tf.filename)

    assert tf.read().strip() == updated_config_exported


def test_configuration_should_be_in_a_node():
    config = NamedTemporaryFile(
        """
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None

    Config.load(config.filename)

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None


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

    assert Config.task_scheduler_configs.parallel_execution is False
    assert Config.task_scheduler_configs.max_number_of_parallel_execution is None

    os.environ[Config.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    Config.load(config_from_filename.filename)

    assert Config.task_scheduler_configs.parallel_execution is True
    assert Config.task_scheduler_configs.max_number_of_parallel_execution == 21


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
