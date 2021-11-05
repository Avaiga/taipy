from typing import List

from taipy.common import protect_name
from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository


class ScenarioConfig:
    def __init__(self, name: str, pipelines_configs: List[PipelineConfig], **properties):
        self.name = protect_name(name)
        self.pipelines_configs = pipelines_configs
        self.properties = properties


class ScenarioConfigs(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, **properties)
        self._data[name] = scenario_config
        return scenario_config
