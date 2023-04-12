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

from src.taipy.core.notification import Registration, Topic
from src.taipy.core.notification.event import EventEntityType, EventOperation


def test_create_registration():
    registration_0 = Registration()
    assert isinstance(registration_0.register_id, str)
    assert registration_0.register_id.startswith(Registration._ID_PREFIX)
    assert isinstance(registration_0.queue, SimpleQueue)
    assert registration_0.queue.qsize() == 0
    assert isinstance(registration_0.topic, Topic)
    assert registration_0.topic.entity_type is None
    assert registration_0.topic.entity_id is None
    assert registration_0.topic.operation is None
    assert registration_0.topic.attribute_name is None

    registration_1 = Registration(entity_type="SCENARIO", entity_id="SCENARIO_scenario_id", operation="creation")
    assert isinstance(registration_1.register_id, str)
    assert registration_1.register_id.startswith(Registration._ID_PREFIX)
    assert isinstance(registration_1.queue, SimpleQueue)
    assert registration_1.queue.qsize() == 0
    assert isinstance(registration_1.topic, Topic)
    assert registration_1.topic.entity_type == EventEntityType.SCENARIO
    assert registration_1.topic.entity_id == "SCENARIO_scenario_id"
    assert registration_1.topic.operation == EventOperation.CREATION
    assert registration_1.topic.attribute_name is None

    registration_2 = Registration(
        entity_type="PIPELINE", entity_id="PIPELINE_scenario_id", operation="update", attribute_name="tasks"
    )
    assert isinstance(registration_2.register_id, str)
    assert registration_2.register_id.startswith(Registration._ID_PREFIX)
    assert isinstance(registration_2.queue, SimpleQueue)
    assert registration_2.queue.qsize() == 0
    assert isinstance(registration_2.topic, Topic)
    assert registration_2.topic.entity_type == EventEntityType.PIPELINE
    assert registration_2.topic.entity_id == "PIPELINE_scenario_id"
    assert registration_2.topic.operation == EventOperation.UPDATE
    assert registration_2.topic.attribute_name == "tasks"
