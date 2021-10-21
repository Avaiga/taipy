from typing import List

from taipy.config import TaskConfig
from taipy.config.interface import ConfigRepository


class PipelineConfig:
    def __init__(self, name: str, tasks: List[TaskConfig], **properties):
        self.name = name.strip().lower().replace(" ", "_")
        self.tasks = tasks
        self.properties = properties


class PipelinesRepository(ConfigRepository):
    def create(self, name: str, tasks: List[TaskConfig], **properties):  # type: ignore
        pipeline_config = PipelineConfig(name, tasks, **properties)
        self._data[name] = pipeline_config
        return pipeline_config
