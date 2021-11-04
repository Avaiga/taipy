import re
import unidecode
from typing import List

from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository


class ScenarioConfig:
    def __init__(self, name: str, pipelines_configs: List[PipelineConfig], **properties):
        self.name = re.sub(r'[\W]+', '-', unidecode.unidecode(name).strip().lower().replace(' ', '_'))
        self.pipelines_configs = pipelines_configs
        self.properties = properties


class ScenarioConfigs(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, **properties)
        self._data[name] = scenario_config
        return scenario_config
