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
