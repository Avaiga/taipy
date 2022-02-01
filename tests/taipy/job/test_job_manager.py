import glob
import multiprocessing
import os
import uuid
from time import sleep

import pytest

from taipy.common.alias import JobId
from taipy.config import Config
from taipy.config._config import _Config
from taipy.data.manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.job import JobNotDeletedException, NonExistingJob
from taipy.scheduler.scheduler import Scheduler
from taipy.task.manager import TaskManager


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
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
    scheduler = Scheduler()
    job_manager = scheduler.job_manager
    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    assert job_manager.get(job_1.id) == job_1

    job_2 = scheduler.submit_task(task)
    assert job_1 != job_2
    assert job_manager.get(job_1.id).id == job_1.id
    assert job_manager.get(job_2.id).id == job_2.id


def test_get_latest_job():
    scheduler = Scheduler()
    job_manager = scheduler.job_manager
    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    assert job_manager.get_latest_job(task) == job_1

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = scheduler.submit_task(task)
    assert job_manager.get_latest_job(task).id == job_2.id


def test_raise_on_job_unknown():
    scheduler = Scheduler()
    job_manager = scheduler.job_manager

    with pytest.raises(NonExistingJob):
        job_manager.get(JobId("Unknown"))


def test_get_jobs():
    scheduler = Scheduler()
    job_manager = scheduler.job_manager

    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    job_2 = scheduler.submit_task(task)

    assert {job.id for job in job_manager.get_all()} == {job_1.id, job_2.id}


def test_delete_job():
    scheduler = Scheduler()
    job_manager = scheduler.job_manager
    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    job_2 = scheduler.submit_task(task)

    job_manager.delete(job_1)

    assert [job.id for job in job_manager.get_all()] == [job_2.id]
    with pytest.raises(NonExistingJob):
        job_manager.get(job_1.id)


def test_raise_when_trying_to_delete_unfinished_job():
    m = multiprocessing.Manager()
    lock = m.Lock()

    scheduler = Scheduler(Config.set_job_config(nb_of_workers=2))
    job_manager = scheduler.job_manager

    def inner_lock_multiply(nb1: float, nb2: float):
        with lock:
            return multiply(nb1, nb2)

    task = _create_task(inner_lock_multiply)

    with lock:
        job = scheduler.submit_task(task)

        with pytest.raises(JobNotDeletedException):
            job_manager.delete(job)


def _create_task(function, nb_outputs=1):
    output_ds_config_name = str(uuid.uuid4())
    input1_ds_config = Config.add_data_node("input1", "in_memory", Scope.PIPELINE, default_data=21)
    DataManager().get_or_create(input1_ds_config)
    input2_ds_config = Config.add_data_node("input2", "in_memory", Scope.PIPELINE, default_data=2)
    DataManager().get_or_create(input2_ds_config)
    output_ds_configs = [
        Config.add_data_node(f"{output_ds_config_name}-output{i}", "pickle", Scope.PIPELINE, default_data=0)
        for i in range(nb_outputs)
    ]
    [DataManager().get_or_create(cfg) for cfg in output_ds_configs]
    task_config = Config.add_task(
        output_ds_config_name, [input1_ds_config, input2_ds_config], function, output_ds_configs
    )
    return TaskManager().get_or_create(task_config)
