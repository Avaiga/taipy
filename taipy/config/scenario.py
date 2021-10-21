from typing import List

from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository


class ScenarioConfig:
    def __init__(self, name: str, pipelines: List[PipelineConfig], **properties):
        self.name = name.strip().lower().replace(" ", "_")
        self.pipelines = pipelines
        self.properties = properties


class ScenariosRepository(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, **properties)
        self._data[name] = scenario_config
        return scenario_config
