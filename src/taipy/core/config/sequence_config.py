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
from typing import Any, Dict, List, Optional, Union

from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.config import Config
from taipy.config.section import Section

from ..common._warnings import _warn_deprecated
from .task_config import TaskConfig


class SequenceConfig(Section):
    """
    Configuration fields needed to instantiate an actual `Sequence^`.

    Attributes:
        id (str): Identifier of the sequence configuration. It must be a valid Python variable name.
        task_configs (Union[TaskConfig, List[TaskConfig]]): List of task configs.<br/>
            The default value is [].
        **properties (dict[str, any]): A dictionary of additional properties.
    """

    name = "SEQUENCE"

    _TASK_KEY = "tasks"

    def __init__(self, id: str, tasks: Union[TaskConfig, List[TaskConfig]] = None, **properties):
        if tasks:
            self._tasks = [tasks] if isinstance(tasks, TaskConfig) else copy(tasks)
        else:
            self._tasks = []
        super().__init__(id, **properties)

    def __copy__(self):
        return SequenceConfig(self.id, copy(self._tasks), **copy(self._properties))

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @property
    def task_configs(self) -> List[TaskConfig]:
        return self._tasks

    @property
    def tasks(self) -> List[TaskConfig]:
        return self._tasks

    @classmethod
    def default_config(cls):
        return SequenceConfig(cls._DEFAULT_KEY, [])

    def _clean(self):
        self._tasks = []
        self._properties.clear()

    def _to_dict(self):
        return {self._TASK_KEY: self._tasks, **self._properties}

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):
        as_dict.pop(cls._ID_KEY, id)
        t_configs = config._sections.get(TaskConfig.name, None) or []  # type: ignore
        tasks = []
        if tasks_ids := as_dict.pop(cls._TASK_KEY, None):
            tasks = [t_configs[task_id] for task_id in tasks_ids if task_id in t_configs]
        return SequenceConfig(id=id, tasks=tasks, **as_dict)

    def _update(self, as_dict, default_section=None):
        self._tasks = as_dict.pop(self._TASK_KEY, self._tasks)
        if self._tasks is None and default_section:
            self._tasks = default_section._tasks
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties) -> "SequenceConfig":
        """Configure a new sequence configuration.

        Parameters:
            id (str): The unique identifier of the new sequence configuration.
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make this new sequence. This can be a single task
                configuration object if this sequence holds a single task.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new sequence configuration.
        """
        section = SequenceConfig(id, task_configs, **properties)
        Config._register(section)
        return Config.sections[SequenceConfig.name][id]

    @staticmethod
    def _set_default_configuration(task_configs: Union[TaskConfig, List[TaskConfig]], **properties) -> "SequenceConfig":
        """Set the default values for sequence configurations.

        This function creates the *default sequence configuration* object,
        where all sequence configuration objects will find their default
        values when needed.

        Parameters:
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make the default sequence configuration. This can be
                a single task configuration object if this sequence holds a single task.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.
        Returns:
            The default sequence configuration.
        """
        section = SequenceConfig(_Config.DEFAULT_KEY, task_configs, **properties)
        Config._register(section)
        return Config.sections[SequenceConfig.name][_Config.DEFAULT_KEY]
