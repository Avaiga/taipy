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

from queue import Queue
from typing import List, Tuple

from .event import Event
from .registration import Registration
from .topic import Topic


class Notifier:
    # TODO add a lock on _registration
    _registrations: List[Registration] = []

    @classmethod
    def register(cls, entity_type, entity_id, operation, attribute_name, time_to_live) -> Tuple[str, Queue]:
        register_id = "gui"  # TODO generate an id to return so the client can unregister.
        registration = Registration(register_id, entity_type, entity_id, operation, attribute_name, time_to_live)
        # TODO lock before updating cls._registrations
        cls._registrations.append(registration)
        return register_id, registration.queue

    @classmethod
    def unregister(cls, register_id: str = "gui"):
        # TODO lock before updating cls._registrations
        cls._registrations = [reg for reg in cls._registrations if reg.register_id != register_id]

    @classmethod
    def publish(cls, event: Event):
        for registration in cls._registrations:
            if cls.is_matching(event, registration.topic):
                registration.queue.put(event)

    @classmethod
    def is_matching(cls, event: Event, topic: Topic) -> bool:
        # TODO implement logic to see if event matches the topic
        return True
