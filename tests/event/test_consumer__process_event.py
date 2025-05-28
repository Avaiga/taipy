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
from typing import Any, Dict, List, Optional
from unittest import mock

from taipy import Gui, Scenario
from taipy.core.notification import Event, EventEntityType, EventOperation, _Topic
from taipy.event._event_callback import _Callback
from taipy.event.event_processor import EventProcessor

collector: Dict[str, Any] = {"cb_0": 0, "cb_1": 0, "cb_2": 0, "cb_3": 0, "cb_for_state": 0,
            "cb_scenario_creation": 0, "cb_scenario_creation_with_state": 0}
args_collector: Dict[str, List] = {}


def init_collector():
    return {"cb_0": 0, "cb_1": 0, "cb_2": 0, "cb_3": 0, "cb_for_state": 0,
            "cb_scenario_creation": 0, "cb_scenario_creation_with_state": 0}, {}


def cb_0(event: Event, gui: Optional[Gui], extra:str):
    collector["cb_0"]+=1
    if not args_collector.get("cb_0"):
        args_collector["cb_0"] = [extra]
    else:
        args_collector["cb_0"].append(extra)
    print(f"event created at {event.creation_date} triggered callback cb_0.")  # noqa: T201


def cb_1(event: Event, gui: Optional[Gui]):
    collector["cb_1"]+=1
    print(f"event created at {event.creation_date} triggered callback cb_1.")  # noqa: T201


def cb_2(event: Event, gui: Gui,):
    collector["cb_2"]+=1
    print(f"event created at {event.creation_date} triggered callback cb_2.")  # noqa: T201


def cb_3(event: Event, gui: Gui, ):
    collector["cb_3"]+=1
    print(f"event created at {event.creation_date} triggered callback cb_3.")  # noqa: T201


def cb_for_state(state, event: Event):
    collector["cb_for_state"]+=1
    print(f"event created at {event.creation_date} triggered callback cb_for_state.")  # noqa: T201


def cb_scenario_creation(event: Event, scenario: Scenario, gui: Gui, extra_arg: str):
    collector["cb_scenario_creation"]+=1
    print(f"scenario {scenario.id} created at {event.creation_date} with {extra_arg}.")  # noqa: T201


def cb_scenario_creation_with_state(state, event: Event, scenario: Scenario, extra_arg: str):
    collector["cb_scenario_creation_with_state"]+=1
    print(f"scenario {scenario.id} created at {event.creation_date} with {extra_arg}.")  # noqa: T201



def test_process_event(scenario):
    global collector
    global args_collector
    consumer = EventProcessor()
    consumer.on_event(callback=cb_0, callback_args=["foo"])
    consumer.on_event(callback=cb_1, entity_type=EventEntityType.SCENARIO)
    consumer.on_event(callback=cb_2, entity_type=EventEntityType.SCENARIO, entity_id="bar")
    consumer.on_event(callback=cb_3, operation=EventOperation.CREATION)
    consumer.on_event(callback=cb_0, callback_args=["baz"], operation=EventOperation.CREATION)
    consumer.on_event(callback=cb_1, entity_type=EventEntityType.SEQUENCE, operation=EventOperation.SUBMISSION)
    consumer.on_event(callback=cb_1, entity_type=EventEntityType.JOB,
                      operation=EventOperation.UPDATE, attribute_name="status")

    collector, args_collector = init_collector()
    event_1 = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        entity_id="bar",
        attribute_name=None,
        attribute_value=None,
        metadata={},
    )
    consumer.process_event(event_1)

    assert collector["cb_0"] == 2
    assert collector["cb_1"] == 1
    assert collector["cb_2"] == 1
    assert collector["cb_3"] == 1

    collector, args_collector = init_collector()
    event_2 = Event(
        entity_type=EventEntityType.SEQUENCE,
        operation=EventOperation.SUBMISSION,
        entity_id="quux",
        attribute_name=None,
        attribute_value=None,
        metadata={},
    )
    consumer.process_event(event_2)

    assert collector["cb_0"] == 1
    assert collector["cb_1"] == 1
    assert collector["cb_2"] == 0
    assert collector["cb_3"] == 0
    collector, args_collector = init_collector()

    collector, args_collector = init_collector()
    event_3 = Event(
        entity_type=EventEntityType.JOB,
        operation=EventOperation.UPDATE,
        entity_id="corge",
        attribute_name="status",
        attribute_value="COMPLETED",
        metadata={},
    )
    consumer.process_event(event_3)

    assert collector["cb_0"] == 1
    assert collector["cb_1"] == 1
    assert collector["cb_2"] == 0
    assert collector["cb_3"] == 0
    collector, args_collector = init_collector()


def test_process_event_with_state():
    consumer = EventProcessor(gui=Gui())
    consumer.broadcast_on_event(callback=cb_for_state)

    event_1 = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        entity_id="foo",
        attribute_name=None,
        attribute_value=None,
        metadata={},
    )
    with mock.patch("taipy.Gui.broadcast_callback") as mock_broadcast:
        consumer.process_event(event_1)
        mock_broadcast.assert_called_once_with(cb_for_state, [event_1])


def test_process_event_with_filter():
    global collector
    global args_collector
    def filt(event: Event) -> bool:
        return event.metadata.get("foo") == "bar"

    consumer = EventProcessor()
    consumer.on_event(callback=cb_0,
                      callback_args=["foo"],
                      entity_type=EventEntityType.SCENARIO,
                      operation=EventOperation.CREATION,
                      filter=filt)

    topic = _Topic(entity_type=EventEntityType.SCENARIO, operation=EventOperation.CREATION)
    assert len(consumer._topic_callbacks_map) == 1
    assert consumer._topic_callbacks_map[topic] == [_Callback(cb_0, ["foo"], False, filt)]

    collector, args_collector = init_collector()
    event_matching_filter = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        metadata={"foo": "bar"},
    )
    consumer.process_event(event_matching_filter)

    assert collector["cb_0"] == 1

    collector, args_collector = init_collector()
    event_not_matching_filter = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        metadata={"baz": "qux"},
    )
    consumer.process_event(event_not_matching_filter)

    assert collector["cb_0"] == 0
    collector, args_collector = init_collector()


def test_process_event_with_predefined_args(scenario):
    global collector
    global args_collector
    consumer = EventProcessor()
    consumer.on_event(callback=cb_scenario_creation, callback_args=["foo"])
    collector, args_collector = init_collector()
    event = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        entity_id="foo",
        attribute_name=None,
        attribute_value=None,
        metadata={"predefined_args": [scenario]},
    )
    consumer.process_event(event)

    assert collector["cb_scenario_creation"] == 1
    collector, args_collector = init_collector()


def test_process_event_with_predefined_args_and_state(scenario):
    consumer = EventProcessor(Gui())
    consumer.broadcast_on_event(callback=cb_scenario_creation_with_state, callback_args=["foo"])
    event = Event(
        entity_type=EventEntityType.SCENARIO,
        operation=EventOperation.CREATION,
        entity_id="foo",
        attribute_name=None,
        attribute_value=None,
        metadata={"predefined_args": [scenario]},
    )

    with mock.patch("taipy.Gui.broadcast_callback") as mock_broadcast:
        consumer.process_event(event)
        mock_broadcast.assert_called_once_with(cb_scenario_creation_with_state, [event, scenario, "foo"])
