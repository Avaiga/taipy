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
    The possible operations are `CREATION`, `UPDATE`, `DELETION`, or `SUBMISSION`.
    """

    CREATION = 1
    """Event related to a creation operation."""
    UPDATE = 2
    """Event related to an update operation."""
    DELETION = 3
    """Event related to a deletion operation."""
    SUBMISSION = 4
    """Event related to a submission operation."""


class EventEntityType(_ReprEnum):
    """Enum representing an entity type.

    `EventEntityType` is used as an attribute of the `Event^` object to describe
    an entity that was changed.<br>
    The possible operations are `CYCLE`, `SCENARIO`, `SEQUENCE`, `TASK`, `DATA_NODE`, `JOB` or `SUBMISSION`.
    """

    CYCLE = 1
    """Event related to a cycle entity."""
    SCENARIO = 2
    """Event related to a scenario entity."""
    SEQUENCE = 3
    """Event related to a sequence entity."""
    TASK = 4
    """Event related to a task entity."""
    DATA_NODE = 5
    """Event related to a data node entity."""
    JOB = 6
    """Event related to a job entity."""
    SUBMISSION = 7
    """Event related to a submission entity."""


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
    """Event object used to notify any change in the Core service.

    An event holds the necessary attributes to identify the change.

    Attributes:
        entity_type (EventEntityType^): Type of the entity that was changed (`DataNode^`,
            `Scenario^`, `Cycle^`, etc. ).
        entity_id (Optional[str]): Unique identifier of the entity that was changed.
        operation (EventOperation^): Enum describing the operation (among `CREATION`, `UPDATE`, `DELETION`,
            and `SUBMISSION`) that was performed on the entity.
        attribute_name (Optional[str]): Name of the entity's attribute changed. Only relevant for `UPDATE`
            operations
        attribute_value (Optional[str]): Name of the entity's attribute changed. Only relevant for `UPDATE`
            operations
        metadata (dict): A dict of additional medata about the source of this event
        creation_date (datetime): Date and time of the event creation.
    """

    entity_type: EventEntityType
    operation: EventOperation
    entity_id: Optional[str] = None
    attribute_name: Optional[str] = None
    attribute_value: Optional[Any] = None

    metadata: dict = field(default_factory=dict)
    creation_date: datetime = field(init=False)

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
