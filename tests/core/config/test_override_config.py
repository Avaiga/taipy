import os
from unittest import mock

import pytest

from taipy.core.config.config import Config
from taipy.core.exceptions.configuration import InconsistentEnvVariableError, MissingEnvVariableError
from tests.core.config.named_temporary_file import NamedTemporaryFile


def test_override_default_configuration_with_code_configuration():
    assert Config.job_config.nb_of_workers == 1
    assert not Config.global_config.root_folder == "foo"
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.pipelines) == 1
    assert len(Config.scenarios) == 1

    Config._set_job_config(nb_of_workers=-1)
    Config._set_global_config(root_folder="foo")
    foo_config = Config._add_data_node("foo", "in_memory")
    bar_config = Config._add_task("bar", print, [foo_config], [])
    baz_config = Config._add_pipeline("baz", [bar_config])
    qux_config = Config._add_scenario("qux", [baz_config])

    assert Config.job_config.nb_of_workers == -1
    assert Config.global_config.root_folder == "foo"
    assert len(Config.data_nodes) == 2
    assert "default" in Config.data_nodes
    assert foo_config.id in Config.data_nodes
    assert Config.data_nodes[foo_config.id].storage_type == "in_memory"
    assert len(Config.tasks) == 2
    assert "default" in Config.tasks
    assert bar_config.id in Config.tasks
    assert len(Config.tasks[bar_config.id].input_configs) == 1
    assert Config.tasks[bar_config.id].input_configs[0].id == foo_config.id
    assert len(Config.tasks[bar_config.id].output_configs) == 0
    assert Config.tasks[bar_config.id].function == print
    assert len(Config.pipelines) == 2
    assert "default" in Config.pipelines
    assert baz_config.id in Config.pipelines
    assert len(Config.pipelines[baz_config.id].task_configs) == 1
    assert Config.pipelines[baz_config.id].task_configs[0].id == bar_config.id
    assert len(Config.scenarios) == 2
    assert "default" in Config.scenarios
    assert qux_config.id in Config.scenarios
    assert len(Config.scenarios[qux_config.id].pipeline_configs) == 1
    assert Config.scenarios[qux_config.id].pipeline_configs[0].id == baz_config.id


def test_override_default_config_with_code_config_including_env_variable_values():
    Config._set_global_config()
    assert not Config.global_config.clean_entities_enabled
    Config._set_global_config(clean_entities_enabled=True)
    assert Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "False"}):
        Config._set_global_config(clean_entities_enabled="ENV[ENV_VAR]")
        assert not Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "true"}):
        Config._set_global_config(clean_entities_enabled="ENV[ENV_VAR]")
        assert Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "foo"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config._set_global_config(clean_entities_enabled="ENV[ENV_VAR]")


def test_override_default_configuration_with_file_configuration():
    tf = NamedTemporaryFile(
        """
[TAIPY]
clean_entities_enabled = true

[JOB]
nb_of_workers = -1

[DATA_NODE.foo]

[TASK.bar]

[PIPELINE.baz]

[SCENARIO.qux]
"""
    )
    Config._set_global_config()
    assert Config.job_config.nb_of_workers == 1
    assert not Config.global_config.clean_entities_enabled
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.pipelines) == 1
    assert len(Config.scenarios) == 1

    Config._load(tf.filename)

    assert Config.job_config.nb_of_workers == -1
    assert Config.global_config.clean_entities_enabled
    assert len(Config.data_nodes) == 2
    assert "default" in Config.data_nodes
    assert "foo" in Config.data_nodes
    assert len(Config.tasks) == 2
    assert "default" in Config.tasks
    assert "bar" in Config.tasks
    assert len(Config.pipelines) == 2
    assert "default" in Config.pipelines
    assert "default" in Config.scenarios
    assert len(Config.scenarios) == 2
    assert "baz" in Config.pipelines
    assert "qux" in Config.scenarios


def test_override_default_config_with_file_config_including_env_variable_values():
    tf = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = "ENV[FOO]"
start_airflow = "ENV[BAR]"
"""
    )
    assert Config.job_config.nb_of_workers == 1
    assert not Config.job_config.start_airflow

    with mock.patch.dict(os.environ, {"FOO": "6", "BAR": "TRUe"}):
        Config._load(tf.filename)
        assert Config.job_config.nb_of_workers == 6
        assert Config.job_config.start_airflow

    with mock.patch.dict(os.environ, {"FOO": "foo", "BAR": "true"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config._load(tf.filename)

    with mock.patch.dict(os.environ, {"FOO": "5"}):
        with pytest.raises(MissingEnvVariableError):
            Config._load(tf.filename)


def test_code_configuration_do_not_override_file_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config._load(config_from_filename.filename)

    Config._set_job_config(nb_of_workers=21)

    assert Config.job_config.nb_of_workers == 2  # From file config


def test_code_configuration_do_not_override_file_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config._load(config_from_filename.filename)

    with mock.patch.dict(os.environ, {"FOO": "21"}):
        Config._set_job_config(nb_of_workers="ENV[FOO]")
        assert Config.job_config.nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config._set_job_config(nb_of_workers=21)
    Config._load(config_from_filename.filename)

    assert Config.job_config.nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = "ENV[FOO]"
    """
    )
    Config._set_job_config(nb_of_workers=21)

    with mock.patch.dict(os.environ, {"FOO": "2"}):
        Config._load(config_from_filename.filename)
        assert Config.job_config.nb_of_workers == 2  # From file config


def test_override_default_configuration_with_multiple_configurations():
    file_config = NamedTemporaryFile(
        """
[DATA_NODE.default]
has_header = true
[DATA_NODE.my_datanode]
path = "/data/csv"

[JOB]
nb_of_workers = 10

[TAIPY]
clean_entities_enabled = false
    """
    )

    Config._set_global_config()
    # Default config is applied
    assert Config.job_config.nb_of_workers == 1
    assert Config.global_config.clean_entities_enabled is False

    # Code config is applied
    Config._set_job_config(nb_of_workers=-1)
    Config._set_global_config(clean_entities_enabled=True)
    assert Config.global_config.clean_entities_enabled is True
    assert Config.job_config.nb_of_workers == -1

    # File config is applied
    Config._load(file_config.filename)
    assert Config.global_config.clean_entities_enabled is False
    assert Config.job_config.nb_of_workers == 10
    assert Config.data_nodes["my_datanode"].has_header
    assert Config.data_nodes["my_datanode"].path == "/data/csv"
    assert Config.data_nodes["my_datanode"].not_defined is None


def test_override_default_configuration_with_multiple_configurations_including_environment_varaible_values():
    file_config = NamedTemporaryFile(
        """
[DATA_NODE.default]
has_header = true
[DATA_NODE.my_datanode]
path = "ENV[FOO]"

[JOB]
nb_of_workers = 10

[TAIPY]
clean_entities_enabled = false
    """
    )

    Config._set_global_config()
    with mock.patch.dict(os.environ, {"FOO": "/data/csv", "BAR": "/baz/data/csv"}):
        # Default config is applied
        assert Config.job_config.nb_of_workers == 1
        assert Config.global_config.clean_entities_enabled is False

        # Code config is applied
        Config._set_job_config(nb_of_workers=-1)
        Config._set_global_config(clean_entities_enabled=True)
        Config._add_data_node("my_datanode", path="ENV[BAR]")
        assert Config.global_config.clean_entities_enabled is True
        assert Config.job_config.nb_of_workers == -1
        assert Config.data_nodes["my_datanode"].path == "/baz/data/csv"

        # File config is applied
        Config._load(file_config.filename)
        assert Config.global_config.clean_entities_enabled is False
        assert Config.job_config.nb_of_workers == 10
        assert Config.data_nodes["my_datanode"].has_header
        assert Config.data_nodes["my_datanode"].path == "/data/csv"
        assert Config.data_nodes["my_datanode"].not_defined is None
