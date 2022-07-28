# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import glob
import multiprocessing
import os
import random
import string
from datetime import datetime
from functools import partial
from time import sleep

import pytest

from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core.common.alias import JobId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import JobNotDeletedException
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config import JobConfig
from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope
from tests.core import utils


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
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_get_job():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task = _create_task(multiply, name="get_job")

    job_1 = _Scheduler.submit_task(task, "submit_id_1")
    assert _JobManager._get(job_1.id) == job_1

    job_2 = _Scheduler.submit_task(task, "submit_id_2")
    assert job_1 != job_2
    assert _JobManager._get(job_1.id).id == job_1.id
    assert _JobManager._get(job_2.id).id == job_2.id


def test_get_latest_job():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task = _create_task(multiply, name="get_latest_job")
    task_2 = _create_task(multiply, name="get_latest_job_2")

    job_1 = _Scheduler.submit_task(task, "submit_id_1")
    assert _JobManager._get_latest(task) == job_1
    assert _JobManager._get_latest(task_2) is None

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = _Scheduler.submit_task(task_2, "submit_id_2")
    assert _JobManager._get_latest(task).id == job_1.id
    assert _JobManager._get_latest(task_2).id == job_2.id

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_1_bis = _Scheduler.submit_task(task, "submit_id_1_bis")
    assert _JobManager._get_latest(task).id == job_1_bis.id
    assert _JobManager._get_latest(task_2).id == job_2.id


def test_get_job_unknown():
    assert _JobManager._get(JobId("Unknown")) is None


def test_get_jobs():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task = _create_task(multiply, name="get_all_jobs")

    job_1 = _Scheduler.submit_task(task, "submit_id_1")
    job_2 = _Scheduler.submit_task(task, "submit_id_2")

    assert {job.id for job in _JobManager._get_all()} == {job_1.id, job_2.id}


def test_delete_job():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task = _create_task(multiply, name="delete_job")

    job_1 = _Scheduler.submit_task(task, "submit_id_1")
    job_2 = _Scheduler.submit_task(task, "submit_id_2")

    _JobManager._delete(job_1)

    assert [job.id for job in _JobManager._get_all()] == [job_2.id]
    assert _JobManager._get(job_1.id) is None


m = multiprocessing.Manager()
lock = m.Lock()


def inner_lock_multiply(nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_raise_when_trying_to_delete_unfinished_job():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, nb_of_workers=2)
    _Scheduler._update_job_config()
    task = _create_task(inner_lock_multiply, name="delete_unfinished_job")
    with lock:
        job = _Scheduler.submit_task(task, "submit_id")
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job)
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job, force=False)
    utils.assert_true_after_1_minute_max(job.is_completed)
    _JobManager._delete(job)


def test_force_deleting_unfinished_job():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, nb_of_workers=2)
    _Scheduler._update_job_config()
    task = _create_task(inner_lock_multiply, name="delete_unfinished_job")
    with lock:
        job = _Scheduler.submit_task(task, "submit_id")
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job, force=False)
        _JobManager._delete(job, force=True)
    assert _JobManager._get(job.id) is None


def test_cancel_single_job():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, nb_of_workers=2)
    _Scheduler._update_job_config()
    task = _create_task(inner_lock_multiply, name="delete_unfinished_job")

    assert _Scheduler._dispatcher._nb_available_workers == 2

    with lock:
        job = _Scheduler.submit_task(task, "submit_id")

        assert job.is_running()
        assert len(_Scheduler._processes) == 1
        _JobManager._cancel(job.id)
        assert job.is_cancelled()
        assert len(_Scheduler._processes) == 0
    assert job.is_cancelled()
    wait_120_second_max_on_nb_of_workers(2)
    assert _Scheduler._dispatcher._nb_available_workers == 2


def wait_120_second_max_on_nb_of_workers(nb_of_workers):
    start = datetime.now()
    while (datetime.now() - start).seconds < 120:
        sleep(0.1)  # Limit CPU usage
        if _Scheduler._dispatcher._nb_available_workers == nb_of_workers:
            return
    assert _Scheduler._dispatcher._nb_available_workers == nb_of_workers


def test_cancel_subsequent_jobs():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, nb_of_workers=1)
    _Scheduler._update_job_config()

    m = multiprocessing.Manager()
    lock_1 = m.Lock()

    dn_1 = InMemoryDataNode("dn_config_1", Scope.PIPELINE, properties={"default_data": 1})
    dn_2 = InMemoryDataNode("dn_config_2", Scope.PIPELINE, properties={"default_data": 2})
    dn_3 = InMemoryDataNode("dn_config_3", Scope.PIPELINE, properties={"default_data": 3})
    dn_4 = InMemoryDataNode("dn_config_4", Scope.PIPELINE, properties={"default_data": 4})

    task_1 = Task("task_config_1", partial(lock_multiply, lock_1), [dn_1, dn_2], [dn_3], id="task_1")
    task_2 = Task("task_config_2", multiply, [dn_1, dn_3], [dn_4], id="task_2")
    task_3 = Task("task_config_3", print, [dn_4], id="task_3")

    _DataManager._set(dn_1)
    _DataManager._set(dn_2)
    _DataManager._set(dn_3)
    _DataManager._set(dn_4)

    with lock_1:
        submit_id_1 = "submit_1"
        job_1 = _Scheduler.submit_task(task_1, submit_id=submit_id_1)
        job_2 = _Scheduler.submit_task(task_2, submit_id=submit_id_1)
        job_3 = _Scheduler.submit_task(task_3, submit_id=submit_id_1)

        assert job_1.is_running()
        assert job_2.is_blocked()
        assert job_3.is_blocked()
        assert len(_Scheduler.blocked_jobs) == 2
        assert _Scheduler.jobs_to_run.qsize() == 0

        submit_id_2 = "submit_2"
        job_4 = _Scheduler.submit_task(task_1, submit_id=submit_id_2)
        job_5 = _Scheduler.submit_task(task_2, submit_id=submit_id_2)
        job_6 = _Scheduler.submit_task(task_3, submit_id=submit_id_2)

        assert job_4.is_pending()
        assert job_5.is_blocked()
        assert job_6.is_blocked()
        assert _Scheduler.jobs_to_run.qsize() == 1
        assert len(_Scheduler.blocked_jobs) == 4

        _JobManager._cancel(job_4)
        assert job_4.is_cancelled()
        assert job_5.is_abandoned()
        assert job_6.is_abandoned()
        assert _Scheduler.jobs_to_run.qsize() == 0
        assert len(_Scheduler.blocked_jobs) == 2

        _JobManager._cancel(job_1)
        assert job_1.is_cancelled()
        assert job_2.is_abandoned()
        assert job_3.is_abandoned()

    assert job_1.is_cancelled()
    assert job_2.is_abandoned()
    assert job_3.is_abandoned()
    assert job_4.is_cancelled()
    assert job_5.is_abandoned()
    assert job_6.is_abandoned()
    assert _Scheduler.jobs_to_run.qsize() == 0


def _create_task(function, nb_outputs=1, name=None):
    input1_dn_config = Config.configure_data_node("input1", "pickle", Scope.PIPELINE, default_data=21)
    input2_dn_config = Config.configure_data_node("input2", "pickle", Scope.PIPELINE, default_data=2)
    output_dn_configs = [
        Config.configure_data_node(f"output{i}", "pickle", Scope.PIPELINE, default_data=0) for i in range(nb_outputs)
    ]
    _DataManager._bulk_get_or_create([cfg for cfg in output_dn_configs])
    name = name or "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    task_config = Config.configure_task(
        name,
        function,
        [input1_dn_config, input2_dn_config],
        output_dn_configs,
    )
    return _TaskManager._bulk_get_or_create([task_config])[0]
