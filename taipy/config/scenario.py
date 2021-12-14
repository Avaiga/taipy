from collections import defaultdict
from typing import Callable, List, Optional

from taipy.common import protect_name
from taipy.config import PipelineConfig
from taipy.config.interface import ConfigRepository
from taipy.cycle.frequency import Frequency
from taipy.exceptions.scenario import NonExistingComparator


class ScenarioConfig:
    COMPARATOR_KEY = "comparators"

    def __init__(
        self, name: str, pipelines_configs: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties
    ):
        self.name = protect_name(name)
        self.pipelines_configs = pipelines_configs
        self.frequency = frequency
        self.comparators = defaultdict(list)

        if self.COMPARATOR_KEY in properties.keys():
            for k, v in properties[self.COMPARATOR_KEY].items():
                self.comparators[k] = v
            del properties[self.COMPARATOR_KEY]

        self.properties = properties

    def add_comparator(self, ds_config_name: str, comparator: Callable):
        self.comparators[ds_config_name].append(comparator)

    def delete_comparator(self, ds_config_name: str):
        if ds_config_name in self.comparators:
            del self.comparators[ds_config_name]
        else:
            raise NonExistingComparator


class ScenarioConfigs(ConfigRepository):
    def create(self, name: str, pipelines: List[PipelineConfig], frequency: Optional[Frequency] = None, **properties):  # type: ignore
        scenario_config = ScenarioConfig(name, pipelines, frequency=frequency, **properties)
        self._data[protect_name(name)] = scenario_config
        return scenario_config
