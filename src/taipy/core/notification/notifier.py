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

from ._registration import _Registration
from ._topic import _Topic
from .event import Event, EventEntityType, EventOperation


def _publish_event(
    entity_type: EventEntityType,
    entity_id: Optional[str],
    operation: EventOperation,
    attribute_name: Optional[str] = None,
):
    Notifier.publish(Event(entity_type, entity_id, operation, attribute_name))


class Notifier:
    """A class for managing event registrations and publishing `Core^` service events."""

    _topics_registrations_list: Dict[_Topic, Set[_Registration]] = {}

    @classmethod
    def register(
        cls,
        entity_type: Optional[EventEntityType] = None,
        entity_id: Optional[str] = None,
        operation: Optional[EventOperation] = None,
        attribute_name: Optional[str] = None,
    ) -> Tuple[str, SimpleQueue]:
        """Register a listener for a specific event topic.

        The topic is defined by the combination of the entity type, the entity id,
        the operation and the attribute name.

        Parameters:
            entity_type (Optional[EventEntityType^]): If provided, the listener will
                be notified for all events related to this entity type. Otherwise,
                the listener will be notified for events related to all entity types.
                <br>
                The possible entity type values are defined in the `EventEntityType^`
                enum. The possible values are:
                <ul>
                    <li>CYCLE</li>
                    <li>SCENARIO</li>
                    <li>SEQUENCE</li>
                    <li>TASK</li>
                    <li>DATA_NODE</li>
                    <li>JOB</li>
                </ul>
            entity_id (Optional[str]): If provided, the listener will be notified
                for all events related to this entity. Otherwise, the listener
                will be notified for events related to all entities.
            operation (Optional[EventOperation^]): If provided, the listener will
                be notified for all events related to this operation. Otherwise,
                the listener will be notified for events related to all operations.
                <br>
                The possible operation values are defined in the `EventOperation^`
                enum. The possible values are:
                <ul>
                    <li>CREATION</li>
                    <li>UPDATE</li>
                    <li>DELETION</li>
                    <li>SUBMISSION</li>
                </ul>
            attribute_name (Optional[str]): If provided, the listener will be notified
                for all events related to this entity's attribute. Otherwise, the listener
                will be notified for events related to all attributes.

        Returns:
            A tuple containing the registration id and the event queue.
        """
        registration = _Registration(entity_type, entity_id, operation, attribute_name)

        if registrations := cls._topics_registrations_list.get(registration.topic, None):
            registrations.add(registration)
        else:
            cls._topics_registrations_list[registration.topic] = {registration}

        return registration.registration_id, registration.queue

    @classmethod
    def unregister(cls, registration_id: str):
        """Unregister a listener.

        Parameters:
            registration_id (RegistrationId^): The registration id returned by the `register` method.
        """
        to_remove_registration: Optional[_Registration] = None

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
        """Publish a `Core^` service event to all registered listeners whose topic matches the event.

        Parameters:
            event (Event^): The event to publish.
        """
        for topic, registrations in cls._topics_registrations_list.items():
            if Notifier._is_matching(event, topic):
                for registration in registrations:
                    registration.queue.put(event)

    @staticmethod
    def _is_matching(event: Event, topic: _Topic) -> bool:
        """Check if an event matches a topic."""
        if topic.entity_type is not None and event.entity_type != topic.entity_type:
            return False
        if topic.entity_id is not None and event.entity_id != topic.entity_id:
            return False
        if topic.operation is not None and event.operation != topic.operation:
            return False
        if topic.attribute_name is not None and event.attribute_name and event.attribute_name != topic.attribute_name:
            return False
        return True
