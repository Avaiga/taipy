import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from taipy.common import protect_name
from taipy.common.alias import CycleId
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.dimension import Dimension
from taipy.scenario.scenario import Scenario


class Cycle:

    __ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        dimension: Dimension,
        properties: Dict[str, str],
        scenarios: List[Scenario],
        creation_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cycle_id: CycleId = None,
    ):
        self.config_name = self.__protect_name(config_name)
        self.id: CycleId = cycle_id or self.new_id(config_name)
        self.dimension = dimension
        self.properties = properties
        self.scenarios = {scenario.config_name: scenario for scenario in scenarios}
        self.creation_date: datetime = creation_date or datetime.now()
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def __protect_name(config_name: str) -> str:
        return protect_name(config_name)

    @staticmethod
    def new_id(config_name: str) -> CycleId:
        return CycleId(
            Cycle.__SEPARATOR.join([Cycle.__ID_PREFIX, Cycle.__protect_name(config_name), str(uuid.uuid4())])
        )

    def __getattribute__(self, attribute_name: str):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        if protected_attribute_name in self.scenarios:
            return self.scenarios[protected_attribute_name]
        for scenario in self.scenarios.values():
            if protected_attribute_name in scenario.pipelines:
                return scenario.pipelines[protected_attribute_name]
            for pipeline in scenario.pipelines.values():
                if protected_attribute_name in pipeline.tasks:
                    return pipeline.tasks[protected_attribute_name]
                for task in pipeline.tasks:
                    if protected_attribute_name in task.input:
                        return task.input[protected_attribute_name]
                    if protected_attribute_name in task.output:
                        return task.output[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of cycle {self.id}")
        raise AttributeError

    def to_model(self) -> CycleModel:
        return CycleModel(
            self.id,
            self.config_name,
            self.dimension,
            [scenario.id for scenario in self.scenarios.values()],
            self.creation_date,
            self.start_date,
            self.end_date,
            self.properties,
        )
