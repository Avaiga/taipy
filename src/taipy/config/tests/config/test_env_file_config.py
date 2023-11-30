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

import pytest

from src.taipy.config.config import Config
from src.taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked
from tests.config.utils.named_temporary_file import NamedTemporaryFile

config_from_filename = NamedTemporaryFile(
    """
[TAIPY]
custom_property_not_overwritten = true
custom_property_overwritten = 10
"""
)

config_from_environment = NamedTemporaryFile(
    """
[TAIPY]
custom_property_overwritten = 11
"""
)


def test_load_from_environment_overwrite_load_from_filename():
    os.environ[Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    Config.load(config_from_filename.filename)

    assert Config.global_config.custom_property_not_overwritten is True
    assert Config.global_config.custom_property_overwritten == 11
    os.environ.pop(Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH)


def test_block_load_from_environment_overwrite_load_from_filename():
    Config.load(config_from_filename.filename)
    assert Config.global_config.custom_property_not_overwritten is True
    assert Config.global_config.custom_property_overwritten == 10

    Config.block_update()

    with pytest.raises(ConfigurationUpdateBlocked):
        os.environ[Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
        Config.load(config_from_filename.filename)

    os.environ.pop(Config._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH)
    assert Config.global_config.custom_property_not_overwritten is True
    assert Config.global_config.custom_property_overwritten == 10  # The Config.load is failed to override
