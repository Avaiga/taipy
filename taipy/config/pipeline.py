import re
import unidecode
from typing import List

from taipy.config import TaskConfig
from taipy.config.interface import ConfigRepository


class PipelineConfig:
    def __init__(self, name: str, tasks_configs: List[TaskConfig], **properties):
        self.name = re.sub(r'[\W]+', '-', unidecode.unidecode(name).strip().lower().replace(' ', '_'))
        self.tasks_configs = tasks_configs
        self.properties = properties


class PipelineConfigs(ConfigRepository):
    def create(self, name: str, tasks: List[TaskConfig], **properties):  # type: ignore
        pipeline_config = PipelineConfig(name, tasks, **properties)
        self._data[name] = pipeline_config
        return pipeline_config
