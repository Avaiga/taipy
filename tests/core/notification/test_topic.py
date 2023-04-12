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

from src.taipy.core.exceptions.exceptions import (
    InvalidEntityId,
    InvalidEntityType,
    InvalidEventAttributeName,
    InvalidEventOperation,
)
from src.taipy.core.notification.event import EventEntityType, EventOperation
from src.taipy.core.notification.topic import Topic


def test_topic_creation_cycle():
    topic_1 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.CYCLE
    assert topic_1.entity_id == "CYCLE_cycle_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.UPDATE, "frequency")
    assert topic_2.entity_type == EventEntityType.CYCLE
    assert topic_2.entity_id == "CYCLE_cycle_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "frequency"

    topic_3 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.CYCLE
    assert topic_3.entity_id == "CYCLE_cycle_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "CYCLE_cycle_id", EventOperation.DELETION)
    assert topic_4.entity_type == EventEntityType.CYCLE
    assert topic_4.entity_id == "CYCLE_cycle_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "CYCLE_cycle_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.CREATION, "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.DELETION, "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", attribute_name="frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "CYCLE_cycle_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", EventOperation.SUBMISSION, "frequency")


def test_topic_creation_scenario():
    topic_1 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.SCENARIO
    assert topic_1.entity_id == "SCENARIO_scenario_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.UPDATE, "is_primary")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "SCENARIO_scenario_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "is_primary"

    topic_3 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.SCENARIO
    assert topic_3.entity_id == "SCENARIO_scenario_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.SCENARIO
    assert topic_4.entity_id == "SCENARIO_scenario_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "SCENARIO_scenario_id", EventOperation.DELETION)
    assert topic_5.entity_type == EventEntityType.SCENARIO
    assert topic_5.entity_id == "SCENARIO_scenario_id"
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "SCENARIO_scenario_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.CREATION, "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.DELETION, "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", EventOperation.SUBMISSION, "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", attribute_name="is_primary")


def test_topic_creation_pipeline():
    topic_1 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.PIPELINE
    assert topic_1.entity_id == "PIPELINE_pipeline_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.UPDATE, "subscribers")
    assert topic_2.entity_type == EventEntityType.PIPELINE
    assert topic_2.entity_id == "PIPELINE_pipeline_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "subscribers"

    topic_3 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.PIPELINE
    assert topic_3.entity_id == "PIPELINE_pipeline_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.PIPELINE
    assert topic_4.entity_id == "PIPELINE_pipeline_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "PIPELINE_pipeline_id", EventOperation.SUBMISSION)
    assert topic_5.entity_type == EventEntityType.PIPELINE
    assert topic_5.entity_id == "PIPELINE_pipeline_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "PIPELINE_pipeline_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.CREATION, "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.DELETION, "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", EventOperation.SUBMISSION, "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", attribute_name="subscribers")


def test_topic_creation_task():
    topic_1 = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.TASK
    assert topic_1.entity_id == "TASK_task_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.UPDATE, "function")
    assert topic_2.entity_type == EventEntityType.TASK
    assert topic_2.entity_id == "TASK_task_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "function"

    topic_3 = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.TASK
    assert topic_3.entity_id == "TASK_task_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.SUBMISSION)
    assert topic_4.entity_type == EventEntityType.TASK
    assert topic_4.entity_id == "TASK_task_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "TASK_task_id", EventOperation.SUBMISSION)
    assert topic_5.entity_type == EventEntityType.TASK
    assert topic_5.entity_id == "TASK_task_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.TASK, "task_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "TASK_task_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.CREATION, "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.DELETION, "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", EventOperation.SUBMISSION, "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", attribute_name="function")


def test_topic_creation_datanode():
    topic_1 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.DATA_NODE
    assert topic_1.entity_id == "DATANODE_dn_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.UPDATE, "properties")
    assert topic_2.entity_type == EventEntityType.DATA_NODE
    assert topic_2.entity_id == "DATANODE_dn_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "properties"

    topic_3 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.DATA_NODE
    assert topic_3.entity_id == "DATANODE_dn_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "DATANODE_dn_id", EventOperation.DELETION)
    assert topic_4.entity_type == EventEntityType.DATA_NODE
    assert topic_4.entity_id == "DATANODE_dn_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "DATANODE_dn_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.CREATION, "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.DELETION, "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", attribute_name="properties")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "DATANODE_job_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", EventOperation.SUBMISSION, "properties")


def test_topic_creation_job():
    topic_1 = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.CREATION)
    assert topic_1.entity_type == EventEntityType.JOB
    assert topic_1.entity_id == "JOB_job_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.UPDATE, "force")
    assert topic_2.entity_type == EventEntityType.JOB
    assert topic_2.entity_id == "JOB_job_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "force"

    topic_3 = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.DELETION)
    assert topic_3.entity_type == EventEntityType.JOB
    assert topic_3.entity_id == "JOB_job_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "JOB_job_id", EventOperation.DELETION)
    assert topic_4.entity_type == EventEntityType.JOB
    assert topic_4.entity_id == "JOB_job_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.JOB, "job_id", EventOperation.CREATION)

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "JOB_job_id", EventOperation.CREATION)

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.CREATION, "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.DELETION, "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", attribute_name="force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "JOB_job_id", EventOperation.SUBMISSION)

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", EventOperation.SUBMISSION, "force")
