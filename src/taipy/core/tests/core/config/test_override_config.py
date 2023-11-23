# Copyright 2023 Avaiga Private Limited
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

from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InconsistentEnvVariableError, MissingEnvVariableError
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_override_default_configuration_with_code_configuration():
    assert not Config.core.root_folder == "foo"
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.scenarios) == 1

    Config.configure_job_executions(max_nb_of_workers=-1)
    Config.configure_core(root_folder="foo")
    foo_config = Config.configure_data_node("foo", "in_memory")
    xyz_config = Config.configure_data_node("xyz")
    bar_config = Config.configure_task("bar", print, [foo_config], [])
    qux_config = Config.configure_scenario("qux", [bar_config], [xyz_config])

    assert Config.job_config.max_nb_of_workers == -1
    assert Config.core.root_folder == "foo"
    assert len(Config.data_nodes) == 3
    assert "default" in Config.data_nodes
    assert foo_config.id in Config.data_nodes
    assert xyz_config.id in Config.data_nodes
    assert Config.data_nodes[foo_config.id].storage_type == "in_memory"
    assert Config.data_nodes[xyz_config.id].storage_type == "pickle"
    assert len(Config.tasks) == 2
    assert "default" in Config.tasks
    assert bar_config.id in Config.tasks
    assert len(Config.tasks[bar_config.id].input_configs) == 1
    assert Config.tasks[bar_config.id].input_configs[0].id == foo_config.id
    assert len(Config.tasks[bar_config.id].output_configs) == 0
    assert Config.tasks[bar_config.id].function == print

    assert len(Config.scenarios) == 2
    assert "default" in Config.scenarios
    assert qux_config.id in Config.scenarios
    assert len(Config.scenarios[qux_config.id].tasks) == 1
    assert Config.scenarios[qux_config.id].tasks[0].id == bar_config.id
    assert len(Config.scenarios[qux_config.id].additional_data_nodes) == 1
    assert Config.scenarios[qux_config.id].additional_data_nodes[0].id == xyz_config.id


def test_override_default_config_with_code_config_including_env_variable_values():
    Config.configure_core()
    assert Config.core.repository_type == "filesystem"
    Config.configure_core(repository_type="othertype")
    assert Config.core.repository_type == "othertype"

    with mock.patch.dict(os.environ, {"REPOSITORY_TYPE": "foo"}):
        Config.configure_core(repository_type="ENV[REPOSITORY_TYPE]")
        assert Config.core.repository_type == "foo"


def test_override_default_configuration_with_file_configuration():
    tf = NamedTemporaryFile(
        """
[TAIPY]

[JOB]
max_nb_of_workers = -1

[DATA_NODE.foo]

[TASK.bar]

[SCENARIO.qux]
"""
    )
    assert Config.job_config.max_nb_of_workers == 1
    assert len(Config.data_nodes) == 1
    assert len(Config.tasks) == 1
    assert len(Config.scenarios) == 1

    Config.override(tf.filename)

    assert Config.job_config.max_nb_of_workers == -1
    assert len(Config.data_nodes) == 2
    assert "default" in Config.data_nodes
    assert "foo" in Config.data_nodes
    assert len(Config.tasks) == 2
    assert "default" in Config.tasks
    assert "bar" in Config.tasks
    assert "default" in Config.scenarios
    assert len(Config.scenarios) == 2
    assert "qux" in Config.scenarios


def test_override_default_config_with_file_config_including_env_variable_values():
    tf = NamedTemporaryFile(
        """
[JOB]
max_nb_of_workers = "ENV[FOO]:int"
start_executor = "ENV[BAR]"
"""
    )
    assert Config.job_config.max_nb_of_workers == 1
    assert not Config.job_config.start_executor

    with mock.patch.dict(os.environ, {"FOO": "6", "BAR": "TRUe"}):
        Config.override(tf.filename)
        assert Config.job_config.max_nb_of_workers == 6
        assert Config.job_config.start_executor

    with mock.patch.dict(os.environ, {"FOO": "foo", "BAR": "true"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.override(tf.filename)

    with mock.patch.dict(os.environ, {"FOO": "5"}):
        with pytest.raises(MissingEnvVariableError):
            Config.override(tf.filename)


def test_code_configuration_do_not_override_file_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
max_nb_of_workers = 2
    """
    )
    Config.override(config_from_filename.filename)

    Config.configure_job_executions(max_nb_of_workers=21)

    assert Config.job_config.max_nb_of_workers == 2  # From file config


def test_code_configuration_do_not_override_file_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
max_nb_of_workers = 2
    """
    )
    Config.override(config_from_filename.filename)

    with mock.patch.dict(os.environ, {"FOO": "21"}):
        Config.configure_job_executions(max_nb_of_workers="ENV[FOO]")
        assert Config.job_config.max_nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
max_nb_of_workers = 2
    """
    )
    Config.configure_job_executions(max_nb_of_workers=21)
    Config.override(config_from_filename.filename)

    assert Config.job_config.max_nb_of_workers == 2  # From file config


def test_file_configuration_override_code_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
max_nb_of_workers = "ENV[FOO]:int"
    """
    )
    Config.configure_job_executions(max_nb_of_workers=21)

    with mock.patch.dict(os.environ, {"FOO": "2"}):
        Config.override(config_from_filename.filename)
        assert Config.job_config.max_nb_of_workers == 2  # From file config


def test_override_default_configuration_with_multiple_configurations():
    file_config = NamedTemporaryFile(
        """
[DATA_NODE.default]
has_header = true
[DATA_NODE.my_datanode]
path = "/data/csv"

[JOB]
max_nb_of_workers = 10

[TAIPY]
    """
    )

    # Default config is applied
    assert Config.job_config.max_nb_of_workers == 1

    # Code config is applied
    Config.configure_job_executions(max_nb_of_workers=-1)
    assert Config.job_config.max_nb_of_workers == -1

    # File config is applied
    Config.override(file_config.filename)
    assert Config.job_config.max_nb_of_workers == 10
    assert Config.data_nodes["my_datanode"].has_header
    assert Config.data_nodes["my_datanode"].path == "/data/csv"
    assert Config.data_nodes["my_datanode"].not_defined is None


def test_override_default_configuration_with_multiple_configurations_including_environment_variable_values():
    file_config = NamedTemporaryFile(
        """
[DATA_NODE.default]
has_header = true
[DATA_NODE.my_datanode]
path = "ENV[FOO]"

[JOB]
max_nb_of_workers = 10

[TAIPY]
    """
    )

    with mock.patch.dict(os.environ, {"FOO": "/data/csv", "BAR": "/baz/data/csv"}):
        # Default config is applied
        assert Config.job_config.max_nb_of_workers == 1

        # Code config is applied
        Config.configure_job_executions(max_nb_of_workers=-1)
        Config.configure_data_node("my_datanode", path="ENV[BAR]")
        assert Config.job_config.max_nb_of_workers == -1
        assert Config.data_nodes["my_datanode"].path == "/baz/data/csv"

        # File config is applied
        Config.override(file_config.filename)
        assert Config.job_config.max_nb_of_workers == 10
        assert Config.data_nodes["my_datanode"].has_header
        assert Config.data_nodes["my_datanode"].path == "/data/csv"
        assert Config.data_nodes["my_datanode"].not_defined is None
