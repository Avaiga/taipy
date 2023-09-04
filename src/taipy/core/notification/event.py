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

from datetime import datetime
from typing import Optional

from ..common._repr_enum import _ReprEnum
from ..exceptions.exceptions import InvalidEventAttributeName, InvalidEventOperation


class EventOperation(_ReprEnum):
    """Enum representing a type of operation performed on a Core entity.

    `EventOperation` is used as an attribute of the `Event^` object to describe the
    operation performed on an entity.<br>
    The possible operations are `CREATION`, `UPDATE`, `DELETION`, or `SUBMISSION`.
    """

    CREATION = 1
    UPDATE = 2
    DELETION = 3
    SUBMISSION = 4


class EventEntityType(_ReprEnum):
    """Enum representing an entity type.

    `EventEntityType` is used as an attribute of the `Event^` object to describe
    an entity that was changed.<br>
    The possible operations are `CYCLE`, `SCENARIO`, `SEQUENCE`, `TASK`, `DATA_NODE`, or `JOB`.
    """

    CYCLE = 1
    SCENARIO = 2
    SEQUENCE = 3
    TASK = 4
    DATA_NODE = 5
    JOB = 6


_NO_ATTRIBUTE_NAME_OPERATIONS = set([EventOperation.CREATION, EventOperation.DELETION, EventOperation.SUBMISSION])
_UNSUBMITTABLE_ENTITY_TYPES = (EventEntityType.CYCLE, EventEntityType.DATA_NODE, EventEntityType.JOB)
_ENTITY_TO_EVENT_ENTITY_TYPE = {
    "scenario": EventEntityType.SCENARIO,
    "sequence": EventEntityType.SEQUENCE,
    "task": EventEntityType.TASK,
    "data": EventEntityType.DATA_NODE,
    "job": EventEntityType.JOB,
    "cycle": EventEntityType.CYCLE,
}


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
        creation_date (datetime): Date and time of the event creation.
    """

    def __init__(
        self,
        entity_type: EventEntityType,
        entity_id: Optional[str],
        operation: EventOperation,
        attribute_name: Optional[str] = None,
    ):
        self.creation_date = datetime.now()
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.operation = self.__preprocess_operation(operation, entity_type)
        self.attribute_name = self.__preprocess_attribute_name(attribute_name, operation)

    @classmethod
    def __preprocess_attribute_name(cls, attribute_name: Optional[str], operation: EventOperation) -> Optional[str]:
        if operation in _NO_ATTRIBUTE_NAME_OPERATIONS and attribute_name is not None:
            raise InvalidEventAttributeName
        return attribute_name

    @classmethod
    def __preprocess_operation(cls, operation: EventOperation, entity_type: EventEntityType) -> EventOperation:
        if entity_type in _UNSUBMITTABLE_ENTITY_TYPES and operation == EventOperation.SUBMISSION:
            raise InvalidEventOperation
        return operation
