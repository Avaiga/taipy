from copy import copy
from typing import Any, Dict, List, Optional, Union

from taipy.core.common._validate_id import _validate_id
from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl
from taipy.core.config.task_config import TaskConfig


class PipelineConfig:
    """
    Holds all the configuration fields needed to create actual pipelines from the PipelineConfig.

    Attributes:
        id (str): Identifier of the pipeline configuration. Must be a valid Python variable name.
        tasks (list): List of task configs. Default value: [].
        properties (dict): Dictionary of additional properties.
    """

    TASK_KEY = "tasks"

    def __init__(self, id: str, tasks: Union[TaskConfig, List[TaskConfig]] = None, **properties):
        self.id = _validate_id(id)
        self.properties = properties
        if tasks:
            self.tasks = [tasks] if isinstance(tasks, TaskConfig) else copy(tasks)
        else:
            self.tasks = []

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return PipelineConfig(self.id, copy(self.tasks), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return PipelineConfig(id, [])

    @property
    def tasks_configs(self) -> List[TaskConfig]:
        return self.tasks

    def to_dict(self):
        return {self.TASK_KEY: self.tasks, **self.properties}

    @classmethod
    def from_dict(cls, id: str, config_as_dict: Dict[str, Any], task_configs: Dict[str, TaskConfig]):
        config = PipelineConfig(id)
        config.id = _validate_id(id)
        if tasks := config_as_dict.pop(cls.TASK_KEY, None):
            config.tasks = [task_configs[task_id] for task_id in tasks if task_id in task_configs]
        config.properties = config_as_dict
        return config

    def update(self, config_as_dict, default_pipeline_cfg=None):
        self.tasks = config_as_dict.pop(self.TASK_KEY, self.tasks) or default_pipeline_cfg.tasks
        if self.tasks is None and default_pipeline_cfg:
            self.tasks = default_pipeline_cfg.tasks
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)
