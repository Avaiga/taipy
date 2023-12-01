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

from src.taipy.config.common.frequency import Frequency
from src.taipy.core.exceptions.exceptions import InvalidEventAttributeName, InvalidEventOperation
from src.taipy.core.notification.event import Event, EventEntityType, EventOperation


def test_event_creation_cycle():
    event_1 = Event(
        entity_type=EventEntityType.CYCLE,
        operation=EventOperation.CREATION,
        entity_id="cycle_id",
    )
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.CYCLE
    assert event_1.entity_id == "cycle_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.CYCLE,
        operation=EventOperation.UPDATE,
        entity_id="cycle_id",
        attribute_name="frequency",
        attribute_value=Frequency.DAILY,
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.CYCLE
    assert event_2.entity_id == "cycle_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "frequency"

    event_3 = Event(entity_type=EventEntityType.CYCLE, entity_id="cycle_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.CYCLE
    assert event_3.entity_id == "cycle_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.CYCLE,
            operation=EventOperation.CREATION,
            entity_id="cycle_id",
            attribute_name="frequency",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(EventEntityType.CYCLE, EventOperation.DELETION, entity_id="cycle_id", attribute_name="frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Event(
            entity_type=EventEntityType.CYCLE,
            operation=EventOperation.SUBMISSION,
            entity_id="cycle_id",
        )

    with pytest.raises(InvalidEventOperation):
        _ = Event(
            entity_type=EventEntityType.CYCLE,
            operation=EventOperation.SUBMISSION,
            entity_id="cycle_id",
            attribute_name="frequency",
        )


def test_event_creation_scenario():
    event_1 = Event(entity_type=EventEntityType.SCENARIO, entity_id="scenario_id", operation=EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.SCENARIO
    assert event_1.entity_id == "scenario_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.SCENARIO,
        entity_id="scenario_id",
        operation=EventOperation.UPDATE,
        attribute_name="is_primary",
        attribute_value=True,
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.SCENARIO
    assert event_2.entity_id == "scenario_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "is_primary"
    assert event_2.attribute_value is True

    event_3 = Event(entity_type=EventEntityType.SCENARIO, entity_id="scenario_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.SCENARIO
    assert event_3.entity_id == "scenario_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(entity_type=EventEntityType.SCENARIO, entity_id="scenario_id", operation=EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.SCENARIO
    assert event_4.entity_id == "scenario_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SCENARIO,
            entity_id="scenario_id",
            operation=EventOperation.CREATION,
            attribute_name="is_primary",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SCENARIO,
            entity_id="scenario_id",
            operation=EventOperation.DELETION,
            attribute_name="is_primary",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SCENARIO,
            entity_id="scenario_id",
            operation=EventOperation.SUBMISSION,
            attribute_name="is_primary",
        )


def test_event_creation_sequence():
    event_1 = Event(entity_type=EventEntityType.SEQUENCE, entity_id="sequence_id", operation=EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.SEQUENCE
    assert event_1.entity_id == "sequence_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.SEQUENCE,
        entity_id="sequence_id",
        operation=EventOperation.UPDATE,
        attribute_name="subscribers",
        attribute_value=object(),
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.SEQUENCE
    assert event_2.entity_id == "sequence_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "subscribers"

    event_3 = Event(entity_type=EventEntityType.SEQUENCE, entity_id="sequence_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.SEQUENCE
    assert event_3.entity_id == "sequence_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(entity_type=EventEntityType.SEQUENCE, entity_id="sequence_id", operation=EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.SEQUENCE
    assert event_4.entity_id == "sequence_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SEQUENCE,
            entity_id="sequence_id",
            operation=EventOperation.CREATION,
            attribute_name="subscribers",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SEQUENCE,
            entity_id="sequence_id",
            operation=EventOperation.DELETION,
            attribute_name="subscribers",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.SEQUENCE,
            entity_id="sequence_id",
            operation=EventOperation.SUBMISSION,
            attribute_name="subscribers",
        )


def test_event_creation_task():
    event_1 = Event(entity_type=EventEntityType.TASK, entity_id="task_id", operation=EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.TASK
    assert event_1.entity_id == "task_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.TASK,
        entity_id="task_id",
        operation=EventOperation.UPDATE,
        attribute_name="function",
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.TASK
    assert event_2.entity_id == "task_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "function"

    event_3 = Event(entity_type=EventEntityType.TASK, entity_id="task_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.TASK
    assert event_3.entity_id == "task_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    event_4 = Event(entity_type=EventEntityType.TASK, entity_id="task_id", operation=EventOperation.SUBMISSION)
    assert event_4.creation_date is not None
    assert event_4.entity_type == EventEntityType.TASK
    assert event_4.entity_id == "task_id"
    assert event_4.operation == EventOperation.SUBMISSION
    assert event_4.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.TASK,
            entity_id="task_id",
            operation=EventOperation.CREATION,
            attribute_name="function",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.TASK,
            entity_id="task_id",
            operation=EventOperation.DELETION,
            attribute_name="function",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.TASK,
            entity_id="task_id",
            operation=EventOperation.SUBMISSION,
            attribute_name="function",
        )


def test_event_creation_datanode():
    event_1 = Event(entity_type=EventEntityType.DATA_NODE, entity_id="dn_id", operation=EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.DATA_NODE
    assert event_1.entity_id == "dn_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.DATA_NODE,
        entity_id="dn_id",
        operation=EventOperation.UPDATE,
        attribute_name="properties",
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.DATA_NODE
    assert event_2.entity_id == "dn_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "properties"

    event_3 = Event(entity_type=EventEntityType.DATA_NODE, entity_id="dn_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.DATA_NODE
    assert event_3.entity_id == "dn_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.DATA_NODE,
            entity_id="dn_id",
            operation=EventOperation.CREATION,
            attribute_name="properties",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.DATA_NODE,
            entity_id="dn_id",
            operation=EventOperation.DELETION,
            attribute_name="properties",
        )

    with pytest.raises(InvalidEventOperation):
        _ = Event(entity_type=EventEntityType.DATA_NODE, entity_id="dn_id", operation=EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Event(
            entity_type=EventEntityType.DATA_NODE,
            entity_id="dn_id",
            operation=EventOperation.SUBMISSION,
            attribute_name="properties",
        )


def test_event_creation_job():
    event_1 = Event(entity_type=EventEntityType.JOB, entity_id="job_id", operation=EventOperation.CREATION)
    assert event_1.creation_date is not None
    assert event_1.entity_type == EventEntityType.JOB
    assert event_1.entity_id == "job_id"
    assert event_1.operation == EventOperation.CREATION
    assert event_1.attribute_name is None

    event_2 = Event(
        entity_type=EventEntityType.JOB, entity_id="job_id", operation=EventOperation.UPDATE, attribute_name="force"
    )
    assert event_2.creation_date is not None
    assert event_2.entity_type == EventEntityType.JOB
    assert event_2.entity_id == "job_id"
    assert event_2.operation == EventOperation.UPDATE
    assert event_2.attribute_name == "force"

    event_3 = Event(entity_type=EventEntityType.JOB, entity_id="job_id", operation=EventOperation.DELETION)
    assert event_3.creation_date is not None
    assert event_3.entity_type == EventEntityType.JOB
    assert event_3.entity_id == "job_id"
    assert event_3.operation == EventOperation.DELETION
    assert event_3.attribute_name is None

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.JOB,
            entity_id="job_id",
            operation=EventOperation.CREATION,
            attribute_name="force",
        )

    with pytest.raises(InvalidEventAttributeName):
        _ = Event(
            entity_type=EventEntityType.JOB,
            entity_id="job_id",
            operation=EventOperation.DELETION,
            attribute_name="force",
        )

    with pytest.raises(InvalidEventOperation):
        _ = Event(entity_type=EventEntityType.JOB, entity_id="job_id", operation=EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Event(
            entity_type=EventEntityType.JOB,
            entity_id="job_id",
            operation=EventOperation.SUBMISSION,
            attribute_name="force",
        )
