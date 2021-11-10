import os

import pytest

from taipy.config import Config
from taipy.exceptions.configuration import LoadingError
from tests.taipy.config.named_temporary_file import NamedTemporaryFile


def test_default_configuration():
    tf = NamedTemporaryFile()

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers is None

    # Load an empty file
    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers is None


def test_override_default_configuration():
    tf = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = -1
[DATA_SOURCE.default]
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers is None


def test_override_default_configuration_with_multiple_configuration():
    config = NamedTemporaryFile(
        """
[DATA_SOURCE.default]
has_header = true
[DATA_SOURCE.my_datasource]
path = "/data/csv"

[TASK]
parallel_execution = true
nb_of_workers = 10
    """
    )

    task_scheduler_config = Config.task_scheduler_configs.create()

    assert task_scheduler_config.parallel_execution is False
    assert task_scheduler_config.nb_of_workers is None

    Config.load(config.filename)

    task_scheduler_config = Config.task_scheduler_configs.create()

    assert Config._data_source_serializer["my_datasource"]["has_header"] is True
    assert Config._data_source_serializer["my_datasource"]["path"] == "/data/csv"
    with pytest.raises(KeyError):
        assert Config._data_source_serializer["my_datasource"]["not_defined"]
    assert task_scheduler_config.parallel_execution is True
    assert task_scheduler_config.nb_of_workers == 10


def test_node_can_not_appears_twice():
    config = NamedTemporaryFile(
        """
[TASK]
parallel_execution = false
nb_of_workers = 40

[TASK]
parallel_execution = true
nb_of_workers = 10
    """
    )

    with pytest.raises(LoadingError, match="Can not load configuration"):
        Config.load(config.filename)


def test_write_configuration_file():
    default_config = """
[TASK]
execution_env = "local"
nb_of_workers = -1

[DATA_SOURCE.default]
""".strip()
    tf = NamedTemporaryFile()

    Config.export(tf.filename)
    assert tf.read().strip() == default_config

    updated_config = """
[TASK]
execution_env = "local"
nb_of_workers = 2

[DATA_SOURCE.my_datasource]
has_header = true
""".strip()

    updated_config_exported = """
[TASK]
execution_env = "local"
nb_of_workers = 2

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
nb_of_workers = 10
    """
    )

    Config.load(config.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers is None


def test_load_from_environment_overwrite_load_from_filename():
    config_from_filename = NamedTemporaryFile(
        """
[TASK]
parallel_execution = true
nb_of_workers = 10
    """
    )
    config_from_environment = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = 21
    """
    )

    os.environ[Config.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    Config.load(config_from_filename.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 21


def test_can_not_override_conf_with_code():
    config_from_filename = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = 2
    """
    )
    Config.load(config_from_filename.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create(
        parallel_execution=False, nb_of_workers=21, remote_execution=True
    )

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 2
