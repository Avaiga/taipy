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


from queue import SimpleQueue

from taipy.core.notification import EventEntityType, EventOperation
from taipy.core.notification._registration import _Registration
from taipy.core.notification._topic import _Topic


def test_create_registration():
    registration = _Registration()
    assert isinstance(registration.registration_id, str)
    assert registration.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration.queue, SimpleQueue)
    assert registration.queue.qsize() == 0
    assert len(registration.topics) == 0

def test_create_registration_from_topic():
    registration_0 = _Registration.from_topic()
    assert isinstance(registration_0.registration_id, str)
    assert registration_0.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_0.queue, SimpleQueue)
    assert registration_0.queue.qsize() == 0
    assert len(registration_0.topics) == 1
    topic_0 = registration_0.topics.pop()
    assert isinstance(topic_0, _Topic)
    assert topic_0.entity_type is None
    assert topic_0.entity_id is None
    assert topic_0.operation is None
    assert topic_0.attribute_name is None

    registration_1 = _Registration.from_topic(
        entity_type=EventEntityType.SCENARIO,
        entity_id="SCENARIO_scenario_id",
        operation=EventOperation.CREATION
    )
    assert isinstance(registration_1.registration_id, str)
    assert registration_1.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_1.queue, SimpleQueue)
    assert registration_1.queue.qsize() == 0
    assert len(registration_1.topics) == 1
    topic_1 = registration_1.topics.pop()
    assert isinstance(topic_1, _Topic)
    assert topic_1.entity_type == EventEntityType.SCENARIO
    assert topic_1.entity_id == "SCENARIO_scenario_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    registration_2 = _Registration.from_topic(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="SEQUENCE_scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="tasks",
    )
    assert isinstance(registration_2.registration_id, str)
    assert registration_2.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_2.queue, SimpleQueue)
    assert registration_2.queue.qsize() == 0
    topic_2 = registration_2.topics.pop()
    assert isinstance(topic_2, _Topic)
    assert topic_2.entity_type == EventEntityType.SEQUENCE
    assert topic_2.entity_id == "SEQUENCE_scenario_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "tasks"

def test_eq():
    registration = _Registration.from_topic(operation=EventOperation.DELETION)
    other_registration = _Registration()
    other_registration.registration_id = registration.registration_id
    assert registration == other_registration

def test_ne():
    registration = _Registration.from_topic(operation=EventOperation.DELETION)
    other_registration = _Registration()
    assert registration != other_registration

def test_add_topic():
    registration = _Registration()
    assert len(registration.topics) == 0
    registration.add_topic()
    assert len(registration.topics) == 1
    topic = registration.topics.pop()
    assert isinstance(topic, _Topic)
    assert topic.entity_type is None
    assert topic.entity_id is None
    assert topic.operation is None
    assert topic.attribute_name is None

    registration.add_topic(
        entity_type=EventEntityType.SCENARIO,
        entity_id="SCENARIO_scenario_id",
        operation=EventOperation.CREATION
    )
    assert len(registration.topics) == 1
    topic = registration.topics.pop()
    assert isinstance(topic, _Topic)
    assert topic.entity_type == EventEntityType.SCENARIO
    assert topic.entity_id == "SCENARIO_scenario_id"
    assert topic.operation == EventOperation.CREATION
    assert topic.attribute_name is None

    registration.add_topic(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="SEQUENCE_scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="tasks",
    )
    assert len(registration.topics) == 1
    topic = registration.topics.pop()
    assert isinstance(topic, _Topic)
    assert topic.entity_type == EventEntityType.SEQUENCE
    assert topic.entity_id == "SEQUENCE_scenario_id"
    assert topic.operation == EventOperation.UPDATE
    assert topic.attribute_name == "tasks"

def test_add_remove_topic():
    registration = _Registration()
    registration.add_topic()
    topic_0 = _Topic()
    registration.add_topic(
        entity_type=EventEntityType.SCENARIO,
        entity_id="SCENARIO_scenario_id",
        operation=EventOperation.CREATION
    )
    topic_1 = _Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.CREATION)
    registration.add_topic(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="SEQUENCE_scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="tasks",
    )
    topic_2 = _Topic(EventEntityType.SEQUENCE, "SEQUENCE_scenario_id", EventOperation.UPDATE, "tasks")
    assert len(registration.topics) == 3
    assert topic_0 in registration.topics
    assert topic_1 in registration.topics
    assert topic_2 in registration.topics

    registration.remove_topic(
        entity_type=EventEntityType.SCENARIO,
        entity_id="SCENARIO_scenario_id",
        operation=EventOperation.CREATION
    )
    assert len(registration.topics) == 2
    assert topic_0 in registration.topics
    assert topic_2 in registration.topics

    registration.remove_topic(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="SEQUENCE_scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="tasks",
    )
    assert len(registration.topics) == 1
    assert topic_0 in registration.topics

    registration.remove_topic()
    assert len(registration.topics) == 0
