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

from queue import SimpleQueue
from typing import Any, Dict, Optional, Set, Tuple

from ._registration import _Registration
from ._topic import _Topic
from .event import Event, EventEntityType, EventOperation


def _publish_event(
    entity_type: EventEntityType,
    operation: EventOperation,
    /,
    entity_id: Optional[str] = None,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> None:
    """Internal helper function to send events.

    It basically creates an event corresponding to the given arguments
    and send it using `Notifier.publish(event)`

    Parameters:
        entity_type (EventEntityType^)
        operation (EventOperation^)
        entity_id (Optional[str])
        attribute_name (Optional[str])
        attribute_value (Optional[Any])
        **kwargs
    """
    event = Event(
        entity_id=entity_id,
        entity_type=entity_type,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=kwargs,
    )
    Notifier.publish(event)


class Notifier:
    """A class for managing event registrations and publishing a Taipy application events."""

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

        The topic is defined by the combination of an optional entity type, an optional
        entity id, an optional operation, and an optional attribute name. The purpose is
        to be as flexible as possible. For example, we can register to:

        - All scenario creations
        - A specific data node update
        - A sequence submission
        - A Scenario deletion
        - Job failures

        !!! example "Standard usage"

            ```python
            registration_id, registered_queue = Notifier.register(
                entity_type=EventEntityType.SCENARIO,
                operation=EventOperation.CREATION
            )
            ```

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
                    <li>SUBMISSION</li>
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
    def unregister(cls, registration_id: str) -> None:
        """Unregister a listener.

        !!! example "Standard usage"

            ```python
            registration_id, registered_queue = Notifier.register(
                entity_type=EventEntityType.CYCLE,
                entity_id="CYCLE_cycle_1",
                operation=EventOperation.CREATION
            )

            Notifier.unregister(registration_id)
            ```

        Parameters:
            registration_id (`RegistrationId`): The registration id returned by the `register` method.
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
    def publish(cls, event: Event) -> None:
        """Publish a Taipy application event to all registered listeners whose topic matches the event.

        Parameters:
            event (`Event^`): The event to publish.
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
