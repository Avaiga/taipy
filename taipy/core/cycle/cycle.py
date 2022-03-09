import uuid
from datetime import datetime
from typing import Any, Dict

from taipy.core.common._entity import _Entity
from taipy.core.common._get_valid_filename import _get_valid_filename
from taipy.core.common._properties import _Properties
from taipy.core.common._reload import reload, self_reload, self_setter
from taipy.core.common.alias import CycleId
from taipy.core.common.frequency import Frequency


class Cycle(_Entity):
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
        self._name = self._new_name(name)
        self.id = id or self._new_id(self._name)
        self._properties = _Properties(self, **properties)

    def _new_name(self, name: str = None) -> str:
        return name if name else Cycle.__SEPARATOR.join([str(self._frequency), self._creation_date.isoformat()])

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def frequency(self):
        return self._frequency

    @frequency.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def frequency(self, val):
        self._frequency = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def creation_date(self):
        return self._creation_date

    @creation_date.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def start_date(self):
        return self._start_date

    @start_date.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def start_date(self, val):
        self._start_date = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def end_date(self):
        return self._end_date

    @end_date.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def end_date(self, val):
        self._end_date = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def name(self):
        return self._name

    @name.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def name(self, val):
        self._name = val

    @property  # type: ignore
    def properties(self):
        self._properties = reload(self.MANAGER_NAME, self)._properties
        return self._properties

    @staticmethod
    def _new_id(name: str) -> CycleId:
        return CycleId(_get_valid_filename(Cycle.__SEPARATOR.join([Cycle._ID_PREFIX, name, str(uuid.uuid4())])))

    def __getattr__(self, attribute_name):
        protected_attribute_name = attribute_name
        if protected_attribute_name in self._properties:
            return self._properties[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of cycle {self.id}")

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
