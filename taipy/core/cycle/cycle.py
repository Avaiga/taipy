import uuid
from datetime import datetime
from typing import Any, Dict

from taipy.core.common.alias import CycleId
from taipy.core.common.entity import Entity
from taipy.core.common.frequency import Frequency
from taipy.core.common.reload import self_reload, self_setter
from taipy.core.common.unicode_to_python_variable_name import protect_name
from taipy.core.common.wrapper import Properties


class Cycle(Entity):
    """
    A Cycle object holds the frequency representing a work cycle.

    Attributes:
        frequency (Frequency): The frequency of the cycle
        properties (dict[str, str]): List of additional arguments.
        name (str): Name that identifies the cycle.
        creation_date (datetime): Date and time of the creation of the cycle
        start_date (datetime): Date and time of the start of the cycle
        end_date (datetime): Date and time of the end of the cycle
        id (str): Unique identifier of the cycle
    """

    ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"
    MANAGER_NAME = "cycle"

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
        self._frequency = frequency
        self._creation_date = creation_date
        self._start_date = start_date
        self._end_date = end_date
        self._name = self.new_name(name)
        self.id = id or self.new_id(self._name)
        self.properties = Properties(self, **properties)

    def new_name(self, name: str = None) -> str:
        return (
            protect_name(name)
            if name
            else Cycle.__SEPARATOR.join([str(self._frequency), self._creation_date.isoformat()])
        )

    @property  # type: ignore
    @self_reload("cycle")
    def frequency(self):
        return self._frequency

    @frequency.setter  # type: ignore
    @self_setter("cycle")
    def frequency(self, val):
        self._frequency = val

    @property  # type: ignore
    @self_reload("cycle")
    def creation_date(self):
        return self._creation_date

    @creation_date.setter  # type: ignore
    @self_setter("cycle")
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @self_reload("cycle")
    def start_date(self):
        return self._start_date

    @start_date.setter  # type: ignore
    @self_setter("cycle")
    def start_date(self, val):
        self._start_date = val

    @property  # type: ignore
    @self_reload("cycle")
    def end_date(self):
        return self._end_date

    @end_date.setter  # type: ignore
    @self_setter("cycle")
    def end_date(self, val):
        self._end_date = val

    @property  # type: ignore
    @self_reload("cycle")
    def name(self):
        return self._name

    @name.setter  # type: ignore
    @self_setter("cycle")
    def name(self, val):
        self._name = val

    @staticmethod
    def new_id(name: str) -> CycleId:
        return CycleId(Cycle.__SEPARATOR.join([Cycle.ID_PREFIX, protect_name(name), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of cycle {self.id}")

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
