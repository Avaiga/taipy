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

from typing import Any, Dict, Optional, Type

from ..common._template_handler import _TemplateHandler as _tpl
from .default_development_config import _DefaultDevelopmentConfig
from .default_standalone_config import DefaultStandaloneConfig
from ..exceptions.exceptions import ModeNotAvailable


class JobConfig:
    """
    Configuration fields related to the jobs' executions.

    Parameters:
        mode (str): The Taipy operating mode. By default, the "standalone" mode is set. A "development" mode is also
            available for testing and debugging the executions of jobs.
        **properties: A dictionary of additional properties.
    """

    _MODE_KEY = "mode"
    _STANDALONE_MODE = "standalone"
    _DEVELOPMENT_MODE = "development"
    _DEFAULT_MODE = _DEVELOPMENT_MODE

    def __init__(self, mode: str = None, **properties):
        self.mode = mode or self._DEFAULT_MODE
        self._config = self._create_config(self.mode, **properties)

    def __getattr__(self, key: str) -> Optional[Any]:
        return self._config.get(key, None)

    @classmethod
    def default_config(cls):
        return JobConfig(cls._DEFAULT_MODE)

    def _to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        as_dict.update(self._config)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        mode = config_as_dict.pop(cls._MODE_KEY, None)
        config = JobConfig(mode, **config_as_dict)
        return config

    def _update(self, config_as_dict: Dict[str, Any]):
        mode = _tpl._replace_templates(config_as_dict.pop(self._MODE_KEY, self.mode))
        if self.mode != mode:
            self.mode = mode
            self._config = self._create_config(self.mode, **config_as_dict)
        if self._config is not None:
            self._update_config(config_as_dict)

    def _update_config(self, config_as_dict: Dict[str, Any]):
        for k, v in config_as_dict.items():
            type_to_convert = type(self.get_default_config(self.mode).get(k, None)) or str
            value = _tpl._replace_templates(v, type_to_convert)
            if value is not None:
                self._config[k] = value

    @property
    def is_standalone(self) -> bool:
        """True if the config is set to standalone mode"""
        return self.mode == self._STANDALONE_MODE

    @property
    def is_development(self) -> bool:
        """True if the config is set to development mode"""
        return self.mode == self._DEVELOPMENT_MODE

    @classmethod
    def get_default_config(cls, mode: str):
        if cls.is_standalone:
            return DefaultStandaloneConfig._DEFAULT_CONFIG
        if cls.is_development:
            return _DefaultDevelopmentConfig._DEFAULT_CONFIG
        raise ModeNotAvailable(mode)

    @classmethod
    def _create_config(cls, mode, **properties):
        return {**cls.get_default_config(mode), **properties}
