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
    topic_1 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.CYCLE
    assert topic_1.entity_id == "CYCLE_cycle_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "UPDATE", "frequency")
    assert topic_2.entity_type == EventEntityType.CYCLE
    assert topic_2.entity_id == "CYCLE_cycle_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "frequency"

    topic_3 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.CYCLE
    assert topic_3.entity_id == "CYCLE_cycle_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "CYCLE_cycle_id", "DELETION")
    assert topic_4.entity_type == EventEntityType.CYCLE
    assert topic_4.entity_id == "CYCLE_cycle_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    topic_5 = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "creation")
    assert topic_5.entity_type == EventEntityType.CYCLE
    assert topic_5.entity_id == "CYCLE_cycle_id"
    assert topic_5.operation == EventOperation.CREATION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.CYCLE, "cycle_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "CYCLE_cycle_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "CREATION", "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "DELETION", "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", attribute_name="frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "CYCLE_cycle_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "CYCLE_cycle_id", "UPDATE_1", "attribute")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.CYCLE, "CYCLE_cycle_id", "SUBMISSION", "frequency")


def test_topic_creation_scenario():
    topic_1 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.SCENARIO
    assert topic_1.entity_id == "SCENARIO_scenario_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "UPDATE", "is_primary")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "SCENARIO_scenario_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "is_primary"

    topic_3 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.SCENARIO
    assert topic_3.entity_id == "SCENARIO_scenario_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.SCENARIO
    assert topic_4.entity_id == "SCENARIO_scenario_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "SCENARIO_scenario_id", "DELETION")
    assert topic_5.entity_type == EventEntityType.SCENARIO
    assert topic_5.entity_id == "SCENARIO_scenario_id"
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    topic_6 = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "update", "properties")
    assert topic_6.entity_type == EventEntityType.SCENARIO
    assert topic_6.entity_id == "SCENARIO_scenario_id"
    assert topic_6.operation == EventOperation.UPDATE
    assert topic_6.attribute_name == "properties"

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.SCENARIO, "scenario_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "SCENARIO_scenario_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "CREATION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "DELETION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "SUBMISSION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", attribute_name="is_primary")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.SCENARIO, "SCENARIO_scenario_id", "POPUlATE")


def test_topic_creation_pipeline():
    topic_1 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.PIPELINE
    assert topic_1.entity_id == "PIPELINE_pipeline_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "UPDATE", "subscribers")
    assert topic_2.entity_type == EventEntityType.PIPELINE
    assert topic_2.entity_id == "PIPELINE_pipeline_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "subscribers"

    topic_3 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.PIPELINE
    assert topic_3.entity_id == "PIPELINE_pipeline_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.PIPELINE
    assert topic_4.entity_id == "PIPELINE_pipeline_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "PIPELINE_pipeline_id", "SUBMISSION")
    assert topic_5.entity_type == EventEntityType.PIPELINE
    assert topic_5.entity_id == "PIPELINE_pipeline_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    topic_6 = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "deletion")
    assert topic_6.entity_type == EventEntityType.PIPELINE
    assert topic_6.entity_id == "PIPELINE_pipeline_id"
    assert topic_6.operation == EventOperation.DELETION
    assert topic_6.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.PIPELINE, "pipeline_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "PIPELINE_pipeline_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "CREATION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "DELETION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "SUBMISSION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", attribute_name="subscribers")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.PIPELINE, "PIPELINE_pipeline_id", "HI")


def test_topic_creation_task():
    topic_1 = Topic(EventEntityType.TASK, "TASK_task_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.TASK
    assert topic_1.entity_id == "TASK_task_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.TASK, "TASK_task_id", "UPDATE", "function")
    assert topic_2.entity_type == EventEntityType.TASK
    assert topic_2.entity_id == "TASK_task_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "function"

    topic_3 = Topic(EventEntityType.TASK, "TASK_task_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.TASK
    assert topic_3.entity_id == "TASK_task_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(EventEntityType.TASK, "TASK_task_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.TASK
    assert topic_4.entity_id == "TASK_task_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "TASK_task_id", "SUBMISSION")
    assert topic_5.entity_type == EventEntityType.TASK
    assert topic_5.entity_id == "TASK_task_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    topic_6 = Topic(EventEntityType.TASK, "TASK_task_id", "submission")
    assert topic_6.entity_type == EventEntityType.TASK
    assert topic_6.entity_id == "TASK_task_id"
    assert topic_6.operation == EventOperation.SUBMISSION
    assert topic_6.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.TASK, "task_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.CYCLE, "TASK_task_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", "CREATION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", "DELETION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", "SUBMISSION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", attribute_name="function")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.TASK, "TASK_task_id", "hello", "function")


def test_topic_creation_datanode():
    topic_1 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.DATA_NODE
    assert topic_1.entity_id == "DATANODE_dn_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "UPDATE", "properties")
    assert topic_2.entity_type == EventEntityType.DATA_NODE
    assert topic_2.entity_id == "DATANODE_dn_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "properties"

    topic_3 = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.DATA_NODE
    assert topic_3.entity_id == "DATANODE_dn_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "DATANODE_dn_id", "DELETION")
    assert topic_4.entity_type == EventEntityType.DATA_NODE
    assert topic_4.entity_id == "DATANODE_dn_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "DATANODE_dn_id", "update", "scope")
    assert topic_5.entity_type == EventEntityType.DATA_NODE
    assert topic_5.entity_id == "DATANODE_dn_id"
    assert topic_5.operation == EventOperation.UPDATE
    assert topic_5.attribute_name == "scope"

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.DATA_NODE, "dn_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "DATANODE_dn_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "CREATION", "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "DELETION", "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", attribute_name="properties")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "DATANODE_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "DATANODE_job_id", "hello")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.DATA_NODE, "DATANODE_dn_id", "SUBMISSION", "properties")


def test_topic_creation_job():
    topic_1 = Topic(EventEntityType.JOB, "JOB_job_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.JOB
    assert topic_1.entity_id == "JOB_job_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic(EventEntityType.JOB, "JOB_job_id", "UPDATE", "force")
    assert topic_2.entity_type == EventEntityType.JOB
    assert topic_2.entity_id == "JOB_job_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "force"

    topic_3 = Topic(EventEntityType.JOB, "JOB_job_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.JOB
    assert topic_3.entity_id == "JOB_job_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "JOB_job_id", "DELETION")
    assert topic_4.entity_type == EventEntityType.JOB
    assert topic_4.entity_id == "JOB_job_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    topic_5 = Topic(EventEntityType.JOB, "JOB_job_id", "creation")
    assert topic_5.entity_type == EventEntityType.JOB
    assert topic_5.entity_id == "JOB_job_id"
    assert topic_5.operation == EventOperation.CREATION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic(EventEntityType.JOB, "job_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic(EventEntityType.SCENARIO, "JOB_job_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", "CREATION", "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", "DELETION", "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", attribute_name="force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "JOB_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", "SUBMISSION", "force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(EventEntityType.JOB, "JOB_job_id", "hello", "force")
