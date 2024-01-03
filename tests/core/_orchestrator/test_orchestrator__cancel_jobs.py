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
from taipy import Status, Job, JobId
from taipy.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory


def nothing(*args, **kwargs):
    pass


def create_job(status):
    t_cfg = Config.configure_task("no_output", nothing, [], [])
    t = _TaskManagerFactory._build_manager()._bulk_get_or_create([t_cfg])
    job = Job(JobId("foo"), t[0], "", "")
    _JobManagerFactory._build_manager()._set(job)
    job.status = status
    return job


def create_scenario():
    # dn_0 --> t1 --> dn_1 --> t2 --> dn_2 --> t3 --> dn_3
    #                  \
    #                   \--> t2_bis
    dn_0 = Config.configure_data_node("dn_0", default_data=0)
    dn_1 = Config.configure_data_node("dn_1")
    dn_2 = Config.configure_data_node("dn_2")
    dn_3 = Config.configure_data_node("dn_3")
    t1 = Config.configure_task("t1", nothing, [dn_0], [dn_1])
    t2 = Config.configure_task("t2", nothing, [dn_1], [dn_2])
    t3 = Config.configure_task("t3", nothing, [dn_2], [dn_3])
    t2_bis = Config.configure_task("t2bis", nothing, [dn_1], [])
    sc_conf = Config.configure_scenario("scenario", [t1, t2, t3, t2_bis])
    return taipy.create_scenario(sc_conf)


def test_cancel_job_no_subsequent_jobs():
    job = create_job(Status.PENDING)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert job.is_canceled()


def test_cancel_job_with_subsequent_blocked_jobs():
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job1 = orchestrator._lock_dn_output_and_create_job(scenario.t1, "s_id", "e_id")
    job2 = orchestrator._lock_dn_output_and_create_job(scenario.t2, "s_id", "e_id")
    job3 = orchestrator._lock_dn_output_and_create_job(scenario.t3, "s_id", "e_id")
    job2bis = orchestrator._lock_dn_output_and_create_job(scenario.t2bis, "s_id", "e_id")
    job1.pending()
    job2.blocked()
    job3.blocked()
    job2bis.blocked()
    orchestrator.blocked_jobs = [job2, job3, job2bis]

    orchestrator.cancel_job(job1)

    assert job1.is_canceled()
    assert job2.is_abandoned()
    assert job3.is_abandoned()
    assert job2bis.is_abandoned()
    assert not scenario.dn_0.edit_in_progress
    assert not scenario.dn_1.edit_in_progress
    assert not scenario.dn_2.edit_in_progress
    assert not scenario.dn_3.edit_in_progress
    assert orchestrator.blocked_jobs == []


def test_cancel_job_with_subsequent_jobs_and_parallel_jobs():
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job1 = orchestrator._lock_dn_output_and_create_job(scenario.t1, "s_id", "e_id")
    job2 = orchestrator._lock_dn_output_and_create_job(scenario.t2, "s_id", "e_id")
    job3 = orchestrator._lock_dn_output_and_create_job(scenario.t3, "s_id", "e_id")
    job2bis = orchestrator._lock_dn_output_and_create_job(scenario.t2bis, "s_id", "e_id")
    job1.completed()

    job2.running()
    job3.blocked()
    job2bis.pending()
    orchestrator.blocked_jobs = [job3]

    orchestrator.cancel_job(job2)

    assert job1.is_completed()
    assert job2.is_canceled()
    assert job3.is_abandoned()
    assert job2bis.is_pending()
    assert not scenario.dn_2.edit_in_progress
    assert not scenario.dn_3.edit_in_progress
    assert orchestrator.blocked_jobs == []


def test_cancel_blocked_job_with_subsequent_blocked_jobs():
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job1 = orchestrator._lock_dn_output_and_create_job(scenario.t1, "s_id", "e_id")
    job2 = orchestrator._lock_dn_output_and_create_job(scenario.t2, "s_id", "e_id")
    job3 = orchestrator._lock_dn_output_and_create_job(scenario.t3, "s_id", "e_id")
    job2bis = orchestrator._lock_dn_output_and_create_job(scenario.t2bis, "s_id", "e_id")
    job1.blocked()
    job2.blocked()
    job3.blocked()
    job2bis.blocked()
    orchestrator.blocked_jobs = [job2, job3, job2bis]

    orchestrator.cancel_job(job1)

    assert job1.is_canceled()
    assert job2.is_abandoned()
    assert job3.is_abandoned()
    assert job2bis.is_abandoned()
    assert not scenario.dn_0.edit_in_progress
    assert not scenario.dn_1.edit_in_progress
    assert not scenario.dn_2.edit_in_progress
    assert not scenario.dn_3.edit_in_progress
    assert orchestrator.blocked_jobs == []


def test_cancel_failed_job():
    job = create_job(Status.FAILED)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert not job.is_canceled()
    assert job.is_failed()


def test_cancel_abandoned_job():
    job = create_job(Status.ABANDONED)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert not job.is_canceled()
    assert job.is_abandoned()


def test_cancel_canceled_job():
    job = create_job(Status.CANCELED)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert job.is_canceled()


def test_cancel_completed_job():
    job = create_job(Status.COMPLETED)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert job.is_completed()


def test_cancel_skipped_job():
    job = create_job(Status.SKIPPED)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator.cancel_job(job)

    assert job.is_skipped()
