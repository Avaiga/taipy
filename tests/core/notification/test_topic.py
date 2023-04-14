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
from src.taipy.core.notification.event import EventEntityType, EventOperation
from src.taipy.core.notification.topic import Topic


def test_general_topic_creation():
    topic_1 = Topic(None, None, None, None)
    assert topic_1.entity_type is None
    assert topic_1.entity_id is None
    assert topic_1.operation is None
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.SCENARIO, "scenario_id")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "scenario_id"
    assert topic_2.operation is None
    assert topic_2.attribute_name is None

    topic_3 = Topic(None, None, EventOperation.CREATION)
    assert topic_3.entity_type is None
    assert topic_3.entity_id is None
    assert topic_3.operation == EventOperation.CREATION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, None, EventOperation.UPDATE, "properties")
    assert topic_4.entity_type is None
    assert topic_4.entity_id is None
    assert topic_4.operation == EventOperation.UPDATE
    assert topic_4.attribute_name == "properties"

    topic_5 = Topic(entity_type=EventEntityType.JOB, operation=EventOperation.DELETION)
    assert topic_5.entity_type == EventEntityType.JOB
    assert topic_5.entity_id is None
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    topic_6 = Topic(entity_type=EventEntityType.PIPELINE)
    assert topic_6.entity_type == EventEntityType.PIPELINE
    assert topic_6.entity_id is None
    assert topic_6.operation is None
    assert topic_6.attribute_name is None


def test_topic_creation_cycle():
    topic_1 = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.CYCLE
    assert topic_1.entity_id == "cycle_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.UPDATE, "frequency")
    assert topic_2.entity_type == EventEntityType.CYCLE
    assert topic_2.entity_id == "cycle_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "frequency"

    topic_3 = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.CYCLE
    assert topic_3.entity_id == "cycle_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION)
    assert topic_4.entity_type == EventEntityType.CYCLE
    assert topic_4.entity_id == "cycle_id"
    assert topic_4.operation == EventOperation.CREATION
    assert topic_4.attribute_name is None

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION, "frequency")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.DELETION, "frequency")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.CYCLE, "cycle_id", attribute_name="frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.SUBMISSION, "frequency")


def test_topic_creation_scenario():
    topic_1 = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.SCENARIO
    assert topic_1.entity_id == "scenario_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.UPDATE, "is_primary")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "scenario_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "is_primary"

    topic_3 = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.SCENARIO
    assert topic_3.entity_id == "scenario_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.SCENARIO
    assert topic_4.entity_id == "scenario_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.UPDATE, "properties")
    assert topic_5.entity_type == EventEntityType.SCENARIO
    assert topic_5.entity_id == "scenario_id"
    assert topic_5.operation == EventOperation.UPDATE
    assert topic_5.attribute_name == "properties"

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.CREATION, "is_primary")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.DELETION, "is_primary")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION, "is_primary")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.SCENARIO, "scenario_id", attribute_name="is_primary")


def test_topic_creation_pipeline():
    topic_1 = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.PIPELINE
    assert topic_1.entity_id == "pipeline_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "subscribers")
    assert topic_2.entity_type == EventEntityType.PIPELINE
    assert topic_2.entity_id == "pipeline_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "subscribers"

    topic_3 = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.PIPELINE
    assert topic_3.entity_id == "pipeline_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.PIPELINE
    assert topic_4.entity_id == "pipeline_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.DELETION)
    assert topic_5.entity_type == EventEntityType.PIPELINE
    assert topic_5.entity_id == "pipeline_id"
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.CREATION, "subscribers")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.DELETION, "subscribers")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.SUBMISSION, "subscribers")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.PIPELINE, "pipeline_id", attribute_name="subscribers")


def test_topic_creation_task():
    topic_1 = Topic(EventEntityType.TASK, "task_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.TASK
    assert topic_1.entity_id == "task_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.TASK, "task_id", EventOperation.UPDATE, "function")
    assert topic_2.entity_type == EventEntityType.TASK
    assert topic_2.entity_id == "task_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "function"

    topic_3 = Topic(EventEntityType.TASK, "task_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.TASK
    assert topic_3.entity_id == "task_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.TASK, "task_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.TASK
    assert topic_4.entity_id == "task_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(EventEntityType.TASK, "task_id", EventOperation.SUBMISSION)
    assert topic_5.entity_type == EventEntityType.TASK
    assert topic_5.entity_id == "task_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.TASK, "task_id", EventOperation.CREATION, "function")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.TASK, "task_id", EventOperation.DELETION, "function")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.TASK, "task_id", EventOperation.SUBMISSION, "function")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.TASK, "task_id", attribute_name="function")


def test_topic_creation_datanode():
    topic_1 = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.DATA_NODE
    assert topic_1.entity_id == "dn_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.UPDATE, "properties")
    assert topic_2.entity_type == EventEntityType.DATA_NODE
    assert topic_2.entity_id == "dn_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "properties"

    topic_3 = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.DATA_NODE
    assert topic_3.entity_id == "dn_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "dn_id", EventOperation.UPDATE, "scope")
    assert topic_4.entity_type is None
    assert topic_4.entity_id == "dn_id"
    assert topic_4.operation == EventOperation.UPDATE
    assert topic_4.attribute_name == "scope"

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION, "properties")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.DELETION, "properties")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.DATA_NODE, "dn_id", attribute_name="properties")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.SUBMISSION)

    # with pytest.raises(InvalidEventOperation):
    #     _ = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.SUBMISSION, "properties")


def test_topic_creation_job():
    topic_1 = Topic(EventEntityType.JOB, "job_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.JOB
    assert topic_1.entity_id == "job_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.JOB, "job_id", EventOperation.UPDATE, "force")
    assert topic_2.entity_type == EventEntityType.JOB
    assert topic_2.entity_id == "job_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "force"

    topic_3 = Topic(EventEntityType.JOB, "job_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.JOB
    assert topic_3.entity_id == "job_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.JOB, "job_id", EventOperation.CREATION)
    assert topic_4.entity_type == EventEntityType.JOB
    assert topic_4.entity_id == "job_id"
    assert topic_4.operation == EventOperation.CREATION
    assert topic_4.attribute_name is None

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.JOB, "job_id", EventOperation.CREATION, "force")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.JOB, "job_id", EventOperation.DELETION, "force")

    # with pytest.raises(InvalidEventAttributeName):
    #     _ = Topic(EventEntityType.JOB, "job_id", attribute_name="force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "job_id", EventOperation.SUBMISSION)

    # with pytest.raises(InvalidEventOperation):
    #     _ = Topic(EventEntityType.JOB, "job_id", EventOperation.SUBMISSION, "force")


def test_topic_equal():
    assert Topic() == Topic()
    assert Topic(EventEntityType.SCENARIO) == Topic(EventEntityType.SCENARIO)
    assert Topic(entity_id="pipeline_id") == Topic(entity_id="pipeline_id")
    assert Topic(operation=EventOperation.SUBMISSION) == Topic(operation=EventOperation.SUBMISSION)
    assert Topic(EventEntityType.JOB, "JOB_id", EventOperation.UPDATE, "status") == Topic(
        EventEntityType.JOB, "JOB_id", EventOperation.UPDATE, "status"
    )
