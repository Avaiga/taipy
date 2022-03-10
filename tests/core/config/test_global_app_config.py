import os
from unittest import mock

import pytest

from taipy.core.config.config import Config
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.exceptions.configuration import InconsistentEnvVariableError


def test_clean_entities_enabled_default():
    Config._set_global_config()
    assert Config.global_config.clean_entities_enabled is GlobalAppConfig._DEFAULT_CLEAN_ENTITIES_ENABLED
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "true"}):
        Config._set_global_config()  # Trigger config compilation
        assert Config.global_config.clean_entities_enabled is True
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "false"}):
        Config._set_global_config()
        assert Config.global_config.clean_entities_enabled is False
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "foo"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config._set_global_config()
            assert Config.global_config.clean_entities_enabled is False
