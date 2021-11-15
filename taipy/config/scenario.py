from typing import List, Optional

from taipy.common import protect_name
from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository
from taipy.cycle.frequency import Frequency


class ScenarioConfig:
    def __init__(
        self, name: str, pipelines_configs: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties
    ):
        self.name = protect_name(name)
        self.pipelines_configs = pipelines_configs
        self.frequency = frequency
        self.properties = properties


class ScenarioConfigs(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, frequency=frequency, **properties)
        self._data[name] = scenario_config
        return scenario_config
