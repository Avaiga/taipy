# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import pickle
import shutil
from datetime import datetime
from queue import Queue
from unittest.mock import patch

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import close_all_sessions

from taipy.common.config import Config
from taipy.common.config.checker._checker import _Checker
from taipy.common.config.common.frequency import Frequency
from taipy.common.config.common.scope import Scope
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core._version._version import _Version
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.config import (
    _ConfigIdChecker,
    _CoreSectionChecker,
    _DataNodeConfigChecker,
    _JobConfigChecker,
    _ScenarioConfigChecker,
    _TaskConfigChecker,
)
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.cycle._cycle_model import _CycleModel
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_id import CycleId
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data._data_model import _DataNodeModel
from taipy.core.data.in_memory import DataNodeId, InMemoryDataNode
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.job.job_id import JobId
from taipy.core.notification.notifier import Notifier
from taipy.core.orchestrator import Orchestrator
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario._scenario_model import _ScenarioModel
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_id import ScenarioId
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.sequence.sequence import Sequence
from taipy.core.sequence.sequence_id import SequenceId
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission import Submission
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task, TaskId

current_time = datetime.now()

@pytest.fixture(scope="function")
def current_datetime():
    return current_time


@pytest.fixture(scope="function")
def data_node():
    return InMemoryDataNode(
        "data_node",
        Scope.SCENARIO,
        version="random_version_number",
        properties={"default_data": "foo"},
    )


@pytest.fixture(scope="function")
def scenario(cycle):
    return Scenario(
        "sc",
        set(),
        {},
        set(),
        ScenarioId("SCENARIO_sc_id"),
        current_time,
        is_primary=False,
        tags={"foo"},
        cycle=None,
        version="random_version_number",
    )


@pytest.fixture(scope="function")
def cycle():
    example_date = datetime.fromisoformat("2021-11-11T11:11:01.000001")
    return Cycle(
        Frequency.DAILY,
        {},
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
        name="cc",
        id=CycleId("cc_id"),
    )


@pytest.fixture(scope="function")
def sequence(scenario):
    return Sequence({}, [], SequenceId(f"SEQUENCE_sequence_{scenario.id}"), version="random_version_number")


@pytest.fixture(scope="function")
def submission():
    return Submission("entity_id", "entity_type")


@pytest.fixture(scope="function", autouse=True)
def init(init_notifier):
    init_notifier()

    with patch("sys.argv", ["prog"]):
        yield

    init_notifier()


@pytest.fixture
def init_notifier():
    def _init_notifier():
        Notifier._topics_registrations_list = {}

    return _init_notifier
