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

from src.taipy.config.config import Config
from src.taipy.config.exceptions.exceptions import InconsistentEnvVariableError, MissingEnvVariableError
from tests.config.utils.named_temporary_file import NamedTemporaryFile


def test_override_default_configuration_with_code_configuration():
    assert not Config.global_config.root_folder == "foo"

    assert len(Config.unique_sections) == 1
    assert Config.unique_sections["unique_section_name"] is not None
    assert Config.unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config.unique_sections["unique_section_name"].prop is None

    assert len(Config.sections) == 1
    assert len(Config.sections["section_name"]) == 1
    assert Config.sections["section_name"] is not None
    assert Config.sections["section_name"]["default"].attribute == "default_attribute"

    Config.configure_global_app(root_folder="foo")
    assert Config.global_config.root_folder == "foo"

    Config.configure_unique_section_for_tests("foo", prop="bar")
    assert len(Config.unique_sections) == 1
    assert Config.unique_sections["unique_section_name"] is not None
    assert Config.unique_sections["unique_section_name"].attribute == "foo"
    assert Config.unique_sections["unique_section_name"].prop == "bar"

    Config.configure_section_for_tests("my_id", "baz", prop="qux")
    assert len(Config.unique_sections) == 1
    assert Config.sections["section_name"] is not None
    assert Config.sections["section_name"]["my_id"].attribute == "baz"
    assert Config.sections["section_name"]["my_id"].prop == "qux"


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
            Config.global_config.clean_entities_enabled


def test_override_default_configuration_with_file_configuration():
    tf = NamedTemporaryFile(
        """
[TAIPY]
clean_entities_enabled = true

"""
    )
    assert not Config.global_config.clean_entities_enabled

    Config.load(tf.filename)

    assert Config.global_config.clean_entities_enabled


def test_override_default_config_with_file_config_including_env_variable_values():
    tf = NamedTemporaryFile(
        """
[TAIPY]
foo_attribute = "ENV[FOO]:int"
bar_attribute = "ENV[BAR]:bool"
"""
    )
    assert Config.global_config.foo_attribute is None
    assert Config.global_config.bar_attribute is None

    with mock.patch.dict(os.environ, {"FOO": "foo", "BAR": "true"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.load(tf.filename)
            Config.global_config.foo_attribute

    with mock.patch.dict(os.environ, {"FOO": "5"}):
        with pytest.raises(MissingEnvVariableError):
            Config.load(tf.filename)
            Config.global_config.bar_attribute

    with mock.patch.dict(os.environ, {"FOO": "6", "BAR": "TRUe"}):
        Config.load(tf.filename)
        assert Config.global_config.foo_attribute == 6
        assert Config.global_config.bar_attribute


def test_code_configuration_does_not_override_file_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[TAIPY]
foo = 2
    """
    )
    Config.load(config_from_filename.filename)

    Config.configure_global_app(foo=21)

    assert Config.global_config.foo == 2  # From file config


def test_code_configuration_does_not_override_file_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[TAIPY]
foo = 2
    """
    )
    Config.load(config_from_filename.filename)

    with mock.patch.dict(os.environ, {"FOO": "21"}):
        Config.configure_global_app(foo="ENV[FOO]")
        assert Config.global_config.foo == 2  # From file config


def test_file_configuration_overrides_code_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[TAIPY]
foo = 2
    """
    )
    Config.configure_global_app(foo=21)
    Config.load(config_from_filename.filename)

    assert Config.global_config.foo == 2  # From file config


def test_file_configuration_overrides_code_configuration_including_env_variable_values():
    config_from_filename = NamedTemporaryFile(
        """
[TAIPY]
foo = "ENV[FOO]:int"
    """
    )
    Config.configure_global_app(foo=21)

    with mock.patch.dict(os.environ, {"FOO": "2"}):
        Config.load(config_from_filename.filename)
        assert Config.global_config.foo == 2  # From file config


def test_override_default_configuration_with_multiple_configurations():
    file_config = NamedTemporaryFile(
        """
[TAIPY]
clean_entities_enabled = false
foo = 10
    """
    )
    # Default config is applied
    assert Config.global_config.foo is None
    assert Config.global_config.clean_entities_enabled is False

    Config.configure_global_app()
    assert Config.global_config.foo is None
    assert Config.global_config.clean_entities_enabled is False

    # Code config is applied
    Config.configure_global_app(clean_entities_enabled=True)
    Config.configure_global_app(foo=-1)
    assert Config.global_config.clean_entities_enabled is True
    assert Config.global_config.foo == -1

    # File config is applied
    Config.load(file_config.filename)
    assert Config.global_config.clean_entities_enabled is False
    assert Config.global_config.foo == 10


def test_override_default_configuration_with_multiple_configurations_including_environment_variable_values():
    file_config = NamedTemporaryFile(
        """
[TAIPY]
clean_entities_enabled = false
att = "ENV[BAZ]"
    """
    )

    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        # Default config is applied
        assert Config.global_config.clean_entities_enabled is False
        assert Config.global_config.att is None

        # Code config is applied
        Config.configure_global_app(clean_entities_enabled=True, att="ENV[FOO]")
        assert Config.global_config.clean_entities_enabled is True
        assert Config.global_config.att == "bar"

        # File config is applied
        Config.load(file_config.filename)
        assert Config.global_config.clean_entities_enabled is False
        assert Config.global_config.att == "qux"
