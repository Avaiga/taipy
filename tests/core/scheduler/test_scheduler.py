import glob
import multiprocessing
import os
import random
import string
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from functools import partial
from time import sleep

import pytest

from taipy.core._scheduler._executor._synchronous import _Synchronous
from taipy.core._scheduler._scheduler import _Scheduler
from taipy.core.common.scope import Scope
from taipy.core.config._config import _Config
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.task.task import Task
from tests.core.utils import assert_true_after_1_minute_max


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def multiply(nb1: float, nb2: float):
    sleep(0.1)
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_submit_task():
    scheduler = _Scheduler()

    before_creation = datetime.now()
    sleep(0.1)
    task = _create_task(multiply)
    output_dn_id = task.output[f"{task.config_id}_output0"].id

    assert _DataManager._get(output_dn_id).last_edition_date > before_creation
    assert _DataManager._get(output_dn_id).job_ids == []
    assert _DataManager._get(output_dn_id).is_ready_for_reading

    before_submission_creation = datetime.now()
    sleep(0.1)
    job = scheduler.submit_task(task)
    sleep(0.1)
    after_submission_creation = datetime.now()
    assert _DataManager._get(output_dn_id).read() == 42
    assert _DataManager._get(output_dn_id).last_edition_date > before_submission_creation
    assert _DataManager._get(output_dn_id).last_edition_date < after_submission_creation
    assert _DataManager._get(output_dn_id).job_ids == [job.id]
    assert _DataManager._get(output_dn_id).is_ready_for_reading
    assert job.is_completed()


def test_submit_task_that_return_multiple_outputs():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    scheduler = _Scheduler()

    with_tuple = _create_task(return_2tuple, 2)
    with_list = _create_task(return_list, 2)

    scheduler.submit_task(with_tuple)
    scheduler.submit_task(with_list)

    assert (
        with_tuple.output[f"{with_tuple.config_id}_output0"].read()
        == with_list.output[f"{with_list.config_id}_output0"].read()
        == 42
    )
    assert (
        with_tuple.output[f"{with_tuple.config_id}_output1"].read()
        == with_list.output[f"{with_list.config_id}_output1"].read()
        == 21
    )


def test_submit_task_returns_single_iterable_output():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    scheduler = _Scheduler()
    task_with_tuple = _create_task(return_2tuple, 1)
    task_with_list = _create_task(return_list, 1)

    scheduler.submit_task(task_with_tuple)
    assert task_with_tuple.output[f"{task_with_tuple.config_id}_output0"].read() == (42, 21)
    scheduler.submit_task(task_with_list)
    assert task_with_list.output[f"{task_with_list.config_id}_output0"].read() == [42, 21]


def test_data_node_not_written_due_to_wrong_result_nb():
    def return_2tuple():
        return lambda nb1, nb2: (multiply(nb1, nb2), multiply(nb1, nb2) / 2)

    scheduler = _Scheduler()
    task = _create_task(return_2tuple(), 3)

    job = scheduler.submit_task(task)
    assert task.output[f"{task.config_id}_output0"].read() == 0
    assert job.is_failed()


def test_submit_task_in_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    scheduler = _Scheduler(Config.configure_job_executions(nb_of_workers=2))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = scheduler.submit_task(task)
        assert task.output[f"{task.config_id}_output0"].read() == 0
        assert job.is_running()

    assert_true_after_1_minute_max(job.is_completed)


def test_submit_task_multithreading_multiple_task():
    scheduler = _Scheduler(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = scheduler.submit_task(task_1)
            job_2 = scheduler.submit_task(task_2)

            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
            assert job_1.is_running()
            assert job_2.is_running()

        assert_true_after_1_minute_max(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
        assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
        assert_true_after_1_minute_max(job_2.is_completed)
        assert job_1.is_running()
        assert job_2.is_completed()

    assert_true_after_1_minute_max(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert task_2.output[f"{task_2.config_id}_output0"].read() == 42
    assert_true_after_1_minute_max(job_1.is_completed)
    assert job_2.is_completed()


def test_submit_task_multithreading_multiple_task_in_sync_way_to_check_job_status():
    scheduler = _Scheduler(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_0 = m.Lock()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_0 = _create_task(partial(lock_multiply, lock_0))
    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_0:
        scheduler.submit_task(task_0)
        with lock_1:
            with lock_2:
                job_1 = scheduler.submit_task(task_2)
                job_2 = scheduler.submit_task(task_1)

                assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
                assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
                assert job_1.is_running()
                assert job_2.is_pending()

            assert_true_after_1_minute_max(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert_true_after_1_minute_max(job_1.is_completed)
            assert_true_after_1_minute_max(job_2.is_running)

    assert_true_after_1_minute_max(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert task_2.output[f"{task_2.config_id}_output0"].read() == 42
    assert job_1.is_completed()
    assert_true_after_1_minute_max(job_2.is_completed)


def test_blocked_task():
    scheduler = _Scheduler(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    foo_cfg = Config.configure_data_node("foo", default_data=1)
    foo = _DataManager._get_or_create(foo_cfg)
    bar_cfg = Config.configure_data_node("bar")
    bar = _DataManager._get_or_create(bar_cfg)
    baz_cfg = Config.configure_data_node("baz")
    baz = _DataManager._get_or_create(baz_cfg)
    task_1 = Task("by_2", partial(lock_multiply, lock_1, 2), [foo], [bar])
    task_2 = Task("by_3", partial(lock_multiply, lock_2, 3), [bar], [baz])

    assert task_1.foo.is_ready_for_reading  # foo is ready
    assert not task_1.bar.is_ready_for_reading  # But bar is not ready
    assert not task_2.baz.is_ready_for_reading  # neither does baz

    assert len(scheduler.blocked_jobs) == 0
    job_2 = scheduler.submit_task(task_2)  # job 2 is submitted first
    assert job_2.is_blocked()  # since bar is not up_to_date the job 2 is blocked
    assert len(scheduler.blocked_jobs) == 1
    with lock_2:
        with lock_1:
            job_1 = scheduler.submit_task(task_1)  # job 1 is submitted and locked
            assert job_1.is_running()  # so it is still running
            assert not _DataManager._get(task_1.bar.id).is_ready_for_reading  # And bar still not ready
            assert job_2.is_blocked()  # the job_2 remains blocked
        assert_true_after_1_minute_max(job_1.is_completed)  # job1 unlocked and can complete
        assert _DataManager._get(task_1.bar.id).is_ready_for_reading  # bar becomes ready
        assert _DataManager._get(task_1.bar.id).read() == 2  # the data is computed and written
        assert_true_after_1_minute_max(job_2.is_running)  # And job 2 can start running
        assert len(scheduler.blocked_jobs) == 0
    assert_true_after_1_minute_max(job_2.is_completed)  # job 2 unlocked so it can complete
    assert _DataManager._get(task_2.baz.id).is_ready_for_reading  # baz becomes ready
    assert _DataManager._get(task_2.baz.id).read() == 6  # the data is computed and written


class MyScheduler(_Scheduler):
    def getJobDispatcher(self):
        return self._dispatcher


def test_task_scheduler_create_synchronous_dispatcher():
    scheduler = MyScheduler(Config.configure_job_executions())
    assert isinstance(scheduler.getJobDispatcher()._executor, _Synchronous)
    assert scheduler.getJobDispatcher()._nb_available_workers == 1


def test_task_scheduler_create_parallel_dispatcher():
    scheduler = MyScheduler(Config.configure_job_executions(nb_of_workers=42))
    assert isinstance(scheduler.getJobDispatcher()._executor, ProcessPoolExecutor)
    assert scheduler.getJobDispatcher()._nb_available_workers == 42


def _create_task(function, nb_outputs=1):
    output_dn_config_id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    input_dn = [
        _DataManager._get_or_create(Config.configure_data_node("input1", "pickle", Scope.PIPELINE, default_data=21)),
        _DataManager._get_or_create(Config.configure_data_node("input2", "pickle", Scope.PIPELINE, default_data=2)),
    ]
    output_dn = [
        _DataManager._get_or_create(
            Config.configure_data_node(f"{output_dn_config_id}_output{i}", "pickle", Scope.PIPELINE, default_data=0)
        )
        for i in range(nb_outputs)
    ]

    return Task(
        output_dn_config_id,
        function=function,
        input=input_dn,
        output=output_dn,
    )
