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
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked


def test_global_config_with_env_variable_value():
    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_global_app(foo="ENV[FOO]", bar="ENV[BAZ]")
        assert Config.global_config.foo == "bar"
        assert Config.global_config.bar == "qux"


def test_default_global_app_config():
    global_config = Config.global_config
    assert global_config is not None
    assert not global_config.notification
    assert len(global_config.properties) == 0


def test_block_update_global_app_config():
    Config.block_update()

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.configure_global_app(foo="bar")

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.properties = {"foo": "bar"}

    # Test if the global_config stay as default
    assert Config.global_config.foo is None
    assert len(Config.global_config.properties) == 0
