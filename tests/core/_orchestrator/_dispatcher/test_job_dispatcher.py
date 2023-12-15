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

import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from unittest import mock
from unittest.mock import MagicMock

from pytest import raises

import taipy
from taipy.config.config import Config
from taipy.core import DataNodeId, JobId, TaskId
from taipy.core._orchestrator._dispatcher import _JobDispatcher
from taipy.core._orchestrator._dispatcher._development_job_dispatcher import _DevelopmentJobDispatcher
from taipy.core._orchestrator._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.task.task import Task
from tests.core.utils import assert_true_after_time


def nothing(*args):
    return

def create_scenario():
    dn_cfg = Config.configure_pickle_data_node("dn")
    t1_cfg = Config.configure_task("t1", nothing, [], [dn_cfg])
    sc_conf = Config.configure_scenario("scenario_cfg", [t1_cfg])
    return taipy.create_scenario(sc_conf)

def test_start_stop_is_running():
    dispatcher = _JobDispatcher(_OrchestratorFactory._orchestrator)
    dispatcher.start()
    assert dispatcher.is_running()
    dispatcher.stop()
    time.sleep(0.2)
    assert not dispatcher.is_running()


def test_can_execute():
    dispatcher = _JobDispatcher(_OrchestratorFactory._orchestrator)
    assert dispatcher._can_execute()
    dispatcher._nb_available_workers = 0
    assert not dispatcher._can_execute()
    dispatcher._nb_available_workers = -1
    assert not dispatcher._can_execute()
    dispatcher._nb_available_workers = 1
    assert dispatcher._can_execute()


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
            mck_2.assert_called_once_with(job.task) # this must be called to check if the job needs to run
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

            mck_1.assert_called_once_with(job) # This should be called to dispatch the job
            mck_2.assert_not_called()  # This should NOT be called since we force the execution anyway
            assert job.is_running()  # The job is not executed since the dispatch is mocked
            assert scenario.dn.edit_in_progress  # outputs must NOT have been unlocked because the disptach is mocked


def test_execute_jobs_synchronously():
    orchestrator = _OrchestratorFactory._build_orchestrator()
    orchestrator.jobs_to_run.put()
    execute_job_called = []
    def mock_execute_job(job):
        execute_job_called.append(job)

    dispatcher = _JobDispatcher(orchestrator)


######################################################################################################
def execute(lock):
    with lock:
        ...
    return None



def _error():
    raise RuntimeError("Something bad has happened")


def test_build_development_job_dispatcher():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()
    dispatcher = _OrchestratorFactory._dispatcher

    assert isinstance(dispatcher, _DevelopmentJobDispatcher)
    assert dispatcher._nb_available_workers == 1

    with raises(NotImplementedError):
        assert dispatcher.start()

    assert dispatcher.is_running()

    with raises(NotImplementedError):
        dispatcher.stop()


def test_build_standalone_job_dispatcher():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
    _OrchestratorFactory._build_dispatcher()
    dispatcher = _OrchestratorFactory._dispatcher

    assert not isinstance(dispatcher, _DevelopmentJobDispatcher)
    assert isinstance(dispatcher, _StandaloneJobDispatcher)
    assert isinstance(dispatcher._executor, ProcessPoolExecutor)
    assert dispatcher._nb_available_workers == 2
    assert_true_after_time(dispatcher.is_running)
    dispatcher.stop()
    dispatcher.join()
    assert_true_after_time(lambda: not dispatcher.is_running())


def test_can_execute_2_workers():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    output = list(_DataManager._bulk_get_or_create([Config.configure_data_node("input1", default_data=21)]).values())

    _OrchestratorFactory._build_dispatcher()

    task = Task(
        config_id="name",
        properties={},
        input=[],
        function=partial(execute, lock),
        output=output,
        id=task_id,
    )
    job_id = JobId("id1")
    job = Job(job_id, task, "submit_id", task.id)

    dispatcher = _StandaloneJobDispatcher(_OrchestratorFactory._orchestrator)

    with lock:
        assert dispatcher._can_execute()
        dispatcher._dispatch(job)
        assert dispatcher._can_execute()
        dispatcher._dispatch(job)
        assert not dispatcher._can_execute()

    assert_true_after_time(lambda: dispatcher._can_execute())


def test_can_execute_synchronous():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    task_id = TaskId("task_id1")
    task = Task(config_id="name", properties={}, input=[], function=print, output=[], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task_id, task._ID_PREFIX, task.config_id)
    job_id = JobId("id1")
    job = Job(job_id, task, submission.id, task.id)

    dispatcher = _OrchestratorFactory._dispatcher

    assert dispatcher._can_execute()
    dispatcher._dispatch(job)
    assert dispatcher._can_execute()


def test_exception_in_user_function():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    task = Task(config_id="name", properties={}, input=[], function=_error, output=[], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task_id, task._ID_PREFIX, task.config_id)
    job = Job(job_id, task, submission.id, task.id)

    dispatcher = _OrchestratorFactory._dispatcher
    dispatcher._dispatch(job)
    assert job.is_failed()
    assert 'RuntimeError("Something bad has happened")' in str(job.stacktrace[0])


def test_exception_in_writing_data():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    output = MagicMock()
    output.id = DataNodeId("output_id")
    output.config_id = "my_raising_datanode"
    output._is_in_cache = False
    output.write.side_effect = ValueError()
    task = Task(config_id="name", properties={}, input=[], function=print, output=[output], id=task_id)
    submission = _SubmissionManagerFactory._build_manager()._create(task_id, task._ID_PREFIX, task.config_id)
    job = Job(job_id, task, submission.id, task.id)

    dispatcher = _OrchestratorFactory._dispatcher

    with mock.patch("taipy.core.data._data_manager._DataManager._get") as get:
        get.return_value = output
        dispatcher._dispatch(job)
        assert job.is_failed()
        assert "node" in job.stacktrace[0]
