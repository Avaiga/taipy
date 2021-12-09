from typing import Callable, Dict, List, Optional, Union

from taipy.common import protect_name
from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository
from taipy.cycle.frequency import Frequency
from taipy.exceptions.scenario import InvalidComparators


class ScenarioConfig:
    COMPARATOR_KEY = "comparators"

    def __init__(
        self, name: str, pipelines_configs: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties
    ):
        self.name = protect_name(name)
        self.pipelines_configs = pipelines_configs
        self.frequency = frequency
        self.comparators: Optional[Dict[str, Callable]] = None

        if self.COMPARATOR_KEY in properties.keys():
            self.comparators = properties["comparators"]

        properties.pop("comparators", None)
        self.properties = properties

    def set_comparator(self, ds_config_name: str, comparator: Callable):
        if self.comparators:
            self.comparators[ds_config_name] = comparator
        else:
            self.comparators = {ds_config_name: comparator}


class ScenarioConfigs(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, frequency=frequency, **properties)
        self._data[protect_name(name)] = scenario_config
        return scenario_config
