from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.core.common._validate_id import _validate_id
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl
from taipy.core.config.task_config import TaskConfig


class PipelineConfig:
    """
    Configuration fields needed to instantiate an actual `Pipeline^` from the PipelineConfig.

    Attributes:
        id (str): Identifier of the pipeline configuration. It must be a valid Python variable name.
        task_configs (`TaskConfig^` or List[`TaskConfig^`]): List of task configs. The default value is [].
        **properties: A dictionary of additional properties.
    """

    _TASK_KEY = "tasks"

    def __init__(self, id: str, tasks: Union[TaskConfig, List[TaskConfig]] = None, **properties):
        self.id = _validate_id(id)
        self.properties = properties
        if tasks:
            self._tasks = [tasks] if isinstance(tasks, TaskConfig) else copy(tasks)
        else:
            self._tasks = []

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return PipelineConfig(self.id, copy(self._tasks), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return PipelineConfig(id, [])

    @property
    def task_configs(self) -> List[TaskConfig]:
        return self._tasks

    def _to_dict(self):
        return {self._TASK_KEY: self._tasks, **self.properties}

    @classmethod
    def _from_dict(cls, id: str, config_as_dict: Dict[str, Any], task_configs: Dict[str, TaskConfig]):
        config = PipelineConfig(id)
        config.id = _validate_id(id)
        if tasks := config_as_dict.pop(cls._TASK_KEY, None):
            config._tasks = [task_configs[task_id] for task_id in tasks if task_id in task_configs]
        config.properties = config_as_dict
        return config

    def _update(self, config_as_dict, default_pipeline_cfg=None):
        self._tasks = (
            config_as_dict.pop(self._TASK_KEY, self._tasks)
            if config_as_dict.get(self._TASK_KEY, self._tasks) is not None
            else default_pipeline_cfg.task_configs
        )
        if self._tasks is None and default_pipeline_cfg:
            self._tasks = default_pipeline_cfg._tasks
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = _tpl._replace_templates(v)
