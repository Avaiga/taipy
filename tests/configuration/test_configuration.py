import os
import tempfile

import pytest

from taipy.configuration import ConfigurationManager
from taipy.configuration.task_scheduler_configuration import TaskSchedulerConfiguration


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    ConfigurationManager.task_scheduler_configuration = TaskSchedulerConfiguration()


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
[TASK]
parallel_execution = true
max_number_of_parallel_execution = 10
    """
    )

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is False
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution is None

    ConfigurationManager.load(config.filename)

    assert ConfigurationManager.task_scheduler_configuration.parallel_execution is True
    assert ConfigurationManager.task_scheduler_configuration.max_number_of_parallel_execution == 10


def test_write_configuration_file():
    default_config = """
[TASK]
parallel_execution = false
max_number_of_parallel_execution = -1
""".strip()
    tf = NamedTemporaryFile()

    ConfigurationManager.export(tf.filename)
    assert tf.read().strip() == default_config

    updated_config = """
[TASK]
parallel_execution = true
max_number_of_parallel_execution = -1
""".strip()

    ConfigurationManager.task_scheduler_configuration.parallel_execution = True
    ConfigurationManager.export(tf.filename)

    assert tf.read().strip() == updated_config


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
