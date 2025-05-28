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
from abc import abstractmethod

from taipy.core.notification import Event


class _AbstractEventProcessor:
    """Abstract base class for implementing an event processor."""

    @classmethod
    @abstractmethod
    def process_event(cls, event_processor, event: Event):
        raise NotImplementedError("Subclasses must implement this method.")

class _EventProcessor(_AbstractEventProcessor):

    @classmethod
    def process_event(cls, event_processor, event: Event):
        event_processor._process_event(event)

