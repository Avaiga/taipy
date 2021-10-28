import glob
import multiprocessing
import os
import uuid
from functools import partial
from time import sleep

import pytest

from taipy.config import Config
from taipy.config.task_scheduler import TaskSchedulersRepository
from taipy.config.task_scheduler_serializer import TaskSchedulerSerializer
from taipy.data.manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.job import JobNotDeletedException, NonExistingJob
from taipy.task import JobId, Task
from taipy.task.scheduler import TaskScheduler


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._task_scheduler_serializer = TaskSchedulerSerializer()
    Config.task_scheduler_configs = TaskSchedulersRepository(Config._task_scheduler_serializer)

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def multiply(nb1: float, nb2: float):
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_scheduled_task():
    task_scheduler = TaskScheduler()
    task = _create_task(multiply)

    job = task_scheduler.submit(task)
    assert task.output[f"{task.config_name}-output0"].get() == 42
    assert job.is_completed()


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

    task_scheduler = TaskScheduler(Config.task_scheduler_configs.create(parallel_execution=True))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = task_scheduler.submit(task)

        with pytest.raises(JobNotDeletedException):
            task_scheduler.delete(job)


def test_scheduled_task_that_return_multiple_outputs():
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
        with_tuple.output[f"{with_tuple.config_name}-output0"].get()
        == with_list.output[f"{with_list.config_name}-output0"].get()
        == 42
    )
    assert (
        with_tuple.output[f"{with_tuple.config_name}-output1"].get()
        == with_list.output[f"{with_list.config_name}-output1"].get()
        == 21
    )


def test_scheduled_task_returns_single_iterable_output():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    task_scheduler = TaskScheduler()
    task_with_tuple = _create_task(return_2tuple, 1)
    task_with_list = _create_task(return_list, 1)

    task_scheduler.submit(task_with_tuple)
    assert task_with_tuple.output[f"{task_with_tuple.config_name}-output0"].get() == (42, 21)
    task_scheduler.submit(task_with_list)
    assert task_with_list.output[f"{task_with_list.config_name}-output0"].get() == [42, 21]


def test_data_source_not_written_due_to_wrong_result_nb():
    def return_2tuple():
        return lambda nb1, nb2: (multiply(nb1, nb2), multiply(nb1, nb2) / 2)

    task_scheduler = TaskScheduler()
    task = _create_task(return_2tuple(), 3)

    job = task_scheduler.submit(task)
    assert task.output[f"{task.config_name}-output0"].get() == 0
    assert job.is_failed()


def test_error_during_writing_data_source_don_t_stop_writing_on_other_data_source():
    task_scheduler = TaskScheduler()

    task = _create_task(lambda nb1, nb2: (42, 21), 2)
    DataManager().delete(task.output[f"{task.config_name}-output0"].id)
    task_scheduler.submit(task)

    assert task.output[f"{task.config_name}-output0"].get() == 0
    assert task.output[f"{task.config_name}-output1"].get() == 21


def test_scheduled_task_in_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_scheduler = TaskScheduler(Config.task_scheduler_configs.create(parallel_execution=True))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = task_scheduler.submit(task)
        assert task.output[f"{task.config_name}-output0"].get() == 0
        assert job.is_running()

    # task.lock_output.get()
    sleep(1)
    assert job.is_completed()


def test_scheduled_task_multithreading_multiple_task():
    task_scheduler = TaskScheduler(Config.task_scheduler_configs.create(parallel_execution=True))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = task_scheduler.submit(task_1)
            job_2 = task_scheduler.submit(task_2)

            assert task_1.output[f"{task_1.config_name}-output0"].get() == 0
            assert task_2.output[f"{task_2.config_name}-output0"].get() == 0
            assert job_1.is_running()
            assert job_2.is_running()

        sleep(1)
        assert task_1.output[f"{task_1.config_name}-output0"].get() == 0
        assert task_2.output[f"{task_2.config_name}-output0"].get() == 42
        assert job_1.is_running()
        assert job_2.is_completed()

    sleep(1)
    assert task_1.output[f"{task_1.config_name}-output0"].get(None) == 42
    assert task_2.output[f"{task_2.config_name}-output0"].get(None) == 42
    assert job_1.is_completed()
    assert job_2.is_completed()


def test_scheduled_task_multithreading_multiple_task_in_sync_way_to_check_job_status():
    task_scheduler = TaskScheduler(
        Config.task_scheduler_configs.create(parallel_execution=True, max_number_of_parallel_execution=1)
    )

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = task_scheduler.submit(task_2)
            job_2 = task_scheduler.submit(task_1)

            assert task_1.output[f"{task_1.config_name}-output0"].get() == 0
            assert task_2.output[f"{task_2.config_name}-output0"].get() == 0
            assert job_1.is_running()
            assert job_2.is_pending()

        sleep(1)
        assert task_1.output[f"{task_1.config_name}-output0"].get() == 0
        assert task_2.output[f"{task_2.config_name}-output0"].get() == 42
        assert job_1.is_completed()
        assert job_2.is_running()

    sleep(1)
    assert task_1.output[f"{task_1.config_name}-output0"].get(None) == 42
    assert task_2.output[f"{task_2.config_name}-output0"].get(None) == 42
    assert job_1.is_completed()
    assert job_2.is_completed()


def _create_task(function, nb_outputs=1):
    task_name = str(uuid.uuid4())
    input_ds = [
        DataManager().get_or_create(Config.data_source_configs.create("input1", "in_memory", Scope.PIPELINE, data=21)),
        DataManager().get_or_create(Config.data_source_configs.create("input2", "in_memory", Scope.PIPELINE, data=2)),
    ]
    output_ds = [
        DataManager().get_or_create(
            Config.data_source_configs.create(f"{task_name}-output{i}", "pickle", Scope.PIPELINE, data=0)
        )
        for i in range(nb_outputs)
    ]

    return Task(
        task_name,
        input=input_ds,
        function=function,
        output=output_ds,
    )
