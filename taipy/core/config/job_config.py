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

from importlib import util
from typing import Any, Dict, Optional, Type

from taipy.core.common._utils import _load_fct
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl
from taipy.core.config.job_mode_config import _JobModeConfig
from taipy.core.config.standalone_config import StandaloneConfig
from taipy.core.exceptions.exceptions import DependencyNotInstalled


class JobConfig:
    """
    Configuration fields related to the jobs' executions.

    Parameters:
        mode (str): The Taipy operating mode. By default, the "standalone" mode is set. On Taipy enterprise,
            "enterprise" and "airflow" mode are available.
        **properties: A dictionary of additional properties.
    """

    _MODE_KEY = "mode"
    _DEFAULT_MODE = "standalone"

    _MODE_TO_MODULE: Dict[str, str] = {
        "enterprise": "taipy.enterprise",
    }

    def __init__(self, mode: str = None, **properties):
        self.mode = mode or self._DEFAULT_MODE
        self._config_cls = self._get_config_cls(self.mode)
        self._config = self._create_config(self._config_cls, **properties)

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
            self._config_cls = self._get_config_cls(self.mode)
            self._config = self._create_config(self._config_cls, **config_as_dict)
        if self._config:
            self._update_config(config_as_dict)

    def _update_config(self, config_as_dict: Dict[str, Any]):
        default_config = self._config_cls._DEFAULT_CONFIG
        for k, v in config_as_dict.items():
            type_to_convert = type(default_config.get(k, None)) or str
            value = _tpl._replace_templates(v, type_to_convert)
            if value is not None:
                self._config[k] = value

    @classmethod
    def _get_config_cls(cls, mode: str) -> Type[_JobModeConfig]:
        if mode == cls._DEFAULT_MODE:
            return StandaloneConfig
        module = cls._MODE_TO_MODULE.get(mode, None)
        if not module or not util.find_spec(module):
            raise DependencyNotInstalled(mode)
        config_cls = _load_fct(module + ".config", "Config")
        return config_cls  # type:ignore

    @property
    def is_standalone(self) -> bool:
        """True if the config is set to standalone execution"""
        return self.mode == self._DEFAULT_MODE

    @property
    def is_multiprocess(self) -> bool:
        """True if the config is set to standalone execution and nb_of_workers is greater than 1"""
        return self.is_standalone and int(self.nb_of_workers) > 1  # type: ignore

    @classmethod
    def _create_config(cls, config_cls: Type[_JobModeConfig], **properties):
        default_config = config_cls._DEFAULT_CONFIG
        return {**default_config, **properties}
