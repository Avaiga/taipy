import multiprocessing
from datetime import datetime
from functools import partial
from time import sleep

import pytest

from taipy.task import Job, JobId, Task, TaskId
from taipy.task.scheduler.executor.executor import Executor


def execute(lock):
    with lock:
        ...


def test_can_execute_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(name="name", input=[], function=partial(execute, lock), output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(True, 1)

    with lock:
        assert executor.can_execute()
        executor.execute(job)
        assert not executor.can_execute()

    assert_true_after_10_second_max(lambda: executor.can_execute())


def test_can_execute_parallel_multiple_submit():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(name="name", input=[], function=partial(execute, lock), output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(True, 2)

    with lock:
        assert executor.can_execute()
        executor.execute(job)
        assert executor.can_execute()


def test_can_execute_synchronous():
    task_id = TaskId("task_id1")
    task = Task(name="name", input=[], function=print, output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = Executor(False, None)

    assert executor.can_execute()
    executor.execute(job)
    assert executor.can_execute()


def assert_true_after_10_second_max(assertion):
    start = datetime.now()
    while (datetime.now() - start).seconds < 10:
        if assertion():
            return
    assert assertion()
