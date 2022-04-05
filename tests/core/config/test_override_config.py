# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
from unittest import mock

import pytest

from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import InconsistentEnvVariableError, MissingEnvVariableError
from tests.core.config.named_temporary_file import NamedTemporaryFile


def test_override_default_configuration_with_code_configuration():
    assert Config.job_config.nb_of_workers == 1
    assert not Config.global_config.root_folder == "foo"
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.pipelines) == 1
    assert len(Config.scenarios) == 1

    Config.configure_job_executions(nb_of_workers=-1)
    Config.configure_global_app(root_folder="foo")
    foo_config = Config.configure_data_node("foo", "in_memory")
    bar_config = Config.configure_task("bar", print, [foo_config], [])
    baz_config = Config.configure_pipeline("baz", [bar_config])
    qux_config = Config.configure_scenario("qux", [baz_config])

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
    Config.configure_global_app()
    assert not Config.global_config.clean_entities_enabled
    Config.configure_global_app(clean_entities_enabled=True)
    assert Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "False"}):
        Config.configure_global_app(clean_entities_enabled="ENV[ENV_VAR]")
        assert not Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "true"}):
        Config.configure_global_app(clean_entities_enabled="ENV[ENV_VAR]")
        assert Config.global_config.clean_entities_enabled

    with mock.patch.dict(os.environ, {"ENV_VAR": "foo"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.configure_global_app(clean_entities_enabled="ENV[ENV_VAR]")


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
    Config.configure_global_app()
    assert Config.job_config.nb_of_workers == 1
    assert not Config.global_config.clean_entities_enabled
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.pipelines) == 1
    assert len(Config.scenarios) == 1

    Config.load(tf.filename)

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
        Config.load(tf.filename)
        assert Config.job_config.nb_of_workers == 6
        assert Config.job_config.start_airflow

    with mock.patch.dict(os.environ, {"FOO": "foo", "BAR": "true"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.load(tf.filename)

    with mock.patch.dict(os.environ, {"FOO": "5"}):
        with pytest.raises(MissingEnvVariableError):
            Config.load(tf.filename)


def test_code_configuration_do_not_override_file_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config.load(config_from_filename.filename)

    Config.configure_job_executions(nb_of_workers=21)

    assert Config.job_config.nb_of_workers == 2  # From file config


def test_code_configuration_do_not_override_file_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config.load(config_from_filename.filename)

    with mock.patch.dict(os.environ, {"FOO": "21"}):
        Config.configure_job_executions(nb_of_workers="ENV[FOO]")
        assert Config.job_config.nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config.configure_job_executions(nb_of_workers=21)
    Config.load(config_from_filename.filename)

    assert Config.job_config.nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = "ENV[FOO]"
    """
    )
    Config.configure_job_executions(nb_of_workers=21)

    with mock.patch.dict(os.environ, {"FOO": "2"}):
        Config.load(config_from_filename.filename)
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

    Config.configure_global_app()
    # Default config is applied
    assert Config.job_config.nb_of_workers == 1
    assert Config.global_config.clean_entities_enabled is False

    # Code config is applied
    Config.configure_job_executions(nb_of_workers=-1)
    Config.configure_global_app(clean_entities_enabled=True)
    assert Config.global_config.clean_entities_enabled is True
    assert Config.job_config.nb_of_workers == -1

    # File config is applied
    Config.load(file_config.filename)
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

    Config.configure_global_app()
    with mock.patch.dict(os.environ, {"FOO": "/data/csv", "BAR": "/baz/data/csv"}):
        # Default config is applied
        assert Config.job_config.nb_of_workers == 1
        assert Config.global_config.clean_entities_enabled is False

        # Code config is applied
        Config.configure_job_executions(nb_of_workers=-1)
        Config.configure_global_app(clean_entities_enabled=True)
        Config.configure_data_node("my_datanode", path="ENV[BAR]")
        assert Config.global_config.clean_entities_enabled is True
        assert Config.job_config.nb_of_workers == -1
        assert Config.data_nodes["my_datanode"].path == "/baz/data/csv"

        # File config is applied
        Config.load(file_config.filename)
        assert Config.global_config.clean_entities_enabled is False
        assert Config.job_config.nb_of_workers == 10
        assert Config.data_nodes["my_datanode"].has_header
        assert Config.data_nodes["my_datanode"].path == "/data/csv"
        assert Config.data_nodes["my_datanode"].not_defined is None
