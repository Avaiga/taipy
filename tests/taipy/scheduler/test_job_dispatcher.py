import glob
import multiprocessing
import os
from datetime import datetime
from functools import partial
from time import sleep
from unittest.mock import MagicMock

import pytest

from taipy.common.alias import JobId, TaskId
from taipy.config.config import Config
from taipy.data import Scope
from taipy.data.manager import DataManager
from taipy.job import Job
from taipy.scheduler.job_dispatcher import JobDispatcher
from taipy.task import Task


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def execute(lock):
    with lock:
        ...
    return None


def test_can_execute_synchronous():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(
        config_name="name",
        input=[],
        function=partial(execute, lock),
        output=[DataManager().get_or_create(Config.add_data_node("input1", default_data=21))],
        id=task_id,
    )
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = JobDispatcher(2)

    with lock:
        assert executor.can_execute()
        executor.dispatch(job)
        assert executor.can_execute()
        executor.dispatch(job)
        assert not executor.can_execute()

    assert_true_after_10_second_max(lambda: executor.can_execute())


def test_can_execute_parallel_multiple_submit():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(config_name="name", input=[], function=partial(execute, lock), output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = JobDispatcher(2)

    with lock:
        assert executor.can_execute()
        executor.dispatch(job)
        assert executor.can_execute()


def test_can_execute_synchronous_2():
    task_id = TaskId("task_id1")
    task = Task(config_name="name", input=[], function=print, output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = JobDispatcher(None)

    assert executor.can_execute()
    executor.dispatch(job)
    assert executor.can_execute()


def test_handle_exception_in_user_function():
    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    task = Task(config_name="name", input=[], function=_error, output=[], id=task_id)
    job = Job(job_id, task)

    executor = JobDispatcher(None)
    executor.dispatch(job)
    assert job.is_failed()
    assert "Something bad has happened" == str(job.exceptions[0])


def test_handle_exception_when_writing_datanode():
    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    output = MagicMock()
    output.config_name = "my_raising_datanode"
    output.write.side_effect = ValueError()
    task = Task(config_name="name", input=[], function=print, output=[output], id=task_id)
    job = Job(job_id, task)

    executor = JobDispatcher(None)
    executor.dispatch(job)
    assert job.is_failed()
    stack_trace = str(job.exceptions[0])
    assert "node" in stack_trace


def _error():
    raise RuntimeError("Something bad has happened")


def assert_true_after_10_second_max(assertion):
    start = datetime.now()
    while (datetime.now() - start).seconds < 10:
        sleep(0.1)  # Limit CPU usage
        if assertion():
            return
    assert assertion()
