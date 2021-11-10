import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from taipy.common import protect_name
from taipy.common.alias import CycleId
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.frequency import Frequency

# from taipy.scenario import Scenario


class Cycle:

    __ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        frequency: Frequency,
        properties: Dict[str, str],
        creation_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cycle_id: CycleId = None,
    ):
        self.config_name = self.__protect_name(config_name)
        self.id: CycleId = cycle_id or self.new_id(config_name)
        self.frequency = frequency
        self.properties = properties
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
        logging.error(f"{attribute_name} is not an attribute of cycle {self.id}")
        raise AttributeError

    def to_model(self) -> CycleModel:
        return CycleModel(
            self.id,
            self.config_name,
            self.frequency,
            self.creation_date,
            self.start_date,
            self.end_date,
            self.properties,
        )
