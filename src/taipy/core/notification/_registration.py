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

from queue import SimpleQueue
from typing import Optional
from uuid import uuid4

from ._topic import _Topic
from .event import EventEntityType, EventOperation
from .registration_id import RegistrationId


class _Registration:

    _ID_PREFIX = "REGISTRATION"
    __SEPARATOR = "_"

    def __init__(
        self,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ):

        self.registration_id: str = self._new_id()
        self.topic: _Topic = _Topic(entity_type, entity_id, operation, attribute_name)
        self.queue: SimpleQueue = SimpleQueue()

    @staticmethod
    def _new_id() -> RegistrationId:
        """Generate a unique registration identifier."""
        return RegistrationId(_Registration.__SEPARATOR.join([_Registration._ID_PREFIX, str(uuid4())]))

    def __hash__(self) -> int:
        return hash(self.registration_id)
