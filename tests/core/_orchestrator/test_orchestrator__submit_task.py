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
from datetime import datetime
from unittest import mock

import freezegun
import pytest

from taipy.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission_status import SubmissionStatus


def nothing(*args, **kwargs):
    pass


def create_scenario():
    # dn_0 --> t1 --> dn_1 --> t2 --> dn_2 --> t3 --> dn_3
    #                  \
    #                   \--> t2_bis
    dn_0 = Config.configure_data_node("dn_0", default_data=0)
    dn_1 = Config.configure_data_node("dn_1")
    dn_2 = Config.configure_data_node("dn_2")
    dn_3 = Config.configure_data_node("dn_3")
    t1 = Config.configure_task("t1", nothing, [dn_0], [dn_1], skippable=True)
    t2 = Config.configure_task("t2", nothing, [dn_1], [dn_2])
    t3 = Config.configure_task("t3", nothing, [dn_2], [dn_3])
    t2_bis = Config.configure_task("t2bis", nothing, [dn_1], [])
    sc_conf = Config.configure_scenario("scenario", [t1, t2, t3, t2_bis])
    return taipy.create_scenario(sc_conf)


def test_submit_task_development_mode():
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now()
    with freezegun.freeze_time(submit_time):
        job = orchestrator.submit_task(scenario.t1)  # t1 is executed directly in development mode

    # task output should have been written
    assert scenario.dn_1.last_edit_date == submit_time

    # job exists and is correct
    assert job.task == scenario.t1
    assert not job.force
    assert job.is_completed()
    assert job.submit_entity_id == scenario.t1.id
    assert job.creation_date == submit_time
    assert job.stacktrace == []
    assert len(job._subscribers) == 2  # submission._update_submission_status and orchestrator._on_status_change

    # submission is created and correct
    all_submissions = _SubmissionManagerFactory._build_manager()._get_all()
    assert len(all_submissions) == 1
    assert all_submissions[0].creation_date == submit_time
    assert all_submissions[0].submission_status == SubmissionStatus.COMPLETED
    assert all_submissions[0].jobs == [job]
    assert all_submissions[0].entity_id == scenario.t1.id
    assert all_submissions[0].entity_type == "TASK"
    assert all_submissions[0].entity_config_id == "t1"

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 0
    assert orchestrator.jobs_to_run.qsize() == 0


def test_submit_task_development_mode_blocked_job():
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now()
    with freezegun.freeze_time(submit_time):
        job = orchestrator.submit_task(scenario.t2)  # t1 is executed directly in development mode

    # task output should have been written
    assert scenario.dn_2.edit_in_progress

    # job exists and is correct
    assert job.task == scenario.t2
    assert not job.force
    assert job.is_blocked()  # input data is not ready
    assert job.submit_entity_id == scenario.t2.id
    assert job.creation_date == submit_time
    assert len(job._subscribers) == 2  # submission._update_submission_status and orchestrator._on_status_change
    assert job.stacktrace == []

    # submission is created and correct
    submission = _SubmissionManagerFactory._build_manager()._get(job.submit_id)
    assert submission.submission_status == SubmissionStatus.BLOCKED
    assert submission.creation_date == submit_time
    assert submission.jobs == [job]
    assert submission.entity_id == scenario.t2.id
    assert submission.entity_type == "TASK"
    assert submission.entity_config_id == "t2"

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 1
    assert orchestrator.jobs_to_run.qsize() == 0


@pytest.mark.standalone
def test_submit_task_standalone_mode():
    Config.configure_job_executions(mode="standalone")
    sc = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now()
    with freezegun.freeze_time(submit_time):
        job = orchestrator.submit_task(sc.t1)  # No dispatcher running. t1 is not executed in standalone mode.

    # task output should NOT have been written
    assert sc.dn_1.last_edit_date is None

    # task output should be locked for edition
    assert sc.dn_1.edit_in_progress

    # job exists and is correct
    assert job.creation_date == submit_time
    assert job.task == sc.t1
    assert not job.force
    assert job.is_pending()
    assert job.submit_entity_id == sc.t1.id
    assert len(job._subscribers) == 2  # submission._update_submission_status and orchestrator._on_status_change
    assert job.stacktrace == []

    # submission is created and correct
    submission = _SubmissionManagerFactory._build_manager()._get(job.submit_id)
    assert submission.creation_date == submit_time
    assert submission.submission_status == SubmissionStatus.PENDING
    assert submission.jobs == [job]
    assert submission.entity_id == sc.t1.id
    assert submission.entity_type == "TASK"
    assert submission.entity_config_id == "t1"

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 0
    assert orchestrator.jobs_to_run.qsize() == 1


@pytest.mark.standalone
def test_submit_task_standalone_mode_blocked_job():
    Config.configure_job_executions(mode="standalone")
    sc = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    submit_time = datetime.now()
    with freezegun.freeze_time(submit_time):
        job = orchestrator.submit_task(sc.t2)  # No dispatcher running. t2 is not executed in standalone mode.

    # task output should NOT have been written
    assert sc.dn_2.last_edit_date is None

    # task output should be locked for edition
    assert sc.dn_2.edit_in_progress

    # job exists and is correct
    assert job.creation_date == submit_time
    assert job.task == sc.t2
    assert not job.force
    assert job.is_blocked()  # input data is not ready
    assert job.stacktrace == []
    assert len(job._subscribers) == 2  # submission._update_submission_status and orchestrator._on_status_change
    assert job.submit_entity_id == sc.t2.id

    # submission is created and correct
    submission = _SubmissionManagerFactory._build_manager()._get(job.submit_id)
    assert submission.creation_date == submit_time
    assert submission.submission_status == SubmissionStatus.BLOCKED
    assert submission.jobs == [job]
    assert submission.entity_id == sc.t2.id
    assert submission.entity_type == "TASK"
    assert submission.entity_config_id == "t2"

    # orchestrator state is correct
    assert len(orchestrator.blocked_jobs) == 1
    assert orchestrator.jobs_to_run.qsize() == 0


@pytest.mark.standalone
def test_submit_task_with_callbacks_and_force_and_wait():
    Config.configure_job_executions(mode="standalone")
    scenario = create_scenario()
    orchestrator = _OrchestratorFactory._build_orchestrator()

    with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator._wait_until_job_finished") as mck:
        job = orchestrator.submit_task(scenario.t1, callbacks=[nothing], force=True, wait=True, timeout=2)

        # job exists and is correct
        assert job.task == scenario.t1
        assert job.force
        assert len(job._subscribers) == 3  # nothing, _update_submission_status, and _on_status_change
        mck.assert_called_once_with(job, timeout=2)
