import glob
import multiprocessing
import os
from datetime import datetime, timedelta
from functools import partial
from time import sleep
from unittest import mock
from unittest.mock import MagicMock

import pytest

from taipy.core.common.alias import DataNodeId, JobId, TaskId
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.job.job import Job
from taipy.core.scheduler.job_dispatcher import JobDispatcher
from taipy.core.scheduler.scheduler import Scheduler
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task


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
        config_id="name",
        input=[],
        function=partial(execute, lock),
        output=[_DataManager._get_or_create(Config._add_data_node("input1", default_data=21))],
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
    task = Task(config_id="name", input=[], function=partial(execute, lock), output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = JobDispatcher(2)

    with lock:
        assert executor.can_execute()
        executor.dispatch(job)
        assert executor.can_execute()


def test_can_execute_synchronous_2():
    task_id = TaskId("task_id1")
    task = Task(config_id="name", input=[], function=print, output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    executor = JobDispatcher(None)

    assert executor.can_execute()
    executor.dispatch(job)
    assert executor.can_execute()


def test_handle_exception_in_user_function():
    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    task = Task(config_id="name", input=[], function=_error, output=[], id=task_id)
    job = Job(job_id, task)

    executor = JobDispatcher(None)
    executor.dispatch(job)
    assert job.is_failed()
    assert "Something bad has happened" == str(job.exceptions[0])


def test_handle_exception_when_writing_datanode():
    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    output = MagicMock()
    output.id = DataNodeId("output_id")
    output.config_id = "my_raising_datanode"
    output.is_in_cache = False
    output.write.side_effect = ValueError()
    task = Task(config_id="name", input=[], function=print, output=[output], id=task_id)
    job = Job(job_id, task)

    dispatcher = JobDispatcher(None)

    with mock.patch("taipy.core.data._data_manager._DataManager._get") as get:
        get.return_value = output
        dispatcher.dispatch(job)
        assert job.is_failed()
        stack_trace = str(job.exceptions[0])
        assert "node" in stack_trace


def test_need_to_run_no_output():
    def concat(a, b):
        return a + b

    hello_cfg = Config._add_data_node("hello", default_data="Hello ")
    world_cfg = Config._add_data_node("world", default_data="world !")
    task_cfg = Config._add_task("name", input=[hello_cfg, world_cfg], function=concat, output=[])
    task = _TaskManager()._get_or_create(task_cfg)

    assert JobDispatcher(None)._needs_to_run(task)


def test_need_to_run_output_not_cacheable():
    def concat(a, b):
        return a + b

    hello_cfg = Config._add_data_node("hello", default_data="Hello ")
    world_cfg = Config._add_data_node("world", default_data="world !")
    hello_world_cfg = Config._add_data_node("hello_world", cacheable=False)
    task_cfg = Config._add_task("name", input=[hello_cfg, world_cfg], function=concat, output=[hello_world_cfg])
    task = _TaskManager()._get_or_create(task_cfg)

    assert JobDispatcher(None)._needs_to_run(task)


def nothing():
    return True


def test_need_to_run_output_cacheable_no_input():

    hello_world_cfg = Config._add_data_node("hello_world", cacheable=True)
    task_cfg = Config._add_task("name", input=[], function=nothing, output=[hello_world_cfg])
    task = _TaskManager()._get_or_create(task_cfg)

    scheduler = Scheduler()
    assert scheduler._dispatcher._needs_to_run(task)
    scheduler.submit_task(task)

    assert not scheduler._dispatcher._needs_to_run(task)


def test_need_to_run_output_cacheable_no_validity_period():

    hello_cfg = Config._add_data_node("hello", default_data="Hello ")
    world_cfg = Config._add_data_node("world", default_data="world !")
    hello_world_cfg = Config._add_data_node("hello_world", cacheable=True)
    task_cfg = Config._add_task("name", input=[hello_cfg, world_cfg], function=concat, output=[hello_world_cfg])
    task = _TaskManager()._get_or_create(task_cfg)

    scheduler = Scheduler()
    assert scheduler._dispatcher._needs_to_run(task)
    scheduler.submit_task(task)

    assert not scheduler._dispatcher._needs_to_run(task)


def concat(a, b):
    return a + b


def test_need_to_run_output_cacheable_with_validity_period_up_to_date():
    hello_cfg = Config._add_data_node("hello", default_data="Hello ")
    world_cfg = Config._add_data_node("world", default_data="world !")
    hello_world_cfg = Config._add_data_node("hello_world", cacheable=True, validity_days=1)
    task_cfg = Config._add_task("name", input=[hello_cfg, world_cfg], function=concat, output=[hello_world_cfg])
    task = _TaskManager()._get_or_create(task_cfg)

    scheduler = Scheduler()
    assert scheduler._dispatcher._needs_to_run(task)
    job = scheduler.submit_task(task)

    assert not scheduler._dispatcher._needs_to_run(task)
    job_skipped = scheduler.submit_task(task)

    assert job.is_completed()
    assert job.is_finished()
    assert job_skipped.is_skipped()
    assert job_skipped.is_finished()


def test_need_to_run_output_cacheable_with_validity_period_obsolete():
    def concat(a, b):
        return a + b

    hello_cfg = Config._add_data_node("hello", default_data="Hello ")
    world_cfg = Config._add_data_node("world", default_data="world !")
    hello_world_cfg = Config._add_data_node("hello_world", cacheable=True, validity_days=1)
    task_cfg = Config._add_task("name", input=[hello_cfg, world_cfg], function=concat, output=[hello_world_cfg])
    task = _TaskManager()._get_or_create(task_cfg)

    scheduler = Scheduler()
    assert scheduler._dispatcher._needs_to_run(task)
    scheduler.submit_task(task)

    output = task.hello_world
    output._last_edition_date = datetime.now() - timedelta(days=1, minutes=30)
    _DataManager()._set(output)
    assert scheduler._dispatcher._needs_to_run(task)


def _error():
    raise RuntimeError("Something bad has happened")


def assert_true_after_10_second_max(assertion):
    start = datetime.now()
    while (datetime.now() - start).seconds < 10:
        sleep(0.1)  # Limit CPU usage
        if assertion():
            return
    assert assertion()
