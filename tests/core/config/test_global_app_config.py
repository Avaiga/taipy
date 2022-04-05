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
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.exceptions.exceptions import InconsistentEnvVariableError


def test_clean_entities_enabled_default():
    Config.configure_global_app()
    assert Config.global_config.clean_entities_enabled is GlobalAppConfig._DEFAULT_CLEAN_ENTITIES_ENABLED
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "true"}):
        Config.configure_global_app()  # Trigger config compilation
        assert Config.global_config.clean_entities_enabled is True
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "false"}):
        Config.configure_global_app()
        assert Config.global_config.clean_entities_enabled is False
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "foo"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.configure_global_app()
            assert Config.global_config.clean_entities_enabled is False
