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


def test_general_topic_creation():
    topic_1 = Topic(None, None, None, None)
    assert topic_1.entity_type is None
    assert topic_1.entity_id is None
    assert topic_1.operation is None
    assert topic_1.attribute_name is None

    topic_2 = Topic("SCENARIO", "SCENARIO_scenario_id")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "SCENARIO_scenario_id"
    assert topic_2.operation is None
    assert topic_2.attribute_name is None

    topic_3 = Topic(None, None, "creation")
    assert topic_3.entity_type is None
    assert topic_3.entity_id is None
    assert topic_3.operation == EventOperation.CREATION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, None, "update", "properties")
    assert topic_4.entity_type is None
    assert topic_4.entity_id is None
    assert topic_4.operation == EventOperation.UPDATE
    assert topic_4.attribute_name == "properties"

    topic_5 = Topic(entity_type="job", operation="deletion")
    assert topic_5.entity_type == EventEntityType.JOB
    assert topic_5.entity_id is None
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    topic_6 = Topic(entity_type="pipeline")
    assert topic_6.entity_type == EventEntityType.PIPELINE
    assert topic_6.entity_id is None
    assert topic_6.operation is None
    assert topic_6.attribute_name is None


def test_topic_creation_cycle():
    topic_1 = Topic("CYCLE", "CYCLE_cycle_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.CYCLE
    assert topic_1.entity_id == "CYCLE_cycle_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("CYCLE", "CYCLE_cycle_id", "UPDATE", "frequency")
    assert topic_2.entity_type == EventEntityType.CYCLE
    assert topic_2.entity_id == "CYCLE_cycle_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "frequency"

    topic_3 = Topic("CYCLE", "CYCLE_cycle_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.CYCLE
    assert topic_3.entity_id == "CYCLE_cycle_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "CYCLE_cycle_id", "DELETION")
    assert topic_4.entity_type == EventEntityType.CYCLE
    assert topic_4.entity_id == "CYCLE_cycle_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    topic_5 = Topic("CYCLE", "CYCLE_cycle_id", "creation")
    assert topic_5.entity_type == EventEntityType.CYCLE
    assert topic_5.entity_id == "CYCLE_cycle_id"
    assert topic_5.operation == EventOperation.CREATION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic("CYCLE", "cycle_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("SCENARIO", "CYCLE_cycle_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("CYCLE", "CYCLE_cycle_id", "CREATION", "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("CYCLE", "CYCLE_cycle_id", "DELETION", "frequency")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("CYCLE", "CYCLE_cycle_id", attribute_name="frequency")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("CYCLE", "CYCLE_cycle_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "CYCLE_cycle_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "CYCLE_cycle_id", "UPDATE_1", "attribute")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("CYCLE", "CYCLE_cycle_id", "SUBMISSION", "frequency")


def test_topic_creation_scenario():
    topic_1 = Topic("SCENARIO", "SCENARIO_scenario_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.SCENARIO
    assert topic_1.entity_id == "SCENARIO_scenario_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("Scenario", "SCENARIO_scenario_id", "UPDATE", "is_primary")
    assert topic_2.entity_type == EventEntityType.SCENARIO
    assert topic_2.entity_id == "SCENARIO_scenario_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "is_primary"

    topic_3 = Topic("scenario", "SCENARIO_scenario_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.SCENARIO
    assert topic_3.entity_id == "SCENARIO_scenario_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic("scENArio", "SCENARIO_scenario_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.SCENARIO
    assert topic_4.entity_id == "SCENARIO_scenario_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "SCENARIO_scenario_id", "DELETION")
    assert topic_5.entity_type == EventEntityType.SCENARIO
    assert topic_5.entity_id == "SCENARIO_scenario_id"
    assert topic_5.operation == EventOperation.DELETION
    assert topic_5.attribute_name is None

    topic_6 = Topic("ScENaRIo", "SCENARIO_scenario_id", "update", "properties")
    assert topic_6.entity_type == EventEntityType.SCENARIO
    assert topic_6.entity_id == "SCENARIO_scenario_id"
    assert topic_6.operation == EventOperation.UPDATE
    assert topic_6.attribute_name == "properties"

    with pytest.raises(InvalidEntityId):
        _ = Topic("SCENARIO", "scenario_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("CYCLE", "SCENARIO_scenario_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("SCENARIO", "SCENARIO_scenario_id", "CREATION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("SCENARIO", "SCENARIO_scenario_id", "DELETION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("SCENARIO", "SCENARIO_scenario_id", "SUBMISSION", "is_primary")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("SCENARIO", "SCENARIO_scenario_id", attribute_name="is_primary")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("SCENARIO", "SCENARIO_scenario_id", "POPUlATE")


def test_topic_creation_pipeline():
    topic_1 = Topic("Pipeline", "PIPELINE_pipeline_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.PIPELINE
    assert topic_1.entity_id == "PIPELINE_pipeline_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("pipeline", "PIPELINE_pipeline_id", "UPDATE", "subscribers")
    assert topic_2.entity_type == EventEntityType.PIPELINE
    assert topic_2.entity_id == "PIPELINE_pipeline_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "subscribers"

    topic_3 = Topic("PIPELINE", "PIPELINE_pipeline_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.PIPELINE
    assert topic_3.entity_id == "PIPELINE_pipeline_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic("PIPElinE", "PIPELINE_pipeline_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.PIPELINE
    assert topic_4.entity_id == "PIPELINE_pipeline_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "PIPELINE_pipeline_id", "SUBMISSION")
    assert topic_5.entity_type == EventEntityType.PIPELINE
    assert topic_5.entity_id == "PIPELINE_pipeline_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    topic_6 = Topic("pipeLINE", "PIPELINE_pipeline_id", "deletion")
    assert topic_6.entity_type == EventEntityType.PIPELINE
    assert topic_6.entity_id == "PIPELINE_pipeline_id"
    assert topic_6.operation == EventOperation.DELETION
    assert topic_6.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic("PIPELINE", "pipeline_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("CYCLE" "", "PIPELINE_pipeline_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("PIPELINE", "PIPELINE_pipeline_id", "CREATION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("PIPELINE", "PIPELINE_pipeline_id", "DELETION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("PIPELINE", "PIPELINE_pipeline_id", "SUBMISSION", "subscribers")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("PIPELINE", "PIPELINE_pipeline_id", attribute_name="subscribers")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("PIPELINE", "PIPELINE_pipeline_id", "HI")


def test_topic_creation_task():
    topic_1 = Topic("Task", "TASK_task_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.TASK
    assert topic_1.entity_id == "TASK_task_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("task", "TASK_task_id", "UPDATE", "function")
    assert topic_2.entity_type == EventEntityType.TASK
    assert topic_2.entity_id == "TASK_task_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "function"

    topic_3 = Topic("TAsk", "TASK_task_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.TASK
    assert topic_3.entity_id == "TASK_task_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic("taSK", "TASK_task_id", "SUBMISSION")
    assert topic_4.entity_type == EventEntityType.TASK
    assert topic_4.entity_id == "TASK_task_id"
    assert topic_4.operation == EventOperation.SUBMISSION
    assert topic_4.attribute_name is None

    topic_5 = Topic(None, "TASK_task_id", "SUBMISSION")
    assert topic_5.entity_type == EventEntityType.TASK
    assert topic_5.entity_id == "TASK_task_id"
    assert topic_5.operation == EventOperation.SUBMISSION
    assert topic_5.attribute_name is None

    topic_6 = Topic("TASK", "TASK_task_id", "submission")
    assert topic_6.entity_type == EventEntityType.TASK
    assert topic_6.entity_id == "TASK_task_id"
    assert topic_6.operation == EventOperation.SUBMISSION
    assert topic_6.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic("TASK", "task_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("CYCLE" "", "TASK_task_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("TASK", "TASK_task_id", "CREATION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("TASK", "TASK_task_id", "DELETION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("TASK", "TASK_task_id", "SUBMISSION", "function")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("TASK", "TASK_task_id", attribute_name="function")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("TASK", "TASK_task_id", "hello", "function")


def test_topic_creation_datanode():
    topic_1 = Topic("Data_node", "DATANODE_dn_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.DATA_NODE
    assert topic_1.entity_id == "DATANODE_dn_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("Data_Node", "DATANODE_dn_id", "UPDATE", "properties")
    assert topic_2.entity_type == EventEntityType.DATA_NODE
    assert topic_2.entity_id == "DATANODE_dn_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "properties"

    topic_3 = Topic("data_node", "DATANODE_dn_id", "DELETION")
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
        _ = Topic("DATA_NODE", "dn_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("SCENARIO", "DATANODE_dn_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("DATA_NODE", "DATANODE_dn_id", "CREATION", "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("DATA_NODE", "DATANODE_dn_id", "DELETION", "properties")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("DATA_NODE", "DATANODE_dn_id", attribute_name="properties")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("DATA_NODE", "DATANODE_dn_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "DATANODE_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "DATANODE_job_id", "hello")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("DATA_NODE", "DATANODE_dn_id", "SUBMISSION", "properties")


def test_topic_creation_job():
    topic_1 = Topic("Job", "JOB_job_id", "CREATION")
    assert topic_1.entity_type == EventEntityType.JOB
    assert topic_1.entity_id == "JOB_job_id"
    assert topic_1.operation == EventOperation.CREATION
    assert topic_1.attribute_name is None

    topic_2 = Topic("job", "JOB_job_id", "UPDATE", "force")
    assert topic_2.entity_type == EventEntityType.JOB
    assert topic_2.entity_id == "JOB_job_id"
    assert topic_2.operation == EventOperation.UPDATE
    assert topic_2.attribute_name == "force"

    topic_3 = Topic("JOB", "JOB_job_id", "DELETION")
    assert topic_3.entity_type == EventEntityType.JOB
    assert topic_3.entity_id == "JOB_job_id"
    assert topic_3.operation == EventOperation.DELETION
    assert topic_3.attribute_name is None

    topic_4 = Topic(None, "JOB_job_id", "DELETION")
    assert topic_4.entity_type == EventEntityType.JOB
    assert topic_4.entity_id == "JOB_job_id"
    assert topic_4.operation == EventOperation.DELETION
    assert topic_4.attribute_name is None

    topic_5 = Topic("JoB", "JOB_job_id", "creation")
    assert topic_5.entity_type == EventEntityType.JOB
    assert topic_5.entity_id == "JOB_job_id"
    assert topic_5.operation == EventOperation.CREATION
    assert topic_5.attribute_name is None

    with pytest.raises(InvalidEntityId):
        _ = Topic("JOB", "job_id", "CREATION")

    with pytest.raises(InvalidEntityType):
        _ = Topic("SCENARIO", "JOB_job_id", "CREATION")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("JOB", "JOB_job_id", "CREATION", "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("JOB", "JOB_job_id", "DELETION", "force")

    with pytest.raises(InvalidEventAttributeName):
        _ = Topic("JOB", "JOB_job_id", attribute_name="force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("JOB", "JOB_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic(None, "JOB_job_id", "SUBMISSION")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("JOB", "JOB_job_id", "SUBMISSION", "force")

    with pytest.raises(InvalidEventOperation):
        _ = Topic("JOB", "JOB_job_id", "hello", "force")


def test_topic_equal():
    assert Topic() == Topic()
    assert Topic("scenario") == Topic("scenario")
    assert Topic(entity_id="PIPELINE_pipeline_id") == Topic(entity_id="PIPELINE_pipeline_id")
    assert Topic(operation="SUBMISSION") == Topic(operation="SUBMISSION")
    assert Topic("job", "JOB_id", "update", "status") == Topic("job", "JOB_id", "update", "status")
