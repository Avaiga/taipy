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

from unittest import mock

import taipy
from taipy.config.config import Config
from taipy.core import JobId, TaskId
from taipy.core._orchestrator._dispatcher import _JobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def nothing(*args):
    return


def create_scenario():
    dn_cfg = Config.configure_pickle_data_node("dn")
    t1_cfg = Config.configure_task("t1", nothing, [], [dn_cfg])
    sc_conf = Config.configure_scenario("scenario_cfg", [t1_cfg])
    return taipy.create_scenario(sc_conf)


def test_execute_job():
    scenario = create_scenario()
    scenario.t1.skippable = True  # make the job skippable
    scenario.dn.lock_edit()  # lock output edit
    job = Job(JobId("id"), scenario.t1, "submit_id", TaskId("id"))
    _JobManagerFactory._build_manager()._set(job)
    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._dispatch") as mck_1:
        with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._needs_to_run") as mck_2:
            mck_2.return_value = True
            dispatcher = _JobDispatcher(_OrchestratorFactory._build_orchestrator())
            dispatcher._execute_job(job)

            mck_2.assert_called_once_with(job.task)  # This should be called to check if job needs to run
            mck_1.assert_called_once_with(job)
            assert job.is_running()  # The job is not executed since the dispatch is mocked
            assert scenario.dn.edit_in_progress  # outputs must NOT have been unlocked because the disptach is mocked


def test_execute_job_to_skip():
    scenario = create_scenario()
    scenario.t1.skippable = True  # make the job skippable
    scenario.dn.lock_edit()  # lock output edit
    job = Job(JobId("id"), scenario.t1, "submit_id", TaskId("id"))
    _JobManagerFactory._build_manager()._set(job)

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._dispatch") as mck_1:
        with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._needs_to_run") as mck_2:
            mck_2.return_value = False
            _JobDispatcher(_OrchestratorFactory._build_orchestrator())._execute_job(job)

            assert job.is_skipped()
            mck_1.assert_not_called()  # The job is expecting to be skipped, so it must not be dispatched
            mck_2.assert_called_once_with(job.task)  # this must be called to check if the job needs to run
            assert not scenario.dn.edit_in_progress  # outputs must have been unlocked


def test_execute_job_skippable_with_force():
    scenario = create_scenario()
    scenario.t1.skippable = True  # make the job skippable
    scenario.dn.lock_edit()  # lock output edit
    job = Job(JobId("id"), scenario.t1, "submit_id", TaskId("id"), force=True)
    _JobManagerFactory._build_manager()._set(job)

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._dispatch") as mck_1:
        with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._needs_to_run") as mck_2:
            mck_2.return_value = False
            dispatcher = _JobDispatcher(_OrchestratorFactory._orchestrator)
            dispatcher._execute_job(job)

            mck_1.assert_called_once_with(job)  # This should be called to dispatch the job
            mck_2.assert_not_called()  # This should NOT be called since we force the execution anyway
            assert job.is_running()  # The job is not executed since the dispatch is mocked
            assert scenario.dn.edit_in_progress  # outputs must NOT have been unlocked because the disptach is mocked


def test_execute_jobs_synchronously():
    task = Task("config_id", {}, nothing, [], [])
    _TaskManagerFactory._build_manager()._set(task)
    job_1 = Job(JobId("job1"), task, "s_id", task.id)
    job_2 = Job(JobId("job2"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._set(job_1)
    _JobManagerFactory._build_manager()._set(job_2)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    orchestrator.jobs_to_run.put(job_1)
    orchestrator.jobs_to_run.put(job_2)

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._execute_job") as mck:
        _JobDispatcher(orchestrator)._execute_jobs_synchronously()
        assert mck.call_count == 2
        mck.assert_called_with(job_2)
