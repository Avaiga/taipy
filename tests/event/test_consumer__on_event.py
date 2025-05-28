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

import pytest

from taipy import Gui
from taipy.core.notification import Event, EventEntityType, EventOperation, _Topic
from taipy.event._event_callback import _Callback
from taipy.event.event_processor import EventProcessor
from taipy.event.exceptions.exceptions import NoGuiDefinedInEventProcessor


def cb_0(event: Event, extra:str):
    ...


def cb_1(event: Event):
    ...


def cb_2(event: Event):
    ...


def cb_for_state(state, event: Event):
    ...


def test_on_event():
    consumer = EventProcessor()
    consumer.on_event(callback=cb_0, callback_args=["foo"])
    consumer.on_event(callback=cb_1, entity_type=EventEntityType.SCENARIO)
    consumer.on_event(callback=cb_2, entity_type=EventEntityType.SCENARIO, entity_id="bar")
    consumer.on_event(callback=cb_0, callback_args=["baz"], operation=EventOperation.CREATION)
    consumer.on_event(callback=cb_0, callback_args=["qux"], entity_type=EventEntityType.SEQUENCE,
                      operation=EventOperation.SUBMISSION)
    consumer.on_event(callback=cb_2, entity_type=EventEntityType.SCENARIO) # duplicate topic

    assert consumer._registration is not None
    registration = consumer._registration
    assert registration.registration_id is not None
    assert registration.queue is not None
    assert len(registration.topics) == 5  # 5 unique topics
    topic_1 = _Topic()
    topic_2 = _Topic(entity_type=EventEntityType.SCENARIO)
    topic_3 = _Topic(entity_type=EventEntityType.SCENARIO, entity_id="bar")
    topic_4 = _Topic(operation=EventOperation.CREATION)
    topic_5 = _Topic(entity_type=EventEntityType.SEQUENCE, operation=EventOperation.SUBMISSION)
    assert topic_1 in registration.topics
    assert topic_2 in registration.topics
    assert topic_3 in registration.topics
    assert topic_4 in registration.topics
    assert topic_5 in registration.topics

    assert consumer._gui is None

    assert len(consumer._topic_callbacks_map) == 5  # 5 unique topics
    assert topic_1 in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic_1] == [_Callback(cb_0, ["foo"])]
    assert topic_2 in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic_2] == [_Callback(cb_1), _Callback(cb_2)]
    assert topic_3 in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic_3] == [_Callback(cb_2)]
    assert topic_4 in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic_4] == [_Callback(cb_0, ["baz"])]
    assert topic_5 in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic_5] == [_Callback(cb_0, ["qux"])]


def test_on_event_for_state():
    consumer = EventProcessor(gui=Gui())
    consumer.broadcast_on_event(callback=cb_for_state)

    assert consumer._gui is not None
    assert len(consumer._topic_callbacks_map) == 1
    topic = _Topic()
    assert topic in consumer._topic_callbacks_map
    assert consumer._topic_callbacks_map[topic] == [_Callback(cb_for_state, broadcast=True)]


def test_on_event_missing_gui():
    consumer = EventProcessor()
    with pytest.raises(NoGuiDefinedInEventProcessor):
        consumer.broadcast_on_event(callback=cb_for_state)
    assert len(consumer._topic_callbacks_map) == 0
