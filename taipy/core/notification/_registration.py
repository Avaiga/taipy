# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from queue import SimpleQueue
from typing import Optional, Set
from uuid import uuid4

from ._topic import _Topic
from .event import EventEntityType, EventOperation
from .registration_id import RegistrationId


class _Registration:

    _ID_PREFIX = "REGISTRATION"
    __SEPARATOR = "_"

    def __init__(self) -> None:
        self.registration_id: RegistrationId = self._new_id()
        self.queue: SimpleQueue = SimpleQueue()
        self.topics: Set[_Topic] = set()

    @staticmethod
    def from_topic(
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ) -> "_Registration":
        reg = _Registration()
        reg.topics.add(_Topic(entity_type, entity_id, operation, attribute_name))
        return reg

    @staticmethod
    def _new_id() -> RegistrationId:
        """Generate a unique registration identifier."""
        return RegistrationId(_Registration.__SEPARATOR.join([_Registration._ID_PREFIX, str(uuid4())]))

    def __hash__(self) -> int:
        return hash(self.registration_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Registration):
            return False
        return self.registration_id == other.registration_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return f"Registration ID: {self.registration_id}, Topics: {self.topics}"

    def __repr__(self) -> str:
        return self.__str__()

    def add_topic(
        self,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ) -> None:
        """Add a topic to the registration."""
        self.topics.add(_Topic(entity_type, entity_id, operation, attribute_name))

    def remove_topic(
        self,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ) -> None:
        """Remove a topic from the registration."""
        self.topics.remove(_Topic(entity_type, entity_id, operation, attribute_name))
