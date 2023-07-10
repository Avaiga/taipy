# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from taipy.config.common.frequency import Frequency

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from ..exceptions.exceptions import _SuspiciousFileOperation
from .cycle_id import CycleId


class Cycle(_Entity, _Labeled):
    """An iteration of a recurrent work pattern.

    Attributes:
        id (str): The unique identifier of the cycle.
        frequency (Frequency^): The frequency of this cycle.
        creation_date (datetime): The date and time of the creation of this cycle.
        start_date (datetime): The date and time of the start of this cycle.
        end_date (datetime): The date and time of the end of this cycle.
        name (str): The name of this cycle.
        properties (dict[str, Any]): A dictionary of additional properties.
    """

    _ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"
    _MANAGER_NAME = "cycle"

    def __init__(
        self,
        frequency: Frequency,
        properties: Dict[str, Any],
        creation_date: datetime,
        start_date: datetime,
        end_date: datetime,
        name: Optional[str] = None,
        id: Optional[CycleId] = None,
    ):
        self._frequency = frequency
        self._creation_date = creation_date
        self._start_date = start_date
        self._end_date = end_date
        self._name = self._new_name(name)
        self.id = id or self._new_id(self._name)
        self._properties = _Properties(self, **properties)

    def _new_name(self, name: Optional[str] = None) -> str:
        if name:
            return name
        if self._frequency == Frequency.DAILY:
            # Example "Monday, 2. January 2023"
            return self._start_date.strftime("%A, %d. %B %Y")
        if self._frequency == Frequency.WEEKLY:
            # Example "Week 01 2023, from 2. January"
            return self._start_date.strftime("Week %W %Y, from %d. %B")
        if self._frequency == Frequency.MONTHLY:
            # Example "January 2023"
            return self._start_date.strftime("%B %Y")
        if self._frequency == Frequency.QUARTERLY:
            # Example "2023 Q1"
            return f"{self._start_date.strftime('%Y')} Q{(self._start_date.month-1)//3+1}"
        if self._frequency == Frequency.YEARLY:
            # Example "2023"
            return self._start_date.strftime("%Y")
        return Cycle.__SEPARATOR.join([str(self._frequency.value), self._start_date.ctime()])

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def frequency(self):
        return self._frequency

    @frequency.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def frequency(self, val):
        self._frequency = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def creation_date(self):
        return self._creation_date

    @creation_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def start_date(self):
        return self._start_date

    @start_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def start_date(self, val):
        self._start_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def end_date(self):
        return self._end_date

    @end_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def end_date(self, val):
        self._end_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def name(self):
        return self._name

    @name.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def name(self, val):
        self._name = val

    @property
    def properties(self):
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @staticmethod
    def _new_id(name: str) -> CycleId:
        def _get_valid_filename(name: str) -> str:
            """
            Source: https://github.com/django/django/blob/main/django/utils/text.py
            """
            s = str(name).strip().replace(" ", "_")
            s = re.sub(r"(?u)[^-\w.]", "", s)
            if s in {"", ".", ".."}:
                raise _SuspiciousFileOperation("Could not derive file name from '%s'" % name)
            s = str(s).strip().replace(" ", "_")
            return re.sub(r"(?u)[^-\w.]", "", s)

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

    def get_label(self) -> str:
        """Returns the cycle label.

        Returns:
            The label of the cycle as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the cycle simple label.

        Returns:
            The simple label of the cycle as a string.
        """
        return self._get_simple_label()
