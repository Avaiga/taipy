import uuid
from datetime import datetime
from typing import Any, Dict

from taipy.core.common._get_valid_filename import _get_valid_filename
from taipy.core.common._properties import _Properties
from taipy.core.common.alias import CycleId
from taipy.core.common.frequency import Frequency


class Cycle:
    """
    Represents an iteration of a recurrent work pattern.

    Attributes:
        id (str): The Unique identifier of the cycle.
        frequency (Frequency): The `Frequency^` of the cycle.
        creation_date (datetime): The date and time of the creation of the cycle.
        start_date (datetime): The date and time of the start of the cycle.
        end_date (datetime): The date and time of the end of the cycle.
        name (str): The name of the cycle.
        properties (dict[str, str]): The list of additional arguments.
    """

    _ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"

    def __init__(
        self,
        frequency: Frequency,
        properties: Dict[str, Any],
        creation_date: datetime,
        start_date: datetime,
        end_date: datetime,
        name: str = None,
        id: CycleId = None,
    ):
        self.frequency = frequency
        self.creation_date = creation_date
        self.start_date = start_date
        self.end_date = end_date
        self.name = self._new_name(name)
        self.id = id or self._new_id(self.name)
        self.properties = _Properties(self, **properties)

    def _new_name(self, name: str = None) -> str:
        return name if name else Cycle.__SEPARATOR.join([str(self.frequency), self.creation_date.isoformat()])

    @staticmethod
    def _new_id(name: str) -> CycleId:
        return CycleId(_get_valid_filename(Cycle.__SEPARATOR.join([Cycle._ID_PREFIX, name, str(uuid.uuid4())])))

    def __getattr__(self, attribute_name):
        protected_attribute_name = attribute_name
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of cycle {self.id}")

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
