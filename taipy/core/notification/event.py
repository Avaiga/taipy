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

from dataclasses import dataclass, field
from datetime import datetime
from functools import singledispatch
from typing import Any, Optional

from ..common._repr_enum import _ReprEnum
from ..exceptions.exceptions import InvalidEventAttributeName, InvalidEventOperation


class EventOperation(_ReprEnum):
    """Enum representing a type of operation performed on a Core entity.

    `EventOperation` is used as an attribute of the `Event^` object to describe the
    operation performed on an entity.<br>
    The possible operations are:

     - `CREATION`: Event related to a creation operation.
     - `UPDATE`: Event related to an update operation.
     - `DELETION`: Event related to a deletion operation.
     - `SUBMISSION`: Event related to a submission operation.

    """

    CREATION = 1
    UPDATE = 2
    DELETION = 3
    SUBMISSION = 4


class EventEntityType(_ReprEnum):
    """Enum representing an entity type.

    `EventEntityType` is used as an attribute of the `Event^` object to describe
    an entity that was changed.<br>
    The possible operations are:

    - `CYCLE`: Event related to a cycle entity.
    - `SCENARIO`: Event related to a scenario entity.
    - `SEQUENCE`: Event related to a sequence entity.
    - `TASK`: Event related to a task entity.
    - `DATA_NODE`: Event related to a data node entity.
    - `JOB`: Event related to a job entity.
    - `SUBMISSION`: Event related to a submission entity.
    """

    CYCLE = 1
    SCENARIO = 2
    SEQUENCE = 3
    TASK = 4
    DATA_NODE = 5
    JOB = 6
    SUBMISSION = 7


_NO_ATTRIBUTE_NAME_OPERATIONS = {EventOperation.CREATION, EventOperation.DELETION, EventOperation.SUBMISSION}
_UNSUBMITTABLE_ENTITY_TYPES = (
    EventEntityType.CYCLE,
    EventEntityType.DATA_NODE,
    EventEntityType.JOB,
    EventEntityType.SUBMISSION,
)
_ENTITY_TO_EVENT_ENTITY_TYPE = {
    "scenario": EventEntityType.SCENARIO,
    "sequence": EventEntityType.SEQUENCE,
    "task": EventEntityType.TASK,
    "data": EventEntityType.DATA_NODE,
    "job": EventEntityType.JOB,
    "cycle": EventEntityType.CYCLE,
    "submission": EventEntityType.SUBMISSION,
}


@dataclass(frozen=True)
class Event:
    """Event object used to notify any change in a Taipy application.

    An event holds the necessary attributes to identify the change.
    """

    entity_type: EventEntityType
    """Type of the entity that was changed (`DataNode^`, `Scenario^`, `Cycle^`, etc. )."""
    operation: EventOperation
    """Enum describing the operation that was performed on the entity.

    The operation is among `CREATION`, `UPDATE`, `DELETION`, and `SUBMISSION`.
    """
    entity_id: Optional[str] = None
    """Unique identifier of the entity that was changed."""
    attribute_name: Optional[str] = None
    """Name of the entity's attribute changed. Only relevant for `UPDATE` operations."""
    attribute_value: Optional[Any] = None
    """Value of the entity's attribute changed. Only relevant for `UPDATE` operations."""

    metadata: dict = field(default_factory=dict)
    """A dictionary of additional metadata about the source of this event."""
    creation_date: datetime = field(init=False)
    """Date and time of the event creation."""

    def __post_init__(self):
        # Creation date
        super().__setattr__("creation_date", datetime.now())

        # Check operation:
        if self.entity_type in _UNSUBMITTABLE_ENTITY_TYPES and self.operation == EventOperation.SUBMISSION:
            raise InvalidEventOperation

        # Check attribute name:
        if self.operation in _NO_ATTRIBUTE_NAME_OPERATIONS and self.attribute_name is not None:
            raise InvalidEventAttributeName


@singledispatch
def _make_event(
    entity: Any,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    """Helper function to make an event for this entity with the given `EventOperation^` type.
    In case of `EventOperation.UPDATE^` events, an attribute name and value must be given.

    Parameters:
        entity (Any): The entity object to generate an event for.
        operation (EventOperation^): The operation of the event. The possible values are:
            <ul>
                <li>CREATION</li>
                <li>UPDATE</li>
                <li>DELETION</li>
                <li>SUBMISSION</li>
            </ul>
        attribute_name (Optional[str]): The name of the updated attribute for a `EventOperation.UPDATE`.
            This argument is always given in case of an UPDATE.
        attribute_value (Optional[Any]): The value of the updated attribute for a `EventOperation.UPDATE`.
            This argument is always given in case of an UPDATE.
        **kwargs (dict[str, any]): Any extra information that would be passed to the metadata event.
            Note: you should pass only simple types: str, float, double as values."""
    raise Exception(f"Unexpected entity type: {type(entity)}")
