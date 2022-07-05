# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import timedelta
from time import sleep
from unittest.mock import MagicMock

import pytest
from taipy.config import JobConfig
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope

from src.taipy.core._scheduler._dispatcher._development_job_dispatcher import _DevelopmentJobDispatcher
from src.taipy.core._scheduler._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher
from src.taipy.core.common.alias import JobId, TaskId
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.job.job import Job
from src.taipy.core.job.status import Status
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task


@pytest.fixture
def task_id():
    return TaskId("task_id1")


@pytest.fixture
def task(task_id):
    return Task(config_id="name", function=print, input=[], output=[], id=task_id)


@pytest.fixture
def job_id():
    return JobId("id1")


@pytest.fixture
def job(task, job_id):
    return Job(job_id, task)


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


def test_create_job(task, job):
    assert job.id == "id1"
    assert task in job
    assert job.is_submitted()


def test_comparison(task):
    job_id_1 = JobId("id1")
    job_id_2 = JobId("id2")

    job_1 = Job(job_id_1, task)
    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = Job(job_id_2, task)

    assert job_1 < job_2
    assert job_2 > job_1
    assert job_1 <= job_2
    assert job_1 <= job_1
    assert job_2 >= job_1
    assert job_1 >= job_1
    assert job_1 == job_1
    assert job_1 != job_2


def test_status_job(job):
    assert job.is_submitted()
    assert job.is_skipped() is False
    assert job.is_pending() is False
    assert job.is_blocked() is False
    assert job.is_cancelled() is False
    assert job.is_failed() is False
    assert job.is_completed() is False
    assert job.is_running() is False

    job.cancelled()
    assert job.is_cancelled()
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


def test_notification_job(job):
    subscribe = MagicMock()
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
    task = Task(config_id="name", input=[], function=_error, output=[], id=task_id)
    job = Job(job_id, task)

    _dispatch(task, job)

    job = _JobManager._get(job_id)
    assert job.is_failed()
    assert 'raise RuntimeError("Something bad has happened")' in str(job.stacktrace[0])


def test_handle_exception_in_input_data_node(task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", input=[data_node], function=print, output=[], id=task_id)
    job = Job(job_id, task)

    _dispatch(task, job)

    job = _JobManager._get(job_id)
    assert job.is_failed()
    assert "taipy.core.exceptions.exceptions.NoData" in str(job.stacktrace[0])


def test_handle_exception_in_ouptut_data_node(replace_in_memory_write_fct, task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", input=[], function=_foo, output=[data_node], id=task_id)
    job = Job(job_id, task)

    _dispatch(task, job)

    job = _JobManager._get(job_id)

    assert job.is_failed()
    assert "taipy.core.exceptions.exceptions.DataNodeWritingError" in str(job.stacktrace[0])


def test_auto_set_and_reload(current_datetime, job_id):
    task_1 = Task(config_id="name_1", function=_foo, id=TaskId("task_1"))
    task_2 = Task(config_id="name_2", function=_foo, id=TaskId("task_2"))
    job_1 = Job(job_id, task_1)

    _TaskManager._set(task_1)
    _TaskManager._set(task_2)
    _JobManager._set(job_1)

    job_2 = _JobManager._get(job_1)

    assert job_1.task.id == task_1.id
    job_1.task = task_2
    assert job_1.task.id == task_2.id
    assert job_1.task.id == task_2.id

    assert not job_1.force
    job_1.force = True
    assert job_1.force
    assert job_2.force

    assert job_1.status == Status.SUBMITTED
    job_1.status = Status.BLOCKED
    assert job_1.status == Status.BLOCKED
    assert job_2.status == Status.BLOCKED

    new_datetime = current_datetime + timedelta(1)
    job_1.creation_date = new_datetime
    assert job_1.creation_date == new_datetime
    assert job_2.creation_date == new_datetime

    with job_1 as job:
        assert job.task.id == task_2.id
        assert job.force
        assert job.status == Status.BLOCKED
        assert job.creation_date == new_datetime
        assert job._is_in_context

        new_datetime_2 = new_datetime + timedelta(1)
        job.task = task_1
        job.force = False
        job.status = Status.COMPLETED
        job.creation_date = new_datetime_2

        assert job.task.id == task_2.id
        assert job.force
        assert job.status == Status.BLOCKED
        assert job.creation_date == new_datetime
        assert job._is_in_context

    assert job_1.task.id == task_1.id
    assert not job_1.force
    assert job_1.status == Status.COMPLETED
    assert job_1.creation_date == new_datetime_2
    assert not job_1._is_in_context


def _dispatch(task: Task, job: Job, mode=JobConfig._DEVELOPMENT_MODE):
    Config.configure_job_executions(mode=mode)
    _TaskManager._set(task)
    _JobManager._set(job)
    dispatcher = _StandaloneJobDispatcher()
    if mode == JobConfig._DEVELOPMENT_MODE:
        dispatcher = _DevelopmentJobDispatcher()
    dispatcher._dispatch(job)
