# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
import time
from concurrent.futures import ProcessPoolExecutor, Future
from unittest import mock

from taipy import Config
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.core import JobId
from taipy.core._orchestrator._dispatcher import _StandaloneJobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task
from tests.core._orchestrator._dispatcher.mock_standalone_dispatcher import MockStandaloneDispatcher
from tests.core.utils import assert_true_after_time


def nothing(*args):
    return


def create_task():
    task = Task("config_id", {}, nothing, [], [])
    _TaskManagerFactory._build_manager()._set(task)
    return task


def test_init_default():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job_dispatcher = _StandaloneJobDispatcher(orchestrator)

    assert job_dispatcher.orchestrator == orchestrator
    assert job_dispatcher.lock == orchestrator.lock
    assert job_dispatcher._nb_available_workers == 1
    assert isinstance(job_dispatcher._executor, ProcessPoolExecutor)


def test_init_with_nb_workers():
    Config.configure_job_executions(max_nb_of_workers=2)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job_dispatcher = _StandaloneJobDispatcher(orchestrator)

    assert job_dispatcher._nb_available_workers == 2


def test_dispatch_job():
    task = create_task()
    job = Job(JobId("job"), task, "s_id", task.id)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    dispatcher = MockStandaloneDispatcher(orchestrator)

    dispatcher._dispatch(job)

    # test that the job execution is submitted to the executor
    assert len(dispatcher.dispatch_calls) == 1
    assert len(dispatcher._executor.submit_called) == 1
    submit_first_call = dispatcher._executor.submit_called[0]
    assert submit_first_call[0].job_id == job.id
    assert submit_first_call[0].task == task
    assert submit_first_call[1] == ()
    assert submit_first_call[2]["config_as_string"] == _TomlSerializer()._serialize(Config._applied_config)

    # test that the proc of the job is added to the list of dispatched jobs
    assert len(dispatcher.set_dispatch_processes_calls) == 1
    assert dispatcher.set_dispatch_processes_calls[0][0] == job.id
    assert dispatcher.set_dispatch_processes_calls[0][1] == dispatcher._executor.f[0]

    # test that the worker is released after the job is done
    assert len(dispatcher.release_worker_calls) == 1

    # test that the job status is updated after execution on future
    assert len(dispatcher.update_job_status_from_future_calls) == 1
    assert dispatcher.update_job_status_from_future_calls[0][0] == job
    assert dispatcher.update_job_status_from_future_calls[0][1] == dispatcher._executor.f[0]


def test_release_worker():
    dispatcher = _StandaloneJobDispatcher(_OrchestratorFactory._orchestrator)

    assert dispatcher._nb_available_workers == 1
    dispatcher._release_worker(None)
    assert dispatcher._nb_available_workers == 2
    dispatcher._release_worker(None)
    assert dispatcher._nb_available_workers == 3


def test_update_job_status_from_future():
    task = create_task()
    job = Job(JobId("job"), task, "s_id", task.id)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    dispatcher = _StandaloneJobDispatcher(orchestrator)
    ft = Future()
    ft.set_result(None)
    dispatcher. _set_dispatched_processes(job.id, ft) # the job is dispatched to a process

    dispatcher._update_job_status_from_future(job, ft)

    assert len(dispatcher._dispatched_processes) == 0  # the job process is not stored anymore
    assert job.is_completed()


def test_run():
    task = create_task()
    job_1 = Job(JobId("job1"), task, "s_id", task.id)
    job_2 = Job(JobId("job2"), task, "s_id", task.id)
    job_3 = Job(JobId("job3"), task, "s_id", task.id)
    job_4 = Job(JobId("job4"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._set(job_1)
    _JobManagerFactory._build_manager()._set(job_2)
    _JobManagerFactory._build_manager()._set(job_3)
    _JobManagerFactory._build_manager()._set(job_4)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    orchestrator.jobs_to_run.put(job_1)
    orchestrator.jobs_to_run.put(job_2)
    orchestrator.jobs_to_run.put(job_3)
    orchestrator.jobs_to_run.put(job_4)

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher._execute_job") as mck:
        dispatcher = _StandaloneJobDispatcher(orchestrator)
        dispatcher.start()
        assert_true_after_time(lambda: mck.call_count == 4, msg="The 4 jobs were not dequeued.", time=5)
        dispatcher.stop()
        mck.assert_called_with(job_4)
