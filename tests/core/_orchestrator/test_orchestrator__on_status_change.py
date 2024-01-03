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
from random import random
from unittest import mock

import taipy
from taipy import Status, Job, JobId
from taipy.config import Config
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory


def nothing(*args, **kwargs):
    pass


def create_job(id, status):
    t_cfg = Config.configure_task("no_output", nothing, [], [])
    t = _TaskManagerFactory._build_manager()._bulk_get_or_create([t_cfg])
    job = Job(JobId(id), t[0], "", "")
    _JobManagerFactory._build_manager()._set(job)
    job.status = status
    return job


def create_job_from_task(id, task):
    job = Job(JobId(id), task, "s", task.id)
    _JobManagerFactory._build_manager()._set(job)
    return job


def create_scenario():
    # dn_0 --> t1 --> dn_1 --> t2 --> dn_2
    #  \
    #   \--> t3
    dn_0_cfg = Config.configure_pickle_data_node("dn_0")
    dn_1_cfg = Config.configure_pickle_data_node("dn_1")
    dn_2_cfg = Config.configure_pickle_data_node("dn_2")
    t1_cfg = Config.configure_task("t1", nothing, [dn_0_cfg], [dn_1_cfg])
    t2_cfg = Config.configure_task("t2", nothing, [dn_1_cfg], [dn_2_cfg])
    t3_cfg = Config.configure_task("t3", nothing, [dn_0_cfg], [])
    sc_conf = Config.configure_scenario("scenario_cfg", [t2_cfg, t1_cfg, t3_cfg])
    return taipy.create_scenario(sc_conf)


def test_on_status_change_on_running_job_does_nothing():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job_1_blocked = create_job("1_blocked", Status.BLOCKED)
    job_2_to_be_unblocked = create_job("to_be_unblocked", Status.BLOCKED)
    job_3_blocked = create_job("3_blocked", Status.BLOCKED)
    job_4_running = create_job("running_job", Status.RUNNING)
    orchestrator.blocked_jobs.append(job_1_blocked)
    orchestrator.blocked_jobs.append(job_2_to_be_unblocked)
    orchestrator.blocked_jobs.append(job_3_blocked)

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._is_blocked") as mck:
        orchestrator._on_status_change(job_4_running)

        mck.assert_not_called()
        assert job_1_blocked in orchestrator.blocked_jobs
        assert job_1_blocked.is_blocked()
        assert job_2_to_be_unblocked in orchestrator.blocked_jobs
        assert job_2_to_be_unblocked.is_blocked()
        assert job_3_blocked in orchestrator.blocked_jobs
        assert job_3_blocked.is_blocked()
        assert job_4_running.is_running()
        assert len(orchestrator.blocked_jobs) == 3
        assert orchestrator.jobs_to_run.qsize() == 0


def test_on_status_change_on_completed_job():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job_1_blocked = create_job("1_blocked", Status.BLOCKED)
    job_2_to_be_unblocked = create_job("to_be_unblocked", Status.BLOCKED)
    job_3_blocked = create_job("3_blocked", Status.BLOCKED)
    job_4_completed = create_job("completed_job", Status.COMPLETED)
    orchestrator.blocked_jobs.append(job_1_blocked)
    orchestrator.blocked_jobs.append(job_2_to_be_unblocked)
    orchestrator.blocked_jobs.append(job_3_blocked)

    def mck_is_blocked(job):
        if job.id == "to_be_unblocked":
            return False
        return True

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._is_blocked") as mck:
        mck.side_effect = mck_is_blocked
        orchestrator._on_status_change(job_4_completed)

        assert job_1_blocked in orchestrator.blocked_jobs
        assert job_1_blocked.is_blocked()
        assert job_2_to_be_unblocked not in orchestrator.blocked_jobs
        assert job_2_to_be_unblocked.is_pending()
        assert job_3_blocked in orchestrator.blocked_jobs
        assert job_3_blocked.is_blocked()
        assert job_4_completed.is_completed()
        assert len(orchestrator.blocked_jobs) == 2
        assert orchestrator.jobs_to_run.qsize() == 1
        assert orchestrator.jobs_to_run.get() == job_2_to_be_unblocked


def test_on_status_change_on_skipped_job():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job_1_blocked = create_job("1_blocked", Status.BLOCKED)
    job_2_to_be_unblocked = create_job("to_be_unblocked", Status.BLOCKED)
    job_3_blocked = create_job("3_blocked", Status.BLOCKED)
    job_4_skipped = create_job("skipped_job", Status.SKIPPED)
    orchestrator.blocked_jobs.append(job_1_blocked)
    orchestrator.blocked_jobs.append(job_2_to_be_unblocked)
    orchestrator.blocked_jobs.append(job_3_blocked)

    def mck_is_blocked(job):
        if job.id == "to_be_unblocked":
            return False
        return True

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._is_blocked") as mck:
        mck.side_effect = mck_is_blocked

        orchestrator._on_status_change(job_4_skipped)

        # Assert that when the status is skipped, the unblock jobs mechanism is executed
        assert job_1_blocked in orchestrator.blocked_jobs
        assert job_1_blocked.is_blocked()
        assert job_2_to_be_unblocked not in orchestrator.blocked_jobs
        assert job_2_to_be_unblocked.is_pending()
        assert job_3_blocked in orchestrator.blocked_jobs
        assert job_3_blocked.is_blocked()
        assert job_4_skipped.is_skipped()
        assert len(orchestrator.blocked_jobs) == 2
        assert orchestrator.jobs_to_run.qsize() == 1
        assert orchestrator.jobs_to_run.get() == job_2_to_be_unblocked


def test_on_status_change_on_failed_job():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    scenario = create_scenario()
    j1 = create_job_from_task("j1", scenario.t1)
    j1.status = Status.FAILED
    j2 = create_job_from_task("j2", scenario.t2)
    j2.status = Status.BLOCKED
    j3 = create_job_from_task("j3", scenario.t3)
    j3.status = Status.BLOCKED
    orchestrator.blocked_jobs.append(j2)
    orchestrator.blocked_jobs.append(j3)

    orchestrator._on_status_change(j1)

    # Assert that when the status is skipped, the unblock jobs mechanism is executed
    assert j1.is_failed()
    assert j2 not in orchestrator.blocked_jobs
    assert j2.is_abandoned()
    assert j3 in orchestrator.blocked_jobs
    assert j3.is_blocked()
    assert len(orchestrator.blocked_jobs) == 1
    assert orchestrator.jobs_to_run.qsize() == 0
