# Copyright 2021-2024 Avaiga Private Limited
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

from taipy.common.config import Config
from taipy.common.config._config import _Config
from taipy.common.config.common._template_handler import _TemplateHandler as _tpl
from taipy.common.config.unique_section import UniqueSection


class JobConfig(UniqueSection):
    """ Configuration fields related to the task orchestration and the jobs' executions."""

    name = "JOB"

    _MODE_KEY = "mode"
    _STANDALONE_MODE = "standalone"
    _DEVELOPMENT_MODE = "development"
    _DEFAULT_MODE = _DEVELOPMENT_MODE
    _DEFAULT_MAX_NB_OF_WORKERS = 2
    _MODES = [_DEVELOPMENT_MODE, _STANDALONE_MODE]

    mode: Optional[str]
    """The task orchestration mode.

    By default, the "development" mode is set for testing and debugging the
    executions of jobs. A "standalone" mode is also available.

    In the Taipy Enterprise Edition, the "cluster" mode is available.
    """

    def __init__(self, mode: Optional[str] = None, **properties):
        self.mode = mode
        super().__init__(**properties)

        self._update_default_max_nb_of_workers_properties()

    def __copy__(self):
        return JobConfig(self.mode, **copy(self._properties))

    def __getattr__(self, key: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(key))  # type: ignore[union-attr]

    @property
    def is_standalone(self) -> bool:
        """True if the config is set to standalone mode"""
        return self.mode == self._STANDALONE_MODE

    @property
    def is_development(self) -> bool:
        """True if the config is set to development mode"""
        return self.mode == self._DEVELOPMENT_MODE

    @classmethod
    def default_config(cls) -> "JobConfig":
        """Return a default configuration for the job execution.

        Returns:
            The default job execution configuration.
        """
        return JobConfig(cls._DEFAULT_MODE)

    def _clean(self):
        self.mode = self._DEFAULT_MODE
        self._properties.clear()
        self._update_default_max_nb_of_workers_properties()

    def _to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any], id=None, config: Optional[_Config] = None):
        mode = config_as_dict.pop(cls._MODE_KEY, None)
        return JobConfig(mode, **config_as_dict)

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        mode = _tpl._replace_templates(as_dict.pop(self._MODE_KEY, self.mode))
        if self.mode != mode:
            self.mode = mode
            self._update_default_max_nb_of_workers_properties()

        self._properties.update(as_dict)  # type: ignore[union-attr]

    @staticmethod
    def _configure(
        mode: Optional[str] = None, max_nb_of_workers: Optional[Union[int, str]] = None, **properties
    ) -> "JobConfig":
        """Configure job execution.

        Parameters:
            mode (Optional[str]): The job execution mode.
                Possible values are: *"standalone"* or *"development"*.
            max_nb_of_workers (Optional[int, str]): Parameter used only in *"standalone"* mode.
                This indicates the maximum number of jobs able to run in parallel.<br/>
                The default value is 2.<br/>
                A string can be provided to dynamically set the value using an environment
                variable. The string must follow the pattern: `ENV[&lt;env_var&gt;]` where
                `&lt;env_var&gt;` is the name of an environment variable.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new job execution configuration.
        """
        if max_nb_of_workers:
            properties["max_nb_of_workers"] = max_nb_of_workers
        section = JobConfig(mode=mode, **properties)
        Config._register(section)
        return Config.unique_sections[JobConfig.name]

    def _update_default_max_nb_of_workers_properties(self):
        """If the job execution mode is standalone, set the default value for the max_nb_of_workers property"""
        if self.is_standalone and "max_nb_of_workers" not in self._properties:
            self.properties.update({"max_nb_of_workers": self._DEFAULT_MAX_NB_OF_WORKERS})
