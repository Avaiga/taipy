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

from datetime import datetime, timedelta
from time import sleep
from typing import Union, cast
from unittest import mock
from unittest.mock import MagicMock

import freezegun
import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core import JobId, TaskId
from taipy.core._orchestrator._abstract_orchestrator import _AbstractOrchestrator
from taipy.core._orchestrator._dispatcher._development_job_dispatcher import _DevelopmentJobDispatcher
from taipy.core._orchestrator._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.job._job_manager import _JobManager
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.job.status import Status
from taipy.core.scenario.scenario import Scenario
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


@pytest.fixture
def task_id():
    return TaskId("task_id1")


@pytest.fixture
def task(task_id):
    return Task(config_id="name", properties={}, function=print, input=[], output=[], id=task_id)


@pytest.fixture
def job_id():
    return JobId("id1")


@pytest.fixture(scope="class")
def scenario():
    return Scenario(
        "scenario_config",
        [],
        {},
        [],
        "SCENARIO_scenario_config",
        version="random_version_number",
    )


@pytest.fixture
def job(task, job_id):
    return Job(job_id, task, "submit_id", "SCENARIO_scenario_config")


@pytest.fixture
def replace_in_memory_write_fct():
    default_write = InMemoryDataNode.write
    InMemoryDataNode.write = _error
    yield
    InMemoryDataNode.write = default_write


def _foo():
    return 42


def _error():
    raise RuntimeError("Something bad has happened")


def test_job_equals(job):
    _TaskManagerFactory._build_manager()._set(job.task)
    job_manager = _JobManagerFactory()._build_manager()

    job_id = job.id
    job_manager._set(job)

    # To test if instance is same type
    task = Task("task", {}, print, [], [], job_id)

    job_2 = job_manager._get(job_id)
    assert job == job_2
    assert job != job_id
    assert job != task


def test_create_job(scenario, task, job):
    from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory

    _ScenarioManagerFactory._build_manager()._set(scenario)

    assert job.id == "id1"
    assert task in job
    assert job.is_submitted()
    assert job.submit_id is not None
    assert job.submit_entity_id == "SCENARIO_scenario_config"
    assert job.submit_entity == scenario
    with mock.patch("taipy.core.get") as get_mck:
        get_mck.return_value = task
        assert job.get_label() == "name > " + job.id
    assert job.get_simple_label() == job.id


def test_comparison(task):
    job_id_1 = JobId("id1")
    job_id_2 = JobId("id2")

    job_1 = Job(job_id_1, task, "submit_id", "scenario_entity_id")
    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = Job(job_id_2, task, "submit_id", "scenario_entity_id")

    assert job_1 < job_2
    assert job_2 > job_1
    assert job_1 <= job_2
    assert job_1 <= job_1
    assert job_2 >= job_1
    assert job_1 >= job_1
    assert job_1 == job_1
    assert job_1 != job_2


def test_status_job(task):
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job("job_id", task, submission.id, "SCENARIO_scenario_config")
    submission.jobs = [job]

    assert job.is_submitted()
    assert job.is_skipped() is False
    assert job.is_pending() is False
    assert job.is_blocked() is False
    assert job.is_canceled() is False
    assert job.is_failed() is False
    assert job.is_completed() is False
    assert job.is_running() is False

    job.canceled()
    assert job.is_canceled()
    job.failed()
    assert job.is_failed()
    job.running()
    assert job.is_running()
    job.completed()
    assert job.is_completed()
    job.pending()
    assert job.is_pending()
    job.blocked()
    assert job.is_blocked()
    job.skipped()
    assert job.is_skipped()


def test_stacktrace_job(task):
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job("job_id", task, submission.id, "SCENARIO_scenario_config")

    fake_stacktraces = [
        """Traceback (most recent call last):
File "<stdin>", line 1, in <module>
ZeroDivisionError: division by zero""",
        "Another error",
        "yet\nAnother\nError",
    ]

    job.stacktrace = fake_stacktraces
    assert job.stacktrace == fake_stacktraces


def test_notification_job(task):
    subscribe = MagicMock()
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job("job_id", task, submission.id, "SCENARIO_scenario_config")
    submission.jobs = [job]

    job._on_status_change(subscribe)

    job.running()
    subscribe.assert_called_once_with(job)
    subscribe.reset_mock()

    job.completed()
    subscribe.assert_called_once_with(job)
    subscribe.reset_mock()

    job.skipped()
    subscribe.assert_called_once_with(job)


def test_handle_exception_in_user_function(task_id, job_id):
    task = Task(config_id="name", properties={}, input=[], function=_error, output=[], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job(job_id, task, submission.id, "scenario_entity_id")
    submission.jobs = [job]

    _dispatch(task, job)

    job = _JobManager._get(job_id)
    assert job.is_failed()
    assert 'raise RuntimeError("Something bad has happened")' in str(job.stacktrace[0])


def test_handle_exception_in_input_data_node(task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", properties={}, input=[data_node], function=print, output=[], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job(job_id, task, submission.id, "scenario_entity_id")
    submission.jobs = [job]

    _dispatch(task, job)

    job = _JobManager._get(job_id)
    assert job.is_failed()
    assert "taipy.core.exceptions.exceptions.NoData" in str(job.stacktrace[0])


def test_handle_exception_in_ouptut_data_node(replace_in_memory_write_fct, task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", properties={}, input=[], function=_foo, output=[data_node], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task.id, task._ID_PREFIX, task.config_id)
    job = Job(job_id, task, submission.id, "scenario_entity_id")
    submission.jobs = [job]

    _dispatch(task, job)

    job = _JobManager._get(job_id)

    assert job.is_failed()
    assert "taipy.core.exceptions.exceptions.DataNodeWritingError" in str(job.stacktrace[0])


def test_auto_set_and_reload(current_datetime, job_id):
    task_1 = Task(config_id="name_1", properties={}, function=_foo, id=TaskId("task_1"))
    task_2 = Task(config_id="name_2", properties={}, function=_foo, id=TaskId("task_2"))
    submission = _SubmissionManagerFactory._build_manager()._create(task_1.id, task_1._ID_PREFIX, task_1.config_id)
    job_1 = Job(job_id, task_1, submission.id, "scenario_entity_id")
    submission.jobs = [job_1]

    _TaskManager._set(task_1)
    _TaskManager._set(task_2)
    _JobManager._set(job_1)

    job_2 = _JobManager._get(job_1, "submit_id_2")

    # auto set & reload on task attribute
    assert job_1.task.id == task_1.id
    assert job_2.task.id == task_1.id
    job_1.task = task_2
    assert job_1.task.id == task_2.id
    assert job_2.task.id == task_2.id
    job_2.task = task_1
    assert job_1.task.id == task_1.id
    assert job_2.task.id == task_1.id

    # auto set & reload on force attribute
    assert not job_1.force
    assert not job_2.force
    job_1.force = True
    assert job_1.force
    assert job_2.force
    job_2.force = False
    assert not job_1.force
    assert not job_2.force

    # auto set & reload on status attribute
    assert job_1.status == Status.SUBMITTED
    assert job_2.status == Status.SUBMITTED
    job_1.status = Status.CANCELED
    assert job_1.status == Status.CANCELED
    assert job_2.status == Status.CANCELED
    job_2.status = Status.BLOCKED
    assert job_1.status == Status.BLOCKED
    assert job_2.status == Status.BLOCKED

    # auto set & reload on creation_date attribute
    new_datetime = current_datetime + timedelta(1)
    new_datetime_1 = current_datetime + timedelta(1)
    job_1.creation_date = new_datetime_1
    assert job_1.creation_date == new_datetime_1
    assert job_2.creation_date == new_datetime_1
    job_2.creation_date = new_datetime
    assert job_1.creation_date == new_datetime
    assert job_2.creation_date == new_datetime

    with job_1 as job:
        assert job.task.id == task_1.id
        assert not job.force
        assert job.status == Status.BLOCKED
        assert job.creation_date == new_datetime
        assert job._is_in_context

        new_datetime_2 = new_datetime + timedelta(1)
        job.task = task_2
        job.force = True
        job.status = Status.COMPLETED
        job.creation_date = new_datetime_2

        assert job.task.id == task_1.id
        assert not job.force
        assert job.status == Status.BLOCKED
        assert job.creation_date == new_datetime
        assert job._is_in_context

    assert job_1.task.id == task_2.id
    assert job_1.force
    assert job_1.status == Status.COMPLETED
    assert job_1.creation_date == new_datetime_2
    assert not job_1._is_in_context


def test_status_records(job_id):
    task_1 = Task(config_id="name_1", properties={}, function=_foo, id=TaskId("task_1"))
    submission = _SubmissionManagerFactory._build_manager()._create(task_1.id, task_1._ID_PREFIX, task_1.config_id)
    with freezegun.freeze_time("2024-09-25 13:30:30"):
        job_1 = Job(job_id, task_1, submission.id, "scenario_entity_id")
    submission.jobs = [job_1]

    _TaskManager._set(task_1)
    _JobManager._set(job_1)

    assert job_1._status_change_records == {"SUBMITTED": datetime(2024, 9, 25, 13, 30, 30)}
    assert job_1.submitted_time == datetime(2024, 9, 25, 13, 30, 30)
    assert job_1.execution_duration is None

    with freezegun.freeze_time("2024-09-25 13:35:30"):
        job_1.pending()
    assert job_1._status_change_records == {
        "SUBMITTED": datetime(2024, 9, 25, 13, 30, 30),
        "PENDING": datetime(2024, 9, 25, 13, 35, 30),
    }
    assert job_1.execution_duration is None
    with freezegun.freeze_time("2024-09-25 13:36:00"):
        assert job_1.pending_duration == 30

    with freezegun.freeze_time("2024-09-25 13:40:30"):
        job_1.blocked()
    assert job_1._status_change_records == {
        "SUBMITTED": datetime(2024, 9, 25, 13, 30, 30),
        "PENDING": datetime(2024, 9, 25, 13, 35, 30),
        "BLOCKED": datetime(2024, 9, 25, 13, 40, 30),
    }
    assert job_1.execution_duration is None
    with freezegun.freeze_time("2024-09-25 13:41:00"):
        assert job_1.blocked_duration == 30

    with freezegun.freeze_time("2024-09-25 13:50:30"):
        job_1.running()
    assert job_1._status_change_records == {
        "SUBMITTED": datetime(2024, 9, 25, 13, 30, 30),
        "PENDING": datetime(2024, 9, 25, 13, 35, 30),
        "BLOCKED": datetime(2024, 9, 25, 13, 40, 30),
        "RUNNING": datetime(2024, 9, 25, 13, 50, 30),
    }
    assert job_1.run_time == datetime(2024, 9, 25, 13, 50, 30)
    assert job_1.pending_duration == 900
    assert job_1.blocked_duration == 600
    assert job_1.execution_duration > 0

    with freezegun.freeze_time("2024-09-25 13:56:35"):
        job_1.completed()
    assert job_1._status_change_records == {
        "SUBMITTED": datetime(2024, 9, 25, 13, 30, 30),
        "PENDING": datetime(2024, 9, 25, 13, 35, 30),
        "BLOCKED": datetime(2024, 9, 25, 13, 40, 30),
        "RUNNING": datetime(2024, 9, 25, 13, 50, 30),
        "COMPLETED": datetime(2024, 9, 25, 13, 56, 35),
    }
    assert job_1.execution_duration == 365


def test_is_deletable():
    with mock.patch("taipy.core.job._job_manager._JobManager._is_deletable") as mock_submit:
        task = Task(config_id="name_1", properties={}, function=_foo, id=TaskId("task_1"))
        job = Job(job_id, task, "submit_id_1", "scenario_entity_id")
        job.is_deletable()
        mock_submit.assert_called_once_with(job)


def _dispatch(task: Task, job: Job, mode=JobConfig._DEVELOPMENT_MODE):
    Config.configure_job_executions(mode=mode)
    _TaskManager._set(task)
    _JobManager._set(job)
    dispatcher: Union[_StandaloneJobDispatcher, _DevelopmentJobDispatcher] = _StandaloneJobDispatcher(
        cast(_AbstractOrchestrator, _OrchestratorFactory._orchestrator)
    )
    if mode == JobConfig._DEVELOPMENT_MODE:
        dispatcher = _DevelopmentJobDispatcher(cast(_AbstractOrchestrator, _OrchestratorFactory._orchestrator))
    dispatcher._dispatch(job)
