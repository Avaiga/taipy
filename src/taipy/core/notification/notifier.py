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
from typing import Dict, List, Optional

from .event import Event, EventEntityType, EventOperation
from .registration import Registration
from .topic import Topic


class Notifier:
    _registrations: Dict[Topic, List[Registration]] = {}  # What if this is a dictionary instead?

    @classmethod
    def register(
        cls,
        entity_type: Optional[str],
        entity_id: Optional[str],
        operation: Optional[str],
        attribute_name: Optional[str],
    ) -> Registration:
        registration = Registration(entity_type, entity_id, operation, attribute_name)

        if registrations := cls._registrations.get(registration.topic, None):
            registrations.append(registration)
        else:
            cls._registrations[registration.topic] = [registration]

        return registration

    @classmethod
    def unregister(cls, registration: Registration):
        if registrations := cls._registrations.get(registration.topic, None):
            registrations.remove(registration)
            if len(registrations) == 0:
                del cls._registrations[registration.topic]

    @classmethod
    def publish(cls, event: Event):
        generated_matched_topics_with_event = Topic.generate_topics_from_event(event)

        for topic in generated_matched_topics_with_event:
            if registrations := cls._registrations.get(topic, None):
                for registration in registrations:
                    registration.queue.put(event)
