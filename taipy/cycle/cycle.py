import calendar
import logging
import uuid
from datetime import datetime, time, timedelta
from typing import Dict, Optional

from taipy.common import protect_name
from taipy.common.alias import CycleId
from taipy.cycle.frequency import Frequency


class Cycle:

    __ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"

    def __init__(
        self,
        frequency: Frequency,
        properties: Dict[str, str],
        name: str = None,
        creation_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,  # mandatory
        end_date: Optional[datetime] = None,  # mandatory
        id: CycleId = None,
    ):
        self.frequency = frequency
        self.properties = properties
        self.creation_date = creation_date or datetime.now()
        self.name = self.new_name(name)
        self.id = id or self.new_id(self.name)
        # auto generated from creation date or should not be None
        self.start_date = start_date if start_date else self.__get_start_date_of_cycle()
        # auto generated from start date or should not be None
        self.end_date = end_date if end_date else self.__get_end_date_of_cycle()

    def new_name(self, name: str = None) -> str:
        return (
            protect_name(name)
            if name
            else Cycle.__SEPARATOR.join([str(self.frequency), self.creation_date.isoformat()])
        )

    def __get_start_date_of_cycle(self):
        start_date = self.creation_date.date()
        start_time = time()
        if self.frequency == Frequency.DAILY:
            start_date = start_date
        if self.frequency == Frequency.WEEKLY:
            start_date = start_date - timedelta(days=start_date.weekday())
        if self.frequency == Frequency.MONTHLY:
            start_date = start_date.replace(day=1)
        if self.frequency == Frequency.YEARLY:
            start_date = start_date.replace(day=1, month=1)
        return datetime.combine(start_date, start_time)

    def __get_end_date_of_cycle(self):

        end_date = self.start_date
        print(type(end_date))
        if self.frequency == Frequency.DAILY:
            end_date = end_date + timedelta(days=1)
        if self.frequency == Frequency.WEEKLY:
            end_date = end_date + timedelta(7 - end_date.weekday())
        if self.frequency == Frequency.MONTHLY:
            last_day_of_month = calendar.monthrange(self.start_date.year, self.start_date.month)[1]
            end_date = end_date.replace(day=last_day_of_month) + timedelta(days=1)
        if self.frequency == Frequency.YEARLY:
            end_date = end_date.replace(month=12, day=31) + timedelta(days=1)
        return end_date - timedelta(microseconds=1)

    @staticmethod
    def new_id(name: str) -> CycleId:
        return CycleId(Cycle.__SEPARATOR.join([Cycle.__ID_PREFIX, protect_name(name), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of cycle {self.id}")
        raise AttributeError

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
