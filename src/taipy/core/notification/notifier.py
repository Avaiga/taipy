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
from typing import Dict, Optional, Set, Tuple

from .event import Event, EventEntityType, EventOperation
from .registration import Registration
from .topic import Topic


def _publish_event(
    entity_type: EventEntityType,
    entity_id: Optional[str],
    operation: EventOperation,
    attribute_name: Optional[str] = None,
):
    Notifier.publish(Event(entity_type, entity_id, operation, attribute_name))


class Notifier:
    _topics_registrations_list: Dict[Topic, Set[Registration]] = {}

    @classmethod
    def register(
        cls,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ) -> Tuple[str, SimpleQueue]:
        registration = Registration(entity_type, entity_id, operation, attribute_name)

        if registrations := cls._topics_registrations_list.get(registration.topic, None):
            registrations.add(registration)
        else:
            cls._topics_registrations_list[registration.topic] = {registration}

        return registration.registration_id, registration.queue

    @classmethod
    def unregister(cls, registration_id: str):
        to_remove_registration: Optional[Registration] = None

        for _, registrations in cls._topics_registrations_list.items():
            for registration in registrations:
                if registration.registration_id == registration_id:
                    to_remove_registration = registration
                    break

        if to_remove_registration:
            registrations = cls._topics_registrations_list[to_remove_registration.topic]
            registrations.remove(to_remove_registration)
            if len(registrations) == 0:
                del cls._topics_registrations_list[to_remove_registration.topic]

    @classmethod
    def publish(cls, event):
        for topic, registrations in cls._topics_registrations_list.items():
            if Notifier.is_matching(event, topic):
                for registration in registrations:
                    registration.queue.put(event)

    @staticmethod
    def is_matching(event: Event, topic: Topic) -> bool:
        if topic.entity_type is not None and event.entity_type != topic.entity_type:
            return False
        if topic.entity_id is not None and event.entity_id != topic.entity_id:
            return False
        if topic.operation is not None and event.operation != topic.operation:
            return False
        if topic.attribute_name is not None and event.attribute_name and event.attribute_name != topic.attribute_name:
            return False
        return True
