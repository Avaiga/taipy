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

import pytest

from src.taipy.core.exceptions.exceptions import InvalidEventAttributeName, InvalidEventOperation
from src.taipy.core.notification.event import Event, EventEntityType, EventOperation


def test_event_creation_cycle():
    event_1 = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.CYCLE
    assert event_1.entity_id == "cycle_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.UPDATE, "frequency")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.CYCLE
    assert event_2.entity_id == "cycle_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "frequency"

    event_3 = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.CYCLE
    assert event_3.entity_id == "cycle_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION, "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.DELETION, "frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.CYCLE, "cycle_id", EventOperation.SUBMISSION, "frequency")


def test_event_creation_scenario():
    event_1 = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.SCENARIO
    assert event_1.entity_id == "scenario_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.UPDATE, "is_primary")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.SCENARIO
    assert event_2.entity_id == "scenario_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "is_primary"

    event_3 = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.SCENARIO
    assert event_3.entity_id == "scenario_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.SCENARIO
    assert event_4.entity_id == "scenario_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.CREATION, "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.DELETION, "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION, "is_primary")


def test_event_creation_sequence():
    event_1 = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.SEQUENCE
    assert event_1.entity_id == "sequence_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "subscribers")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.SEQUENCE
    assert event_2.entity_id == "sequence_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "subscribers"

    event_3 = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.SEQUENCE
    assert event_3.entity_id == "sequence_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.SEQUENCE
    assert event_4.entity_id == "sequence_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.CREATION, "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.DELETION, "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.SUBMISSION, "subscribers")


def test_event_creation_task():
    event_1 = Event(EventEntityType.TASK, "task_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.TASK
    assert event_1.entity_id == "task_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.TASK, "task_id", EventOperation.UPDATE, "function")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.TASK
    assert event_2.entity_id == "task_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "function"

    event_3 = Event(EventEntityType.TASK, "task_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.TASK
    assert event_3.entity_id == "task_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(EventEntityType.TASK, "task_id", EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.TASK
    assert event_4.entity_id == "task_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.TASK, "task_id", EventOperation.CREATION, "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.TASK, "task_id", EventOperation.DELETION, "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.TASK, "task_id", EventOperation.SUBMISSION, "function")


def test_event_creation_datanode():
    event_1 = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.DATA_NODE
    assert event_1.entity_id == "dn_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.UPDATE, "properties")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.DATA_NODE
    assert event_2.entity_id == "dn_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "properties"

    event_3 = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.DATA_NODE
    assert event_3.entity_id == "dn_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION, "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.DELETION, "properties")

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.SUBMISSION, "properties")


def test_event_creation_job():
    event_1 = Event(EventEntityType.JOB, "job_id", EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.JOB
    assert event_1.entity_id == "job_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(EventEntityType.JOB, "job_id", EventOperation.UPDATE, "force")
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.JOB
    assert event_2.entity_id == "job_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "force"

    event_3 = Event(EventEntityType.JOB, "job_id", EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.JOB
    assert event_3.entity_id == "job_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.JOB, "job_id", EventOperation.CREATION, "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.JOB, "job_id", EventOperation.DELETION, "force")

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.JOB, "job_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Event(EventEntityType.JOB, "job_id", EventOperation.SUBMISSION, "force")
