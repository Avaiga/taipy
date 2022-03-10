import glob
import multiprocessing
import os
import random
import string
import uuid
from time import sleep

import pytest

from taipy.core.common.alias import JobId
from taipy.core.config._config import _Config
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions.exceptions import JobNotDeletedException
from taipy.core.job._job_manager import _JobManager
from taipy.core.scheduler.scheduler import Scheduler
from taipy.core.task._task_manager import _TaskManager


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


def test_get_job():
    scheduler = Scheduler()
    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    assert _JobManager._get(job_1.id) == job_1

    job_2 = scheduler.submit_task(task)
    assert job_1 != job_2
    assert _JobManager._get(job_1.id).id == job_1.id
    assert _JobManager._get(job_2.id).id == job_2.id


def test_get_latest_job():
    scheduler = Scheduler()
    task = _create_task(multiply)
    task_2 = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    assert _JobManager._get_latest(task) == job_1
    assert _JobManager._get_latest(task_2) is None

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = scheduler.submit_task(task_2)
    assert _JobManager._get_latest(task).id == job_1.id
    assert _JobManager._get_latest(task_2).id == job_2.id

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_1_bis = scheduler.submit_task(task)
    assert _JobManager._get_latest(task).id == job_1_bis.id
    assert _JobManager._get_latest(task_2).id == job_2.id


def test_get_job_unknown():
    assert _JobManager._get(JobId("Unknown")) is None


def test_get_jobs():
    scheduler = Scheduler()

    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    job_2 = scheduler.submit_task(task)

    assert {job.id for job in _JobManager._get_all()} == {job_1.id, job_2.id}


def test_delete_job():
    scheduler = Scheduler()
    task = _create_task(multiply)

    job_1 = scheduler.submit_task(task)
    job_2 = scheduler.submit_task(task)

    _JobManager._delete(job_1)

    assert [job.id for job in _JobManager._get_all()] == [job_2.id]
    assert _JobManager._get(job_1.id) is None


m = multiprocessing.Manager()
lock = m.Lock()


def inner_lock_multiply(nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_raise_when_trying_to_delete_unfinished_job():

    scheduler = Scheduler(Config._set_job_config(nb_of_workers=2))

    task = _create_task(inner_lock_multiply)

    with lock:
        job = scheduler.submit_task(task)

        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job)


def _create_task(function, nb_outputs=1):
    output_dn_config_id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    input1_dn_config = Config._add_data_node("input1", "in_memory", Scope.PIPELINE, default_data=21)
    _DataManager._get_or_create(input1_dn_config)
    input2_dn_config = Config._add_data_node("input2", "in_memory", Scope.PIPELINE, default_data=2)
    _DataManager._get_or_create(input2_dn_config)
    output_dn_configs = [
        Config._add_data_node(f"{output_dn_config_id}_output{i}", "pickle", Scope.PIPELINE, default_data=0)
        for i in range(nb_outputs)
    ]
    [_DataManager._get_or_create(cfg) for cfg in output_dn_configs]
    task_config = Config._add_task(
        output_dn_config_id, function, [input1_dn_config, input2_dn_config], output_dn_configs
    )
    return _TaskManager._get_or_create(task_config)
