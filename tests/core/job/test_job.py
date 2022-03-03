from time import sleep
from unittest.mock import MagicMock

import pytest

from taipy.core.common.alias import JobId, TaskId
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.data_node import NoData
from taipy.core.exceptions.job import DataNodeWritingError
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.scheduler.job_dispatcher import JobDispatcher
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager


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
    job.on_status_change(subscribe)

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

    job = JobManager.get(job_id)
    assert job.is_failed()
    with pytest.raises(RuntimeError):
        raise job.exceptions[0]
    assert "Something bad has happened" == str(job.exceptions[0])


def test_handle_exception_in_input_data_node(task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", input=[data_node], function=print, output=[], id=task_id)
    job = Job(job_id, task)

    _dispatch(task, job)

    job = JobManager.get(job_id)
    assert job.is_failed()
    with pytest.raises(NoData):
        raise job.exceptions[0]


def test_handle_exception_in_ouptut_data_node(replace_in_memory_write_fct, task_id, job_id):
    data_node = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    task = Task(config_id="name", input=[], function=_foo, output=[data_node], id=task_id)
    job = Job(job_id, task)

    _dispatch(task, job)

    job = JobManager.get(job_id)
    assert job.is_failed()
    with pytest.raises(DataNodeWritingError):
        raise job.exceptions[0]
    assert "Error writing in datanode" in str(job.exceptions[0])


def _error():
    raise RuntimeError("Something bad has happened")


def _dispatch(task: Task, job: Job):
    TaskManager.set(task)
    JobManager.set(job)
    executor = JobDispatcher(None)
    executor.dispatch(job)


def _foo():
    return 42
