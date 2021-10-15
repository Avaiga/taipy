import multiprocessing
from datetime import datetime
from functools import partial
from time import sleep

import pytest

from taipy.task import Job, JobId, Task, TaskId
from taipy.task.scheduler.executor.executor import Executor
from tests.task.scheduler.lock_data_source import LockDataSource


def execute(lock):
    with lock:
        ...
    return None


def test_can_execute_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(config_name="name", input=[], function=partial(execute, lock), output=[LockDataSource("lock")], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(True, 1)

    with lock:
        assert executor.can_execute()
        executor.execute(job)
        assert not executor.can_execute()

    task.lock.get()
    executor.can_execute()


def test_can_execute_parallel_multiple_submit():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(config_name="name", input=[], function=partial(execute, lock), output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(True, 2)

    with lock:
        assert executor.can_execute()
        executor.execute(job)
        assert executor.can_execute()


def test_can_execute_synchronous():
    task_id = TaskId("task_id1")
    task = Task(config_name="name", input=[], function=print, output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(False, None)

    assert executor.can_execute()
    executor.execute(job)
    assert executor.can_execute()
