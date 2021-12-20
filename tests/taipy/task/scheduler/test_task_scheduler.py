import glob
import multiprocessing
import os
import uuid
from datetime import datetime
from functools import partial
from time import sleep
from unittest.mock import patch

import pytest

from taipy.common.alias import DataSourceId, JobId
from taipy.config import Config, JobConfig
from taipy.config._config import _Config
from taipy.data import PickleDataSource
from taipy.data.manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.job import JobNotDeletedException, NonExistingJob
from taipy.task import Task
from taipy.task.scheduler import TaskScheduler


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_config = None
    Config._applied_config = _Config.default_config()

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def multiply(nb1: float, nb2: float):
    sleep(0.1)
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_get_job():
    task_scheduler = TaskScheduler()
    task = _create_task(multiply)

    job_1 = task_scheduler.submit(task)
    assert task_scheduler.get_job(job_1.id) == job_1

    job_2 = task_scheduler.submit(task)
    assert job_1 != job_2
    assert task_scheduler.get_job(job_1.id) == job_1
    assert task_scheduler.get_job(job_2.id) == job_2


def test_get_latest_job():
    task_scheduler = TaskScheduler()
    task = _create_task(multiply)

    job_1 = task_scheduler.submit(task)
    assert task_scheduler.get_latest_job(task) == job_1

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = task_scheduler.submit(task)
    assert task_scheduler.get_latest_job(task) == job_2


def test_raise_on_job_unknown():
    task_scheduler = TaskScheduler()

    with pytest.raises(NonExistingJob):
        task_scheduler.get_job(JobId("Unknown"))


def test_get_jobs():
    task_scheduler = TaskScheduler()
    task = _create_task(multiply)

    job_1 = task_scheduler.submit(task)
    job_2 = task_scheduler.submit(task)

    assert task_scheduler.get_jobs() == [job_1, job_2]


def test_delete_job():
    task_scheduler = TaskScheduler()
    task = _create_task(multiply)

    job_1 = task_scheduler.submit(task)
    job_2 = task_scheduler.submit(task)

    task_scheduler.delete(job_1)

    assert task_scheduler.get_jobs() == [job_2]
    with pytest.raises(NonExistingJob):
        task_scheduler.get_job(job_1.id)


def test_raise_when_trying_to_delete_unfinished_job():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_scheduler = TaskScheduler(Config.set_job_config(parallel_execution=True))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = task_scheduler.submit(task)

        with pytest.raises(JobNotDeletedException):
            task_scheduler.delete(job)


def test_submit_task():
    task_scheduler = TaskScheduler()
    data_manager = task_scheduler.data_manager

    before_creation = datetime.now()
    sleep(0.1)
    task = _create_task(multiply)
    output_ds_id = task.output[f"{task.config_name}-output0"].id

    assert data_manager.get(output_ds_id).last_edition_date > before_creation
    assert data_manager.get(output_ds_id).job_ids == []
    assert data_manager.get(output_ds_id).is_ready_for_reading

    before_submission_creation = datetime.now()
    sleep(0.1)
    job = task_scheduler.submit(task)
    sleep(0.1)
    after_submission_creation = datetime.now()
    assert data_manager.get(output_ds_id).read() == 42
    assert data_manager.get(output_ds_id).last_edition_date > before_submission_creation
    assert data_manager.get(output_ds_id).last_edition_date < after_submission_creation
    assert data_manager.get(output_ds_id).job_ids == [job.id]
    assert data_manager.get(output_ds_id).is_ready_for_reading
    assert job.is_completed()


def test_submit_task_that_return_multiple_outputs():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    task_scheduler = TaskScheduler()

    with_tuple = _create_task(return_2tuple, 2)
    with_list = _create_task(return_list, 2)

    task_scheduler.submit(with_tuple)
    task_scheduler.submit(with_list)

    assert (
        with_tuple.output[f"{with_tuple.config_name}-output0"].read()
        == with_list.output[f"{with_list.config_name}-output0"].read()
        == 42
    )
    assert (
        with_tuple.output[f"{with_tuple.config_name}-output1"].read()
        == with_list.output[f"{with_list.config_name}-output1"].read()
        == 21
    )


def test_submit_task_returns_single_iterable_output():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    task_scheduler = TaskScheduler()
    task_with_tuple = _create_task(return_2tuple, 1)
    task_with_list = _create_task(return_list, 1)

    task_scheduler.submit(task_with_tuple)
    assert task_with_tuple.output[f"{task_with_tuple.config_name}-output0"].read() == (42, 21)
    task_scheduler.submit(task_with_list)
    assert task_with_list.output[f"{task_with_list.config_name}-output0"].read() == [42, 21]


def test_data_source_not_written_due_to_wrong_result_nb():
    def return_2tuple():
        return lambda nb1, nb2: (multiply(nb1, nb2), multiply(nb1, nb2) / 2)

    task_scheduler = TaskScheduler()
    task = _create_task(return_2tuple(), 3)

    job = task_scheduler.submit(task)
    assert task.output[f"{task.config_name}-output0"].read() == 0
    assert job.is_failed()


def test_submit_task_in_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_scheduler = TaskScheduler(Config.set_job_config(parallel_execution=True))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = task_scheduler.submit(task)
        assert task.output[f"{task.config_name}-output0"].read() == 0
        assert job.is_running()

    assert_true_after_10_second_max(job.is_completed)


def test_submit_task_multithreading_multiple_task():
    task_scheduler = TaskScheduler(Config.set_job_config(parallel_execution=True, nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = task_scheduler.submit(task_1)
            job_2 = task_scheduler.submit(task_2)

            assert task_1.output[f"{task_1.config_name}-output0"].read() == 0
            assert task_2.output[f"{task_2.config_name}-output0"].read() == 0
            assert job_1.is_running()
            assert job_2.is_running()

        assert_true_after_10_second_max(lambda: task_2.output[f"{task_2.config_name}-output0"].read() == 42)
        assert task_1.output[f"{task_1.config_name}-output0"].read() == 0
        assert job_1.is_running()
        assert job_2.is_completed()

    assert_true_after_10_second_max(lambda: task_1.output[f"{task_1.config_name}-output0"].read() == 42)
    assert task_2.output[f"{task_2.config_name}-output0"].read() == 42
    assert job_1.is_completed()
    assert job_2.is_completed()


def test_submit_task_multithreading_multiple_task_in_sync_way_to_check_job_status():
    task_scheduler = TaskScheduler(Config.set_job_config(parallel_execution=True, nb_of_workers=1))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = task_scheduler.submit(task_2)
            job_2 = task_scheduler.submit(task_1)

            assert task_1.output[f"{task_1.config_name}-output0"].read() == 0
            assert task_2.output[f"{task_2.config_name}-output0"].read() == 0
            assert job_1.is_running()
            assert job_2.is_pending()

        assert_true_after_10_second_max(lambda: task_2.output[f"{task_2.config_name}-output0"].read() == 42)
        assert task_1.output[f"{task_1.config_name}-output0"].read() == 0
        assert job_1.is_completed()
        assert job_2.is_running()

    assert_true_after_10_second_max(lambda: task_1.output[f"{task_1.config_name}-output0"].read() == 42)
    assert task_2.output[f"{task_2.config_name}-output0"].read() == 42
    assert job_1.is_completed()
    assert job_2.is_completed()


def test_blocked_task():
    data_manager = DataManager()
    task_scheduler = TaskScheduler(Config.set_job_config(parallel_execution=True))
    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    data_source_1 = PickleDataSource("foo", Scope.PIPELINE, DataSourceId("s1"), properties={"default_data": 1})
    data_source_2 = PickleDataSource("bar", Scope.PIPELINE, DataSourceId("s2"))
    data_source_3 = PickleDataSource("baz", Scope.PIPELINE, DataSourceId("s3"))
    data_manager.set(data_source_1)
    data_manager.set(data_source_2)
    data_manager.set(data_source_3)
    task_1 = Task("by_2", input=[data_source_1], function=partial(lock_multiply, lock_1, 2), output=[data_source_2])
    task_2 = Task("by_3", input=[data_source_2], function=partial(lock_multiply, lock_2, 3), output=[data_source_3])
    assert data_source_1.is_ready_for_reading  # Data source 1 is ready
    assert not data_source_2.is_ready_for_reading  # But data source 2 is not ready
    assert not data_source_3.is_ready_for_reading  # neither does data source 3

    assert len(task_scheduler.blocked_jobs) == 0
    job_2 = task_scheduler.submit(task_2)  # job 2 is submitted first
    assert job_2.is_blocked()  # since data source 2 is not up_to_date the job 2 is blocked
    assert len(task_scheduler.blocked_jobs) == 1
    with lock_2:
        with lock_1:
            job_1 = task_scheduler.submit(task_1)  # job 1 is submitted and locked
            assert task_scheduler.get_job(job_1.id).is_running()  # so it is still running
            assert not data_manager.get(data_source_2.id).is_ready_for_reading  # And data source 2 still not ready
            assert task_scheduler.get_job(job_2.id).is_blocked()  # the job_2 remains blocked
        assert_true_after_10_second_max(task_scheduler.get_job(job_1.id).is_completed)  # job1 unlocked and can complete
        assert data_manager.get(data_source_2.id).is_ready_for_reading  # Data source 2 becomes ready
        assert data_manager.get(data_source_2.id).read() == 2  # the data is computed and written
        assert task_scheduler.get_job(job_2.id).is_running()  # And job 2 can run
        assert len(task_scheduler.blocked_jobs) == 0
    assert_true_after_10_second_max(task_scheduler.get_job(job_2.id).is_completed)  # job 2 unlocked so it can complete
    assert data_manager.get(data_source_3.id).is_ready_for_reading  # Data source 3 becomes ready
    assert data_manager.get(data_source_3.id).read() == 6  # the data is computed and written


@patch("taipy.task.scheduler.task_scheduler.JobDispatcher")
def test_task_scheduler_create_synchronous_dispatcher(job_dispatcher):
    TaskScheduler(Config.set_job_config())
    job_dispatcher.assert_called_with(
        JobConfig.DEFAULT_PARALLEL_EXECUTION,
        JobConfig.DEFAULT_REMOTE_EXECUTION,
        JobConfig.DEFAULT_NB_OF_WORKERS,
        JobConfig.DEFAULT_HOSTNAME,
    )


@patch("taipy.task.scheduler.task_scheduler.JobDispatcher")
def test_task_scheduler_create_parallel_dispatcher(job_dispatcher):
    TaskScheduler(Config.set_job_config(parallel_execution=True, nb_of_workers=42))
    job_dispatcher.assert_called_with(True, JobConfig.DEFAULT_REMOTE_EXECUTION, 42, JobConfig.DEFAULT_HOSTNAME)


@patch("taipy.task.scheduler.task_scheduler.JobDispatcher")
def test_task_scheduler_create_remote_dispatcher(job_dispatcher):
    TaskScheduler(Config.set_job_config(remote_execution=True, nb_of_workers=42))
    job_dispatcher.assert_called_with(JobConfig.DEFAULT_PARALLEL_EXECUTION, True, 42, JobConfig.DEFAULT_HOSTNAME)


def _create_task(function, nb_outputs=1):
    output_ds_config_name = str(uuid.uuid4())
    input_ds = [
        DataManager().get_or_create(Config.add_data_source("input1", "in_memory", Scope.PIPELINE, default_data=21)),
        DataManager().get_or_create(Config.add_data_source("input2", "in_memory", Scope.PIPELINE, default_data=2)),
    ]
    output_ds = [
        DataManager().get_or_create(
            Config.add_data_source(f"{output_ds_config_name}-output{i}", "pickle", Scope.PIPELINE, default_data=0)
        )
        for i in range(nb_outputs)
    ]

    return Task(
        output_ds_config_name,
        input=input_ds,
        function=function,
        output=output_ds,
    )


def assert_true_after_10_second_max(assertion):
    start = datetime.now()
    while (datetime.now() - start).seconds < 10:
        sleep(0.1)  # Limit CPU usage
        if assertion():
            return
    assert assertion()
