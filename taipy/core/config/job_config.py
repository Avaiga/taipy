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
from copy import copy
from typing import Any, Dict, Optional, Union

from taipy.config import Config
from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.unique_section import UniqueSection

from ..exceptions.exceptions import ModeNotAvailable


class JobConfig(UniqueSection):
    """
    Configuration fields related to the jobs' executions.

    Parameters:
        mode (str): The Taipy operating mode. By default, the "development" mode is set for testing and debugging the
            executions of jobs. A "standalone" mode is also available.
        **properties (dict[str, any]): A dictionary of additional properties.
    """

    name = "JOB"

    _MODE_KEY = "mode"
    _STANDALONE_MODE = "standalone"
    _DEVELOPMENT_MODE = "development"
    _DEFAULT_MODE = _DEVELOPMENT_MODE
    _MODES = [_STANDALONE_MODE, _DEVELOPMENT_MODE]

    def __init__(self, mode: Optional[str] = None, **properties):
        self.mode = mode or self._DEFAULT_MODE
        self._config = self._create_config(self.mode, **properties)
        super().__init__(**properties)

    def __copy__(self):
        return JobConfig(self.mode, **copy(self._properties))

    def __getattr__(self, key: str) -> Optional[Any]:
        return self._config.get(key, None)

    @classmethod
    def default_config(cls):
        return JobConfig(cls._DEFAULT_MODE)

    def _clean(self):
        self.mode = self._DEFAULT_MODE
        self._config = self._create_config(self.mode)

    def _to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        as_dict.update(self._config)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any], id=None, config: Optional[_Config] = None):
        mode = config_as_dict.pop(cls._MODE_KEY, None)
        job_config = JobConfig(mode, **config_as_dict)
        return job_config

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        mode = _tpl._replace_templates(as_dict.pop(self._MODE_KEY, self.mode))
        if self.mode != mode:
            self.mode = mode
            self._config = self._create_config(self.mode, **as_dict)
        if self._config is not None:
            self._update_config(as_dict)

    @staticmethod
    def _configure(
        mode: Optional[str] = None, max_nb_of_workers: Optional[Union[int, str]] = None, **properties
    ) -> "JobConfig":
        """Configure job execution.

        Parameters:
            mode (Optional[str]): The job execution mode.
                Possible values are: *"standalone"* (the default value) or *"development"*.
            max_nb_of_workers (Optional[int, str]): Parameter used only in default *"standalone"* mode.
                This indicates the maximum number of jobs able to run in parallel.<br/>
                The default value is 1.<br/>
                A string can be provided to dynamically set the value using an environment
                variable. The string must follow the pattern: `ENV[&lt;env_var&gt;]` where
                `&lt;env_var&gt;` is the name of an environment variable.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new job execution configuration.
        """
        section = JobConfig(mode, max_nb_of_workers=max_nb_of_workers, **properties)
        Config._register(section)
        return Config.unique_sections[JobConfig.name]

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
    def get_default_config(cls, mode: str) -> Dict[str, Any]:
        if cls.is_standalone:  # type: ignore
            return {"max_nb_of_workers": 1}
        if cls.is_development:
            return {}
        raise ModeNotAvailable(mode)

    @classmethod
    def _create_config(cls, mode, **properties):
        return {**cls.get_default_config(mode), **properties}
