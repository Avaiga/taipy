import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from taipy.common import protect_name
from taipy.common.alias import CycleId
from taipy.cycle.cycle_model import CycleModel
from taipy.cycle.frequency import Frequency


class Cycle:

    __ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        frequency: Frequency,
        properties: Dict[str, str],
        creation_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        id: CycleId = None,
    ):
        self.name = self.__protect_name(name)
        self.id: CycleId = id or self.new_id(name)
        self.frequency = frequency
        self.properties = properties
        self.creation_date: datetime = creation_date or datetime.now()
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def __protect_name(config_name: str) -> str:
        return protect_name(config_name)

    @staticmethod
    def new_id(name: str) -> CycleId:
        return CycleId(Cycle.__SEPARATOR.join([Cycle.__ID_PREFIX, Cycle.__protect_name(name), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of cycle {self.id}")
        raise AttributeError

    def __eq__(self, other):
        return self.id == other.id
