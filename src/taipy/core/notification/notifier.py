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
from typing import Dict, List, Optional, Tuple

from ..exceptions.exceptions import NonExistingRegistration
from .event import Event
from .registration import Registration
from .topic import Topic


class Notifier:
    _topics_subscribers_list: Dict[Topic, List[Registration]] = {}
    _registrations: Dict[str, Registration] = {}

    @classmethod
    def register(
        cls,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        operation: Optional[str] = None,
        attribute_name: Optional[str] = None,
    ) -> Tuple[str, SimpleQueue]:
        registration = Registration(entity_type, entity_id, operation, attribute_name)

        cls._registrations[registration.register_id] = registration

        if registrations := cls._topics_subscribers_list.get(registration.topic, None):
            registrations.append(registration)
        else:
            cls._topics_subscribers_list[registration.topic] = [registration]

        return registration.register_id, registration.queue

    @classmethod
    def unregister(cls, registration_id: str):
        try:
            registration = cls._registrations[registration_id]
            if registrations := cls._topics_subscribers_list.get(registration.topic, None):
                registrations.remove(registration)
                if len(registrations) == 0:
                    del cls._topics_subscribers_list[registration.topic]
            del cls._registrations[registration_id]
        except KeyError:
            raise NonExistingRegistration(registration_id)

    @classmethod
    def publish(cls, event: Event):
        generated_matched_topics_with_event = cls.generate_topics_from_event(event)

        for topic in generated_matched_topics_with_event:
            if registrations := cls._topics_subscribers_list.get(topic, None):
                for registration in registrations:
                    registration.queue.put(event)

    @staticmethod
    def generate_topics_from_event(event: Event):
        # can this be improved by caching?
        TOPIC_ATTRIBUTES_TO_SET_NONE: list = [
            [
                "entity_type",
                "entity_id",
                "operation",
                "attribute_name",
            ],
            [
                "entity_id",
                "operation",
                "attribute_name",
            ],
            [
                "entity_type",
                "entity_id",
            ],
            [
                "entity_type",
                "entity_id",
                "attribute_name",
            ],
            [
                "entity_type",
                "entity_id",
                "operation",
            ],
            [
                "entity_id",
                "attribute_name",
            ],
            [
                "entity_id",
                "operation",
            ],
            [
                "attribute_name",
            ],
            ["operation"],
            [
                "entity_type",
                "entity_id",
            ],
            [
                "entity_id",
            ],
            [],
        ]

        def generate_topic_parameters_from_event(event: Event):
            return {
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "operation": event.operation,
                "attribute_name": event.attribute_name,
            }

        topics = []

        for topic_attributes_to_set_None in TOPIC_ATTRIBUTES_TO_SET_NONE:
            topic_parameters = generate_topic_parameters_from_event(event)
            for topic_attribute in topic_attributes_to_set_None:
                topic_parameters[topic_attribute] = None
            topics.append(Topic(**topic_parameters))
        return topics
