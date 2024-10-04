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

from datetime import datetime, timedelta
from time import sleep
from unittest import mock

import freezegun
import pytest

from taipy import Scenario, Task
from taipy.common.config import Config
from taipy.common.config.common import Scope
from taipy.core import Orchestrator, taipy
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config import JobConfig
from taipy.core.data import PickleDataNode
from taipy.core.data._data_manager import _DataManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission_status import SubmissionStatus
from taipy.core.task._task_manager import _TaskManager
from tests.core.utils import assert_true_after_time


def nothing(*args, **kwargs):
    pass


def create_scenario():
    # dn_0 --> t1 --> dn_1 --> t2 --> dn_2 --> t3 --> dn_3
    #                  \
    #                   \--> t2_bis
    dn_0_cfg = Config.configure_pickle_data_node("dn_0")
    dn_1_cfg = Config.configure_pickle_data_node("dn_1")
    dn_2_cfg = Config.configure_pickle_data_node("dn_2")
    dn_3_cfg = Config.configure_pickle_data_node("dn_3")
    t1_cfg = Config.configure_task("t_1", nothing, [dn_0_cfg], [dn_1_cfg], skippable=True)
    t2_cfg = Config.configure_task("t_2", nothing, [dn_1_cfg], [dn_2_cfg])
    t3_cfg = Config.configure_task("t_3", nothing, [dn_2_cfg], [dn_3_cfg])
    t2_bis_cfg = Config.configure_task("t_2bis", nothing, [dn_1_cfg], [])
    sc_conf = Config.configure_scenario("scenario_cfg", [t2_cfg, t1_cfg, t3_cfg, t2_bis_cfg])
    return taipy.create_scenario(sc_conf)


def test_submit_scenario_development_mode():
    scenario = create_scenario()
    scenario.dn_0.write(0)  # input data is made ready
    orchestrator = _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()

    submit_time = datetime.now() + timedelta(seconds=1)  # +1 to ensure the edit time of dn_0 is before the submit time
    with freezegun.freeze_time(submit_time):
        submission = orchestrator.submit(
            scenario, no_of_retry=10, log=True, log_file="file_path"
        )  # scenario is executed directly in development mode
        jobs = submission.jobs

    # data nodes should have been written (except the input dn_0)
    assert scenario.dn_0.last_edit_date < submit_time
    assert scenario.dn_1.last_edit_date is not None
    assert scenario.dn_2.last_edit_date is not None
    assert scenario.dn_3.last_edit_date is not None

    # jobs are created in a specific order and are correct
    assert len(jobs) == 4
    # t1
    job_1 = jobs[0]
    assert job_1.task == scenario.t_1
    assert not job_1.force
    assert job_1.is_completed()
    assert job_1.submit_entity_id == scenario.id
    assert job_1.creation_date == submit_time
    assert job_1.stacktrace == []
    assert len(job_1._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_1._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_1._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t2 or t2_bis
    job_2 = jobs[1]
    assert job_2.task == scenario.t_2 or job_2.task == scenario.t_2bis
    assert not job_2.force
    assert job_2.is_completed()
    assert job_2.submit_entity_id == scenario.id
    assert job_2.creation_date == submit_time
    assert job_2.stacktrace == []
    assert len(job_2._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t2_bis or t2
    job_2bis = jobs[2]
    assert job_2bis.task == scenario.t_2bis or job_2bis.task == scenario.t_2
    assert job_2bis.is_completed()
    assert not job_2bis.force
    assert job_2bis.submit_entity_id == scenario.id
    assert job_2bis.creation_date == submit_time
    assert len(job_2bis._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2bis._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2bis._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_2bis.stacktrace == []
    # t3
    job_3 = jobs[3]
    assert job_3.task == scenario.t_3
    assert not job_3.force
    assert job_3.is_completed()
    assert job_3.submit_entity_id == scenario.id
    assert job_3.creation_date == submit_time
    assert len(job_3._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_3._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_3._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_3.stacktrace == []

    assert job_1.submit_id == job_2.submit_id == job_2bis.submit_id == job_3.submit_id

    # submission is created and correct
    assert len(_SubmissionManagerFactory._build_manager()._get_all()) == 1
    submission = _SubmissionManagerFactory._build_manager()._get(job_1.submit_id)
    assert submission.submission_status == SubmissionStatus.COMPLETED
    assert submission.jobs == jobs
    assert submission.creation_date == submit_time
    assert submission.entity_id == scenario.id
    assert submission.entity_type == "SCENARIO"
    assert submission.entity_config_id == "scenario_cfg"
    assert submission.properties == {"no_of_retry": 10, "log": True, "log_file": "file_path"}

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 0
    assert orchestrator.jobs_to_run.qsize() == 0


def test_submit_scenario_development_mode_blocked_jobs():
    scenario = create_scenario()  # input data is not ready
    orchestrator = _OrchestratorFactory._build_orchestrator()

    s_time = datetime.now() + timedelta(seconds=1)  # +1 to ensure the scenario creation is before the submit time
    with freezegun.freeze_time(s_time):
        submission = orchestrator.submit(
            scenario, no_of_retry=10, log=True, log_file="file_path"
        )  # first task is blocked because input is not ready
        jobs = submission.jobs

    # dn should be locked for edition
    assert scenario.dn_2.edit_in_progress
    assert scenario.dn_2.edit_in_progress
    assert scenario.dn_3.edit_in_progress

    # jobs are created in a specific order and are correct
    assert len(jobs) == 4
    # t1
    job_1 = jobs[0]
    assert job_1.task == scenario.t_1
    assert not job_1.force
    assert job_1.is_blocked()
    assert job_1.submit_entity_id == scenario.id
    assert job_1.creation_date == s_time
    assert job_1.stacktrace == []
    assert len(job_1._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_1._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_1._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t2 or t2_bis
    job_2 = jobs[1]
    assert job_2.task == scenario.t_2 or job_2.task == scenario.t_2bis
    assert not job_2.force
    assert job_2.is_blocked()
    assert job_2.submit_entity_id == scenario.id
    assert job_2.creation_date == s_time
    assert job_2.stacktrace == []
    assert len(job_2._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t2_bis or t2
    job_2bis = jobs[2]
    assert job_2bis.task == scenario.t_2bis or job_2bis.task == scenario.t_2
    assert job_2bis.is_blocked()
    assert job_2bis.submit_entity_id == scenario.id
    assert not job_2bis.force
    assert job_2bis.creation_date == s_time
    assert len(job_2bis._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2bis._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2bis._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_2bis.stacktrace == []
    # t3
    job_3 = jobs[3]
    assert job_3.task == scenario.t_3
    assert not job_3.force
    assert job_3.is_blocked()
    assert job_3.submit_entity_id == scenario.id
    assert job_3.creation_date == s_time
    assert job_3.stacktrace == []
    assert len(job_3._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_3._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_3._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__

    # Same submit_id
    assert job_1.submit_id == job_2.submit_id == job_2bis.submit_id == job_3.submit_id

    # submission is created and correct
    assert len(_SubmissionManagerFactory._build_manager()._get_all()) == 1
    submission = _SubmissionManagerFactory._build_manager()._get(job_1.submit_id)
    assert submission.submission_status == SubmissionStatus.BLOCKED
    assert submission.jobs == jobs
    assert submission.creation_date == s_time
    assert submission.entity_id == scenario.id
    assert submission.entity_type == "SCENARIO"
    assert submission.entity_config_id == "scenario_cfg"
    assert submission.properties == {"no_of_retry": 10, "log": True, "log_file": "file_path"}

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 4
    assert orchestrator.jobs_to_run.qsize() == 0


@pytest.mark.standalone
def test_submit_scenario_standalone_mode():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    sc = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()
    sc.dn_0.write(0)  # input data is made ready
    submit_time = datetime.now() + timedelta(seconds=1)  # +1 to ensure the edit time of dn_0 is before the submit time
    with freezegun.freeze_time(submit_time):
        submission = orchestrator.submit(
            sc, no_of_retry=10, log=True, log_file="file_path"
        )  # No dispatcher running. sc is not executed.
        jobs = submission.jobs

    # task output should be locked for edition
    assert sc.dn_1.edit_in_progress
    assert sc.dn_2.edit_in_progress
    assert sc.dn_3.edit_in_progress

    # jobs are created in a specific order and are correct
    assert len(jobs) == 4
    # t1
    job_1 = jobs[0]
    assert job_1.task == sc.t_1
    assert not job_1.force
    assert job_1.is_pending()
    assert job_1.creation_date == submit_time
    assert job_1.submit_entity_id == sc.id
    assert len(job_1._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_1._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_1._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_1.stacktrace == []
    # t2 or t2_bis
    job_2 = jobs[1]
    assert job_2.task == sc.t_2 or job_2.task == sc.t_2bis
    assert job_2.is_blocked()
    assert not job_2.force
    assert job_2.submit_entity_id == sc.id
    assert job_2.creation_date == submit_time
    assert job_2.stacktrace == []
    assert len(job_2._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_2._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    # t2_bis or t2
    job_2bis = jobs[2]
    assert job_2bis.task == sc.t_2bis or job_2bis.task == sc.t_2
    assert job_2bis.is_blocked()
    assert not job_2bis.force
    assert job_2bis.submit_entity_id == sc.id
    assert len(job_2bis._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2bis._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_2bis._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2bis.creation_date == submit_time
    assert job_2bis.stacktrace == []
    # t3
    job_3 = jobs[3]
    assert job_3.task == sc.t_3
    assert not job_3.force
    assert job_3.is_blocked()
    assert job_3.submit_entity_id == sc.id
    assert len(job_3._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_3._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_3._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_3.creation_date == submit_time
    assert job_3.stacktrace == []

    assert job_1.submit_id == job_2.submit_id == job_2bis.submit_id == job_3.submit_id

    # submission is created and correct
    assert len(_SubmissionManagerFactory._build_manager()._get_all()) == 1
    submission = _SubmissionManagerFactory._build_manager()._get(job_1.submit_id)
    assert submission.submission_status == SubmissionStatus.PENDING
    assert submission.jobs == jobs
    assert submission.creation_date == submit_time
    assert submission.entity_id == sc.id
    assert submission.entity_type == "SCENARIO"
    assert submission.entity_config_id == "scenario_cfg"
    assert submission.properties == {"no_of_retry": 10, "log": True, "log_file": "file_path"}

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 3
    assert orchestrator.jobs_to_run.qsize() == 1


def test_submit_scenario_with_callbacks_and_force_and_wait():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._wait_until_job_finished") as mck:
        submission = orchestrator.submit(scenario, callbacks=[nothing], force=True, wait=True, timeout=5)
        jobs = submission.jobs

        # jobs are created in a specific order and are correct
        assert len(jobs) == 4
        assert len(jobs[0]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
        assert jobs[0]._subscribers[0].__code__ == nothing.__code__
        assert jobs[0]._subscribers[1].__code__ == _Orchestrator._update_submission_status.__code__
        assert jobs[0]._subscribers[2].__code__ == _Orchestrator._on_status_change.__code__
        assert len(jobs[1]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
        assert jobs[1]._subscribers[0].__code__ == nothing.__code__
        assert jobs[1]._subscribers[1].__code__ == _Orchestrator._update_submission_status.__code__
        assert jobs[1]._subscribers[2].__code__ == _Orchestrator._on_status_change.__code__
        assert len(jobs[2]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
        assert jobs[2]._subscribers[0].__code__ == nothing.__code__
        assert jobs[2]._subscribers[1].__code__ == _Orchestrator._update_submission_status.__code__
        assert jobs[2]._subscribers[2].__code__ == _Orchestrator._on_status_change.__code__
        mck.assert_called_once_with(jobs, 5)


def test_submit_sequence_development_mode():
    sce = create_scenario()
    sce.add_sequence("seq", [sce.t_1, sce.t_2, sce.t_3])
    seq = sce.sequences["seq"]
    sce.dn_0.write(0)  # input data is made ready

    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now() + timedelta(seconds=1)  # +1 to ensure the edit time of dn_0 is before the submit time
    with freezegun.freeze_time(submit_time):
        submission = orchestrator.submit(
            seq, no_of_retry=10, log=True, log_file="file_path"
        )  # sequence is executed directly in development mode
        jobs = submission.jobs

    # data nodes should have been written (except the input dn_0)
    assert sce.dn_0.last_edit_date < submit_time
    assert sce.dn_1.last_edit_date is not None
    assert sce.dn_2.last_edit_date is not None
    assert sce.dn_3.last_edit_date is not None

    # jobs are created in a specific order and are correct
    assert len(jobs) == 3
    # t1
    job_1 = jobs[0]
    assert job_1.task == sce.t_1
    assert not job_1.force
    assert job_1.is_completed()
    assert job_1.submit_entity_id == seq.id
    assert job_1.creation_date == submit_time
    assert job_1.stacktrace == []
    assert len(job_1._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_1._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_1._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t2
    job_2 = jobs[1]
    assert job_2.task == sce.t_2
    assert not job_2.force
    assert job_2.is_completed()
    assert job_2.submit_entity_id == seq.id
    assert job_2.creation_date == submit_time
    assert job_2.stacktrace == []
    assert len(job_2._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_2._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_2._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    # t3
    job_3 = jobs[2]
    assert job_3.task == sce.t_3
    assert not job_3.force
    assert job_3.is_completed()
    assert job_3.submit_entity_id == seq.id
    assert len(job_3._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_3._subscribers[0].__code__ == _Orchestrator._update_submission_status.__code__
    assert job_3._subscribers[1].__code__ == _Orchestrator._on_status_change.__code__
    assert job_3.creation_date == submit_time
    assert job_3.stacktrace == []

    assert job_1.submit_id == job_2.submit_id == job_3.submit_id

    # submission is created and correct
    assert len(_SubmissionManagerFactory._build_manager()._get_all()) == 1
    submission = _SubmissionManagerFactory._build_manager()._get(job_1.submit_id)
    assert submission.entity_type == "SEQUENCE"
    assert submission.submission_status == SubmissionStatus.COMPLETED
    assert submission.entity_config_id is None
    assert submission.jobs == jobs
    assert submission.creation_date == submit_time
    assert submission.entity_id == seq.id
    assert submission.properties == {"no_of_retry": 10, "log": True, "log_file": "file_path"}

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 0
    assert orchestrator.jobs_to_run.qsize() == 0


@pytest.mark.standalone
def test_submit_sequence_standalone_mode():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    scenario = create_scenario()
    scenario.dn_0.write(0)  # input data is made ready
    scenario.add_sequence("seq", [scenario.t_1, scenario.t_2, scenario.t_3])
    sequence = scenario.sequences["seq"]

    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now() + timedelta(seconds=1)  # +1 to ensure the edit time of dn_0 is before the submit time
    with freezegun.freeze_time(submit_time):
        submission = orchestrator.submit(
            sequence, no_of_retry=10, log=True, log_file="file_path"
        )  # sequence is executed directly in development mode
        jobs = submission.jobs

    assert scenario.dn_1.edit_in_progress
    assert scenario.dn_2.edit_in_progress
    assert scenario.dn_3.edit_in_progress

    # jobs are created in a specific order and are correct
    assert len(jobs) == 3
    # t1
    job_1 = jobs[0]
    assert job_1.task == scenario.t_1
    assert not job_1.force
    assert job_1.is_pending()
    assert job_1.creation_date == submit_time
    assert job_1.submit_entity_id == sequence.id
    assert job_1.stacktrace == []
    assert len(job_1._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    # t2
    job_2 = jobs[1]
    assert job_2.task == scenario.t_2
    assert not job_2.force
    assert job_2.is_blocked()
    assert job_2.submit_entity_id == sequence.id
    assert job_2.creation_date == submit_time
    assert job_2.stacktrace == []
    assert len(job_2._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    # t3
    job_3 = jobs[2]
    assert job_3.task == scenario.t_3
    assert not job_3.force
    assert job_3.is_blocked()
    assert job_3.creation_date == submit_time
    assert job_3.submit_entity_id == sequence.id
    assert len(job_3._subscribers) == 2  # _Orchestrator._update_submission_status and orchestrator._on_status_change
    assert job_3.stacktrace == []

    assert job_1.submit_id == job_2.submit_id == job_3.submit_id

    # submission is created and correct
    assert len(_SubmissionManagerFactory._build_manager()._get_all()) == 1
    submission = _SubmissionManagerFactory._build_manager()._get(job_1.submit_id)
    assert submission.submission_status == SubmissionStatus.PENDING
    assert submission.entity_type == "SEQUENCE"
    assert submission.entity_config_id is None
    assert submission.jobs == jobs
    assert submission.creation_date == submit_time
    assert submission.entity_id == sequence.id
    assert submission.properties == {"no_of_retry": 10, "log": True, "log_file": "file_path"}

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 2
    assert orchestrator.jobs_to_run.qsize() == 1


@pytest.mark.standalone
def test_submit_sequence_with_callbacks_and_force_and_wait():
    Config.configure_job_executions(mode="standalone")
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._wait_until_job_finished") as mck:
        jobs = orchestrator.submit(scenario, callbacks=[nothing], force=True, wait=True, timeout=5).jobs
        mck.assert_called_once_with(jobs, 5)

    # jobs are created in a specific order and are correct
    assert len(jobs) == 4
    assert len(jobs[0]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
    assert len(jobs[1]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
    assert len(jobs[2]._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change


def test_submit_submittable_generate_unique_submit_id():
    dn_1 = PickleDataNode("dn_config_id_1", Scope.SCENARIO)
    dn_2 = PickleDataNode("dn_config_id_2", Scope.SCENARIO)
    task_1 = Task("task_config_id_1", {}, print, [dn_1])
    task_2 = Task("task_config_id_2", {}, print, [dn_1], [dn_2])

    _DataManager._set(dn_1)
    _DataManager._set(dn_2)
    _TaskManager._set(task_1)
    _TaskManager._set(task_2)

    scenario = Scenario("scenario", {task_1, task_2}, {})
    _ScenarioManager._set(scenario)

    jobs_1 = taipy.submit(scenario).jobs
    jobs_2 = taipy.submit(scenario).jobs
    assert len(jobs_1) == 2
    assert len(jobs_2) == 2
    assert jobs_1[0].submit_id == jobs_1[1].submit_id
    assert jobs_2[0].submit_id == jobs_2[1].submit_id
    assert jobs_1[0].submit_id != jobs_2[0].submit_id


def task_sleep_1():
    sleep(1)


def task_sleep_2():
    sleep(2)
    return


def test_submit_duration_development_mode():
    orchestrator = Orchestrator()
    orchestrator.run()

    task_1 = Task("task_config_id_1", {}, task_sleep_1, [], [])
    task_2 = Task("task_config_id_2", {}, task_sleep_2, [], [])

    _TaskManager._set(task_1)
    _TaskManager._set(task_2)

    scenario = Scenario("scenario", {task_1, task_2}, {})
    _ScenarioManager._set(scenario)
    submission = taipy.submit(scenario)
    jobs = submission.jobs
    orchestrator.stop()

    assert all(isinstance(job.submitted_at, datetime) for job in jobs)
    assert all(isinstance(job.run_at, datetime) for job in jobs)
    assert all(isinstance(job.finished_at, datetime) for job in jobs)
    jobs_1s = jobs[0] if jobs[0].task.config_id == "task_config_id_1" else jobs[1]
    jobs_2s = jobs[0] if jobs[0].task.config_id == "task_config_id_2" else jobs[1]
    assert jobs_1s.execution_duration >= 1
    assert jobs_2s.execution_duration >= 2

    assert submission.execution_duration >= 3
    assert submission.submitted_at == min(jobs_1s.submitted_at, jobs_2s.submitted_at)
    assert submission.run_at == min(jobs_1s.run_at, jobs_2s.run_at)
    assert submission.finished_at == max(jobs_1s.finished_at, jobs_2s.finished_at)


@pytest.mark.standalone
def test_submit_duration_standalone_mode():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    orchestrator = Orchestrator()
    orchestrator.run()

    task_1 = Task("task_config_id_1", {}, task_sleep_1, [], [])
    task_2 = Task("task_config_id_2", {}, task_sleep_2, [], [])

    _TaskManager._set(task_1)
    _TaskManager._set(task_2)

    scenario = Scenario("scenario", {task_1, task_2}, {})
    _ScenarioManager._set(scenario)
    submission = taipy.submit(scenario)

    assert_true_after_time(lambda: all(job is not None and job.is_completed() for job in submission.jobs))
    orchestrator.stop()

    jobs = submission.jobs

    assert all(isinstance(job.submitted_at, datetime) for job in jobs)
    assert all(isinstance(job.run_at, datetime) for job in jobs)
    assert all(isinstance(job.finished_at, datetime) for job in jobs)
    jobs_1s = jobs[0] if jobs[0].task.config_id == "task_config_id_1" else jobs[1]
    jobs_2s = jobs[0] if jobs[0].task.config_id == "task_config_id_2" else jobs[1]
    assert jobs_1s.execution_duration >= 1
    assert jobs_2s.execution_duration >= 2

    assert submission.execution_duration >= 2  # Both tasks are executed in parallel so the duration may smaller than 3
    assert submission.submitted_at == min(jobs_1s.submitted_at, jobs_2s.submitted_at)
    assert submission.run_at == min(jobs_1s.run_at, jobs_2s.run_at)
    assert submission.finished_at == max(jobs_1s.finished_at, jobs_2s.finished_at)
