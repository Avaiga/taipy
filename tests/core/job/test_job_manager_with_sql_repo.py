# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import multiprocessing
import random
import string
from functools import partial
from time import sleep

import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core import Task
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.data import InMemoryDataNode
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.exceptions.exceptions import JobNotDeletedException
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job_id import JobId
from taipy.core.job.status import Status
from taipy.core.task._task_manager import _TaskManager
from tests.core.utils import assert_true_after_time


def multiply(nb1: float, nb2: float):
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1 or 1, nb2 or 2)


def test_create_jobs(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task = _create_task(multiply, name="get_job")

    job_1 = _JobManager._create(task, [print], "submit_id", "secnario_id", True)
    assert _JobManager._get(job_1.id) == job_1
    assert job_1.is_submitted()
    assert task.config_id in job_1.id
    assert job_1.task.id == task.id
    assert job_1.submit_id == "submit_id"
    assert job_1.submit_entity_id == "secnario_id"
    assert job_1.force

    job_2 = _JobManager._create(task, [print], "submit_id_1", "secnario_id", False)
    assert _JobManager._get(job_2.id) == job_2
    assert job_2.is_submitted()
    assert task.config_id in job_2.id
    assert job_2.task.id == task.id
    assert job_2.submit_id == "submit_id_1"
    assert job_2.submit_entity_id == "secnario_id"
    assert not job_2.force


def test_get_job(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task = _create_task(multiply, name="get_job")

    job_1 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    assert _JobManager._get(job_1.id) == job_1
    assert _JobManager._get(job_1.id).submit_entity_id == task.id

    job_2 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    assert job_1 != job_2
    assert _JobManager._get(job_1.id).id == job_1.id
    assert _JobManager._get(job_2.id).id == job_2.id
    assert _JobManager._get(job_2.id).submit_entity_id == task.id


def test_get_latest_job(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task = _create_task(multiply, name="get_latest_job")
    task_2 = _create_task(multiply, name="get_latest_job_2")

    job_1 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    assert _JobManager._get_latest(task) == job_1
    assert _JobManager._get_latest(task_2) is None

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_2 = _OrchestratorFactory._orchestrator.submit_task(task_2).jobs[0]
    assert _JobManager._get_latest(task).id == job_1.id
    assert _JobManager._get_latest(task_2).id == job_2.id

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    job_1_bis = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    assert _JobManager._get_latest(task).id == job_1_bis.id
    assert _JobManager._get_latest(task_2).id == job_2.id


def test_get_job_unknown(init_sql_repo):
    assert _JobManager._get(JobId("Unknown")) is None


def test_get_jobs(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task = _create_task(multiply, name="get_all_jobs")

    job_1 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    job_2 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]

    assert {job.id for job in _JobManager._get_all()} == {job_1.id, job_2.id}


def test_delete_job(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task = _create_task(multiply, name="delete_job")

    job_1 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]
    job_2 = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]

    _JobManager._delete(job_1)

    assert [job.id for job in _JobManager._get_all()] == [job_2.id]
    assert _JobManager._get(job_1.id) is None


def test_raise_when_trying_to_delete_unfinished_job(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=3)

    dnm = _DataManagerFactory._build_manager()
    dn_1 = InMemoryDataNode("dn_config_1", Scope.SCENARIO, properties={"default_data": 1})
    dnm._set(dn_1)
    dn_2 = InMemoryDataNode("dn_config_2", Scope.SCENARIO, properties={"default_data": 2})
    dnm._set(dn_2)
    dn_3 = InMemoryDataNode("dn_config_3", Scope.SCENARIO)
    dnm._set(dn_3)
    proc_manager = multiprocessing.Manager()
    lock = proc_manager.Lock()
    task = Task("task_cfg", {}, partial(lock_multiply, lock), [dn_1, dn_2], [dn_3], id="raise_when_delete_unfinished")
    dispatcher = _OrchestratorFactory._build_dispatcher()

    with lock:
        job = _OrchestratorFactory._orchestrator.submit_task(task)._jobs[0]
        assert_true_after_time(lambda: len(dispatcher._dispatched_processes) == 1)
        assert_true_after_time(job.is_running)
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job)
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job, force=False)
    assert_true_after_time(job.is_completed)
    _JobManager._delete(job)


def test_force_deleting_unfinished_job(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock = m.Lock()
    dnm = _DataManagerFactory._build_manager()
    dn_1 = InMemoryDataNode("dn_config_1", Scope.SCENARIO, properties={"default_data": 1})
    dnm._set(dn_1)
    dn_2 = InMemoryDataNode("dn_config_2", Scope.SCENARIO, properties={"default_data": 2})
    dnm._set(dn_2)
    dn_3 = InMemoryDataNode("dn_config_3", Scope.SCENARIO)
    dnm._set(dn_3)
    task_1 = Task(
        "task_config_1", {}, partial(lock_multiply, lock), [dn_1, dn_2], [dn_3], id="delete_force_unfinished_job"
    )
    reference_last_edit_date = dn_3.last_edit_date
    _OrchestratorFactory._build_dispatcher()
    with lock:
        job = _OrchestratorFactory._orchestrator.submit_task(task_1)._jobs[0]
        assert_true_after_time(job.is_running)
        with pytest.raises(JobNotDeletedException):
            _JobManager._delete(job, force=False)
        _JobManager._delete(job, force=True)
    assert _JobManager._get(job.id) is None
    assert_true_after_time(lambda: reference_last_edit_date != dn_3.last_edit_date)


def test_is_deletable(init_sql_repo):
    assert len(_JobManager._get_all()) == 0
    task = _create_task(print, 0, "task")
    job = _OrchestratorFactory._orchestrator.submit_task(task).jobs[0]

    assert job.is_completed()
    assert _JobManager._is_deletable(job)
    assert _JobManager._is_deletable(job.id)

    job.abandoned()
    assert job.is_abandoned()
    assert _JobManager._is_deletable(job)
    assert _JobManager._is_deletable(job.id)

    job.canceled()
    assert job.is_canceled()
    assert _JobManager._is_deletable(job)
    assert _JobManager._is_deletable(job.id)

    job.failed()
    assert job.is_failed()
    assert _JobManager._is_deletable(job)
    assert _JobManager._is_deletable(job.id)

    job.skipped()
    assert job.is_skipped()
    assert _JobManager._is_deletable(job)
    assert _JobManager._is_deletable(job.id)

    job.blocked()
    assert job.is_blocked()
    assert not _JobManager._is_deletable(job)
    assert not _JobManager._is_deletable(job.id)

    job.running()
    assert job.is_running()
    assert not _JobManager._is_deletable(job)
    assert not _JobManager._is_deletable(job.id)

    job.pending()
    assert job.is_pending()
    assert not _JobManager._is_deletable(job)
    assert not _JobManager._is_deletable(job.id)

    job.status = Status.SUBMITTED
    assert job.is_submitted()
    assert not _JobManager._is_deletable(job)
    assert not _JobManager._is_deletable(job.id)


def _create_task(function, nb_outputs=1, name=None):
    input1_dn_config = Config.configure_data_node("input1", scope=Scope.SCENARIO, default_data=21)
    input2_dn_config = Config.configure_data_node("input2", scope=Scope.SCENARIO, default_data=2)
    output_dn_configs = [
        Config.configure_data_node(f"output{i}", scope=Scope.SCENARIO, default_data=0) for i in range(nb_outputs)
    ]
    _DataManager._bulk_get_or_create({cfg for cfg in output_dn_configs})
    name = name or "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    task_config = Config.configure_task(
        id=name,
        function=function,
        input=[input1_dn_config, input2_dn_config],
        output=output_dn_configs,
    )
    return _TaskManager._bulk_get_or_create([task_config])[0]
