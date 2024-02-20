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

from taipy.config import Config
from taipy.config.common.scope import Scope
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.submission._submission_manager import _SubmissionManager
from taipy.core.submission.submission_status import SubmissionStatus
from taipy.core.task.task import Task
from tests.core.utils import assert_true_after_time

# ################################  USER FUNCTIONS  ##################################


def multiply(nb1: float, nb2: float):
    sleep(0.1)
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def mult_by_2(n):
    return n * 2


@pytest.mark.orchestrator_dispatcher
def test_submit_task_multithreading_multiple_task():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    _OrchestratorFactory._build_dispatcher(force_restart=True)

    with lock_1:
        with lock_2:
            submission_1 = _Orchestrator.submit_task(task_1)
            job_1 = submission_1._jobs[0]
            submission_2 = _Orchestrator.submit_task(task_2)
            job_2 = submission_2._jobs[0]

            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
            assert_true_after_time(job_1.is_running)
            assert_true_after_time(job_2.is_running)
            assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 2)
            assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.RUNNING)
            assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.RUNNING)

        assert_true_after_time(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
        assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
        assert_true_after_time(job_2.is_completed)
        assert_true_after_time(job_1.is_running)
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
        assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.RUNNING)
        assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.COMPLETED)

    assert_true_after_time(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert_true_after_time(job_1.is_completed)
    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.COMPLETED)

    assert job_2.is_completed()
    assert submission_2.submission_status == SubmissionStatus.COMPLETED


@pytest.mark.orchestrator_dispatcher
def test_submit_submittable_multithreading_multiple_task():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    scenario = Scenario("scenario_config", [task_1, task_2], {})

    _OrchestratorFactory._build_dispatcher(force_restart=True)

    with lock_1:
        with lock_2:
            submission = _Orchestrator.submit(scenario)
            tasks_jobs = {job._task.id: job for job in submission._jobs}
            job_1 = tasks_jobs[task_1.id]
            job_2 = tasks_jobs[task_2.id]

            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
            assert_true_after_time(job_1.is_running)
            assert_true_after_time(job_2.is_running)
            assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 2)
            assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.RUNNING)
        assert_true_after_time(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
        assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
        assert_true_after_time(job_2.is_completed)
        assert_true_after_time(job_1.is_running)
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
        assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.RUNNING)

    assert_true_after_time(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert_true_after_time(job_1.is_completed)
    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert_true_after_time(job_2.is_completed)
    assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.COMPLETED)


@pytest.mark.orchestrator_dispatcher
def test_submit_task_multithreading_multiple_task_in_sync_way_to_check_job_status():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock_0 = m.Lock()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_0 = _create_task(partial(lock_multiply, lock_0))
    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    _OrchestratorFactory._build_dispatcher(force_restart=True)

    with lock_0:
        submission_0 = _Orchestrator.submit_task(task_0)
        job_0 = submission_0._jobs[0]
        assert_true_after_time(job_0.is_running)
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
        assert_true_after_time(
            lambda: _SubmissionManager._get(job_0.submit_id).submission_status == SubmissionStatus.RUNNING
        )
        with lock_1:
            with lock_2:
                assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
                assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
                submission_2 = _Orchestrator.submit_task(task_2)
                job_2 = submission_2._jobs[0]
                submission_1 = _Orchestrator.submit_task(task_1)
                job_1 = submission_1._jobs[0]
                assert_true_after_time(job_0.is_running)
                assert_true_after_time(job_1.is_pending)
                assert_true_after_time(job_2.is_running)
                assert_true_after_time(lambda: submission_0.submission_status == SubmissionStatus.RUNNING)
                assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.PENDING)
                assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.RUNNING)
                assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 2)

            assert_true_after_time(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert_true_after_time(job_0.is_running)
            assert_true_after_time(job_1.is_running)
            assert_true_after_time(job_2.is_completed)
            assert_true_after_time(lambda: submission_0.submission_status == SubmissionStatus.RUNNING)
            assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.RUNNING)
            assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.COMPLETED)
            assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 2)

        assert_true_after_time(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
        assert task_0.output[f"{task_0.config_id}_output0"].read() == 0
        assert_true_after_time(job_0.is_running)
        assert_true_after_time(job_1.is_completed)
        assert_true_after_time(lambda: submission_0.submission_status == SubmissionStatus.RUNNING)
        assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.COMPLETED)

        assert job_2.is_completed()
        assert submission_2.submission_status == SubmissionStatus.COMPLETED
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)

    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert task_0.output[f"{task_0.config_id}_output0"].read() == 42
    assert job_0.is_completed()
    assert job_1.is_completed()
    assert job_2.is_completed()
    assert _SubmissionManager._get(job_0.submit_id).submission_status == SubmissionStatus.COMPLETED
    assert _SubmissionManager._get(job_1.submit_id).submission_status == SubmissionStatus.COMPLETED
    assert _SubmissionManager._get(job_2.submit_id).submission_status == SubmissionStatus.COMPLETED


@pytest.mark.orchestrator_dispatcher
def test_blocked_task():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    foo_cfg = Config.configure_data_node("foo", default_data=1)
    bar_cfg = Config.configure_data_node("bar")
    baz_cfg = Config.configure_data_node("baz")

    _OrchestratorFactory._build_dispatcher(force_restart=True)

    dns = _DataManager._bulk_get_or_create([foo_cfg, bar_cfg, baz_cfg])
    foo = dns[foo_cfg]
    bar = dns[bar_cfg]
    baz = dns[baz_cfg]
    task_1 = Task("by_2", {}, partial(lock_multiply, lock_1, 2), [foo], [bar])
    task_2 = Task("by_3", {}, partial(lock_multiply, lock_2, 3), [bar], [baz])

    assert task_1.foo.is_ready_for_reading  # foo is ready
    assert not task_1.bar.is_ready_for_reading  # But bar is not ready
    assert not task_2.baz.is_ready_for_reading  # neither does baz

    assert len(_Orchestrator.blocked_jobs) == 0
    submission_2 = _Orchestrator.submit_task(task_2)
    job_2 = submission_2._jobs[0]  # job 2 is submitted first
    assert job_2.is_blocked()  # since bar is not is_valid the job 2 is blocked
    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert _SubmissionManager._get(job_2.submit_id).submission_status == SubmissionStatus.BLOCKED
    assert len(_Orchestrator.blocked_jobs) == 1
    with lock_2:
        with lock_1:
            submission_1 = _Orchestrator.submit_task(task_1)
            job_1 = submission_1._jobs[0]  # job 1 is submitted and locked
            assert_true_after_time(job_1.is_running)  # so it is still running
            assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
            assert not _DataManager._get(task_1.bar.id).is_ready_for_reading  # And bar still not ready
            assert_true_after_time(job_2.is_blocked)  # the job_2 remains blocked
            assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.RUNNING)
            assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.BLOCKED)
        assert_true_after_time(job_1.is_completed)  # job1 unlocked and can complete
        assert _DataManager._get(task_1.bar.id).is_ready_for_reading  # bar becomes ready
        assert _DataManager._get(task_1.bar.id).read() == 2  # the data is computed and written
        assert_true_after_time(job_2.is_running)  # And job 2 can start running
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
        assert len(_Orchestrator.blocked_jobs) == 0
        assert_true_after_time(lambda: submission_1.submission_status == SubmissionStatus.COMPLETED)
        assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.RUNNING)
    assert_true_after_time(job_2.is_completed)  # job 2 unlocked so it can complete
    assert _DataManager._get(task_2.baz.id).is_ready_for_reading  # baz becomes ready
    assert _DataManager._get(task_2.baz.id).read() == 6  # the data is computed and written
    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert submission_1.submission_status == SubmissionStatus.COMPLETED
    assert_true_after_time(lambda: submission_2.submission_status == SubmissionStatus.COMPLETED)


@pytest.mark.orchestrator_dispatcher
def test_blocked_submittable():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    foo_cfg = Config.configure_data_node("foo", default_data=1)
    bar_cfg = Config.configure_data_node("bar")
    baz_cfg = Config.configure_data_node("baz")

    _OrchestratorFactory._build_dispatcher(force_restart=True)

    dns = _DataManager._bulk_get_or_create([foo_cfg, bar_cfg, baz_cfg])
    foo = dns[foo_cfg]
    bar = dns[bar_cfg]
    baz = dns[baz_cfg]
    task_1 = Task("by_2", {}, partial(lock_multiply, lock_1, 2), [foo], [bar])
    task_2 = Task("by_3", {}, partial(lock_multiply, lock_2, 3), [bar], [baz])
    scenario = Scenario("scenario_config", [task_1, task_2], {})

    assert task_1.foo.is_ready_for_reading  # foo is ready
    assert not task_1.bar.is_ready_for_reading  # But bar is not ready
    assert not task_2.baz.is_ready_for_reading  # neither does baz

    assert len(_Orchestrator.blocked_jobs) == 0
    with lock_2:
        with lock_1:
            submission = _Orchestrator.submit(scenario)  # scenario is submitted
            tasks_jobs = {job._task.id: job for job in submission._jobs}
            job_1, job_2 = tasks_jobs[task_1.id], tasks_jobs[task_2.id]
            assert_true_after_time(job_1.is_running)  # job 1 is submitted and locked so it is still running
            assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
            assert not _DataManager._get(task_1.bar.id).is_ready_for_reading  # And bar still not ready
            assert_true_after_time(job_2.is_blocked)  # the job_2 remains blocked
            assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.RUNNING)
        assert_true_after_time(job_1.is_completed)  # job1 unlocked and can complete
        assert _DataManager._get(task_1.bar.id).is_ready_for_reading  # bar becomes ready
        assert _DataManager._get(task_1.bar.id).read() == 2  # the data is computed and written
        assert_true_after_time(job_2.is_running)  # And job 2 can start running
        assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 1)
        assert len(_Orchestrator.blocked_jobs) == 0
        assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.RUNNING)
    assert_true_after_time(job_2.is_completed)  # job 2 unlocked so it can complete
    assert _DataManager._get(task_2.baz.id).is_ready_for_reading  # baz becomes ready
    assert _DataManager._get(task_2.baz.id).read() == 6  # the data is computed and written
    assert_true_after_time(lambda: len(_OrchestratorFactory._dispatcher._dispatched_processes) == 0)
    assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.COMPLETED)


# ################################  UTIL METHODS    ##################################
def _create_task(function, nb_outputs=1):
    output_dn_config_id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    dn_input_configs = [
        Config.configure_data_node("input1", "pickle", Scope.SCENARIO, default_data=21),
        Config.configure_data_node("input2", "pickle", Scope.SCENARIO, default_data=2),
    ]
    dn_output_configs = [
        Config.configure_data_node(f"{output_dn_config_id}_output{i}", "pickle", Scope.SCENARIO, default_data=0)
        for i in range(nb_outputs)
    ]
    input_dn = _DataManager._bulk_get_or_create(dn_input_configs).values()
    output_dn = _DataManager._bulk_get_or_create(dn_output_configs).values()
    return Task(
        output_dn_config_id,
        {},
        function=function,
        input=input_dn,
        output=output_dn,
    )
