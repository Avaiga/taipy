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

"""
Package for notifications about changes on `Core^` service entities.


The Core service generates `Event^` objects to track changes on entities.
These events are then relayed to a `Notifier^`, which handles the dispatch
to consumers interested in specific event topics.

To subscribe, a consumer needs to invoke the `Notifier.register()^` method.
This call will yield a `RegistrationId^` and a dedicated event queue for
receiving notifications.

To handle notifications, an event consumer (e.g., the `CoreEventConsumerBase^`
object) must be instantiated with an associated event queue.
"""

from ._registration import _Registration
from ._topic import _Topic
from .core_event_consumer import CoreEventConsumerBase
from .event import _ENTITY_TO_EVENT_ENTITY_TYPE, Event, EventEntityType, EventOperation
from .notifier import Notifier, _publish_event
from .registration_id import RegistrationId
