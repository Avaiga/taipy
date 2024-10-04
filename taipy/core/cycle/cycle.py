# Copyright 2021-2024 Avaiga Private Limited
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

from taipy.common.config.common.frequency import Frequency

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from ..exceptions.exceptions import _SuspiciousFileOperation
from ..notification.event import Event, EventEntityType, EventOperation, _make_event
from .cycle_id import CycleId


class Cycle(_Entity, _Labeled):
    """An iteration of a recurrent work pattern.

    Many business operations are periodic, such as weekly predictions of sales data, monthly
    master planning of supply chains, quarterly financial reports, yearly budgeting, etc.
    The data applications to solve these business problems often require modeling the
    corresponding periods (i.e., cycles).

    For this purpose, a `Cycle` represents a single iteration of such a time pattern.
    Each _cycle_ has a start date and a duration. Examples of cycles are:

    - Monday, 2. January 2023 as a daily cycle
    - Week 01 2023, from 2. January as a weekly cycle
    - January 2023 as a monthly cycle
    - etc.

    `Cycle`s are created along with the `Scenario^`s that are attached to them.
    At its creation, a new scenario is attached to a single cycle, the one that
    matches its optional _frequency_ and its _creation_date_.

    The possible frequencies are:

    - `Frequency.DAILY`
    - `Frequency.WEEKLY`
    - `Frequency.MONTHLY`
    - `Frequency.QUARTERLY`
    - `Frequency.YEARLY`

    !!! example "Example for January cycle"

        ![cycles](../../../../img/cycles_january_colored.svg){ align=left width="250" }

        Let's assume an end-user publishes production orders (i.e., a production plan) every
        month. During each month (the cycle), he/she will be interested in experimenting with
        different scenarios until only one of those scenarios is selected as the official
        production plan to be published. Each month is modeled as a cycle, and each cycle
        can contain one or more scenarios.

        The picture on the left shows the tree of entities: Cycles, Scenarios, and their
        associated Sequence(s). There is an existing past cycle for December and a current
        cycle for January containing a single scenario.

    When comes the end of a _cycle_ (start date + duration), only one of the scenarios is
    applied in production. This "official" scenario is called the _**primary scenario**_.
    Only one _**primary scenario**_ per cycle is allowed.

    !!! example "Example for February cycle"

        ![cycles](../../../../img/cycles_colored.svg){ align=left width="250" }
        Now the user starts working on the February work cycle. He or she creates two
        scenarios for the February cycle (one with a low capacity assumption and one with
        a high capacity assumption). The user can then decide to elect the low capacity
        scenario as the "official" scenario for February. To accomplish that, he just
        needs to promote the low capacity scenario as _**primary**_ for the February cycle.

        The tree of entities resulting from the various scenarios created is represented
        in the picture on the left. The underlined scenarios are _**primary**_.

    !!! note

        For a scenario, cycles are optional. If a scenario has no Frequency, it will not be
        attached to any cycle.

    """

    _ID_PREFIX = "CYCLE"
    __SEPARATOR = "_"
    _MANAGER_NAME = "cycle"

    id:CycleId
    """The unique identifier of the cycle."""

    def __init__(
        self,
        frequency: Frequency,
        properties: Dict[str, Any],
        creation_date: datetime,
        start_date: datetime,
        end_date: datetime,
        name: Optional[str] = None,
        id: Optional[CycleId] = None,
    ) -> None:
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
    def frequency(self) -> Frequency:
        """The frequency of this cycle."""
        return self._frequency

    @frequency.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def frequency(self, val):
        self._frequency = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def creation_date(self) -> datetime:
        """The date and time of the creation of this cycle."""
        return self._creation_date

    @creation_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def start_date(self) -> datetime:
        """The date and time of the start of this cycle."""
        return self._start_date

    @start_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def start_date(self, val):
        self._start_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def end_date(self) -> datetime:
        """The date and time of the end of this cycle."""
        return self._end_date

    @end_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def end_date(self, val):
        self._end_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def name(self) -> str:
        """The name of this cycle."""
        return self._name

    @name.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def name(self, val):
        self._name = val

    @property
    def properties(self) -> _Properties:
        """A dictionary of additional properties."""
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @staticmethod
    def _new_id(name: str) -> CycleId:
        def _get_valid_filename(name: str) -> str:
            """
            Source: https://github.com/django/django/blob/main/django/utils/text.py
            """
            s = name.strip().replace(" ", "_")
            s = re.sub(r"(?u)[^-\w.]", "", s)
            if s in {"", ".", ".."}:
                raise _SuspiciousFileOperation(f"Could not derive file name from '{name}'")
            s = s.strip().replace(" ", "_")
            return re.sub(r"(?u)[^-\w.]", "", s)

        return CycleId(_get_valid_filename(Cycle.__SEPARATOR.join([Cycle._ID_PREFIX, name, str(uuid.uuid4())])))

    def __eq__(self, other):
        return isinstance(other, Cycle) and self.id == other.id

    def __hash__(self) -> int:
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


@_make_event.register(Cycle)
def _make_event_for_cycle(
    cycle: Cycle,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {**kwargs}
    return Event(
        entity_type=EventEntityType.CYCLE,
        entity_id=cycle.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
