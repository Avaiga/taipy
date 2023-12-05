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

from taipy.core.notification import EventEntityType, EventOperation
from taipy.core.notification._registration import _Registration
from taipy.core.notification._topic import _Topic


def test_create_registration():
    registration_0 = _Registration()
    assert isinstance(registration_0.registration_id, str)
    assert registration_0.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_0.queue, SimpleQueue)
    assert registration_0.queue.qsize() == 0
    assert isinstance(registration_0.topic, _Topic)
    assert registration_0.topic.entity_type is None
    assert registration_0.topic.entity_id is None
    assert registration_0.topic.operation is None
    assert registration_0.topic.attribute_name is None

    registration_1 = _Registration(
        entity_type=EventEntityType.SCENARIO, entity_id="SCENARIO_scenario_id", operation=EventOperation.CREATION
    )
    assert isinstance(registration_1.registration_id, str)
    assert registration_1.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_1.queue, SimpleQueue)
    assert registration_1.queue.qsize() == 0
    assert isinstance(registration_1.topic, _Topic)
    assert registration_1.topic.entity_type == EventEntityType.SCENARIO
    assert registration_1.topic.entity_id == "SCENARIO_scenario_id"
    assert registration_1.topic.operation == EventOperation.CREATION
    assert registration_1.topic.attribute_name is None

    registration_2 = _Registration(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="SEQUENCE_scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="tasks",
    )
    assert isinstance(registration_2.registration_id, str)
    assert registration_2.registration_id.startswith(_Registration._ID_PREFIX)
    assert isinstance(registration_2.queue, SimpleQueue)
    assert registration_2.queue.qsize() == 0
    assert isinstance(registration_2.topic, _Topic)
    assert registration_2.topic.entity_type == EventEntityType.SEQUENCE
    assert registration_2.topic.entity_id == "SEQUENCE_scenario_id"
    assert registration_2.topic.operation == EventOperation.UPDATE
    assert registration_2.topic.attribute_name == "tasks"
