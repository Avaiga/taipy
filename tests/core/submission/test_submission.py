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

import pytest

from taipy.core import TaskId
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.job.status import Status
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission import Submission
from taipy.core.submission.submission_status import SubmissionStatus
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def test_create_submission(scenario, job, current_datetime):
    submission_1 = Submission(scenario.id, scenario._ID_PREFIX, scenario.config_id)

    assert submission_1.id is not None
    assert submission_1.entity_id == scenario.id
    assert submission_1.entity_type == scenario._ID_PREFIX
    assert submission_1.entity_config_id == scenario.config_id
    assert submission_1.jobs == []
    assert isinstance(submission_1.creation_date, datetime)
    assert submission_1._submission_status == SubmissionStatus.SUBMITTED
    assert submission_1._version is not None

    submission_2 = Submission(
        scenario.id,
        scenario._ID_PREFIX,
        scenario.config_id,
        "submission_id",
        [job],
        {"debug": True, "log": "log_file", "retry_note": 5},
        current_datetime,
        SubmissionStatus.COMPLETED,
        "version_id",
    )

    assert submission_2.id == "submission_id"
    assert submission_2.entity_id == scenario.id
    assert submission_2.entity_type == scenario._ID_PREFIX
    assert submission_2.entity_config_id == scenario.config_id
    assert submission_2._jobs == [job]
    assert submission_2._properties == {"debug": True, "log": "log_file", "retry_note": 5}
    assert submission_2.creation_date == current_datetime
    assert submission_2._submission_status == SubmissionStatus.COMPLETED
    assert submission_2._version == "version_id"


class MockJob:
    def __init__(self, id: str, status):
        self.status = status
        self.id = id

    def is_failed(self):
        return self.status == Status.FAILED

    def is_canceled(self):
        return self.status == Status.CANCELED

    def is_blocked(self):
        return self.status == Status.BLOCKED

    def is_pending(self):
        return self.status == Status.PENDING

    def is_running(self):
        return self.status == Status.RUNNING

    def is_completed(self):
        return self.status == Status.COMPLETED

    def is_skipped(self):
        return self.status == Status.SKIPPED

    def is_abandoned(self):
        return self.status == Status.ABANDONED

    def is_submitted(self):
        return self.status == Status.SUBMITTED


def __test_update_submission_status(job_ids, expected_submission_status):
    jobs = {
        "job0_submitted": MockJob("job0_submitted", Status.SUBMITTED),
        "job1_failed": MockJob("job1_failed", Status.FAILED),
        "job2_canceled": MockJob("job2_canceled", Status.CANCELED),
        "job3_blocked": MockJob("job3_blocked", Status.BLOCKED),
        "job4_pending": MockJob("job4_pending", Status.PENDING),
        "job5_running": MockJob("job5_running", Status.RUNNING),
        "job6_completed": MockJob("job6_completed", Status.COMPLETED),
        "job7_skipped": MockJob("job7_skipped", Status.SKIPPED),
        "job8_abandoned": MockJob("job8_abandoned", Status.ABANDONED),
    }

    submission = Submission("submission_id", "ENTITY_TYPE", "entity_config_id")
    submission.jobs = [jobs[job_id] for job_id in job_ids]
    for job_id in job_ids:
        job = jobs[job_id]
        submission._update_submission_status(job)
    assert submission.submission_status == expected_submission_status


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job1_failed"], SubmissionStatus.FAILED),
        (["job2_canceled"], SubmissionStatus.CANCELED),
        (["job3_blocked"], SubmissionStatus.BLOCKED),
        (["job4_pending"], SubmissionStatus.PENDING),
        (["job5_running"], SubmissionStatus.RUNNING),
        (["job6_completed"], SubmissionStatus.COMPLETED),
        (["job7_skipped"], SubmissionStatus.COMPLETED),
        (["job8_abandoned"], SubmissionStatus.UNDEFINED),
    ],
)
def test_update_single_submission_status(job_ids, expected_submission_status):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job1_failed", "job1_failed"], SubmissionStatus.FAILED),
        (["job1_failed", "job2_canceled"], SubmissionStatus.FAILED),
        (["job1_failed", "job3_blocked"], SubmissionStatus.FAILED),
        (["job1_failed", "job4_pending"], SubmissionStatus.FAILED),
        (["job1_failed", "job5_running"], SubmissionStatus.FAILED),
        (["job1_failed", "job6_completed"], SubmissionStatus.FAILED),
        (["job1_failed", "job7_skipped"], SubmissionStatus.FAILED),
        (["job1_failed", "job8_abandoned"], SubmissionStatus.FAILED),
        (["job2_canceled", "job1_failed"], SubmissionStatus.FAILED),
        (["job3_blocked", "job1_failed"], SubmissionStatus.FAILED),
        (["job4_pending", "job1_failed"], SubmissionStatus.FAILED),
        (["job5_running", "job1_failed"], SubmissionStatus.FAILED),
        (["job6_completed", "job1_failed"], SubmissionStatus.FAILED),
        (["job7_skipped", "job1_failed"], SubmissionStatus.FAILED),
        (["job8_abandoned", "job1_failed"], SubmissionStatus.FAILED),
    ],
)
def test_update_submission_status_with_one_failed_job_in_jobs(job_ids, expected_submission_status):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job2_canceled", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job3_blocked"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job4_pending"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job5_running"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job6_completed"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job7_skipped"], SubmissionStatus.CANCELED),
        (["job2_canceled", "job8_abandoned"], SubmissionStatus.CANCELED),
        (["job3_blocked", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job4_pending", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job5_running", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job6_completed", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job7_skipped", "job2_canceled"], SubmissionStatus.CANCELED),
        (["job8_abandoned", "job2_canceled"], SubmissionStatus.CANCELED),
    ],
)
def test_update_submission_status_with_one_canceled_job_in_jobs(job_ids, expected_submission_status):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job4_pending", "job3_blocked"], SubmissionStatus.PENDING),
        (["job4_pending", "job4_pending"], SubmissionStatus.PENDING),
        (["job4_pending", "job6_completed"], SubmissionStatus.PENDING),
        (["job4_pending", "job7_skipped"], SubmissionStatus.PENDING),
        (["job3_blocked", "job4_pending"], SubmissionStatus.PENDING),
        (["job6_completed", "job4_pending"], SubmissionStatus.PENDING),
        (["job7_skipped", "job4_pending"], SubmissionStatus.PENDING),
    ],
)
def test_update_submission_status_with_no_failed_or_cancel_one_pending_in_jobs(job_ids, expected_submission_status):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job5_running", "job3_blocked"], SubmissionStatus.RUNNING),
        (["job5_running", "job4_pending"], SubmissionStatus.RUNNING),
        (["job5_running", "job5_running"], SubmissionStatus.RUNNING),
        (["job5_running", "job6_completed"], SubmissionStatus.RUNNING),
        (["job5_running", "job7_skipped"], SubmissionStatus.RUNNING),
        (["job3_blocked", "job5_running"], SubmissionStatus.RUNNING),
        (["job4_pending", "job5_running"], SubmissionStatus.RUNNING),
        (["job6_completed", "job5_running"], SubmissionStatus.RUNNING),
        (["job7_skipped", "job5_running"], SubmissionStatus.RUNNING),
    ],
)
def test_update_submission_status_with_no_failed_cancel_nor_pending_one_running_in_jobs(
    job_ids, expected_submission_status
):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job3_blocked", "job3_blocked"], SubmissionStatus.BLOCKED),
        (["job3_blocked", "job6_completed"], SubmissionStatus.BLOCKED),
        (["job3_blocked", "job7_skipped"], SubmissionStatus.BLOCKED),
        (["job6_completed", "job3_blocked"], SubmissionStatus.BLOCKED),
        (["job7_skipped", "job3_blocked"], SubmissionStatus.BLOCKED),
    ],
)
def test_update_submission_status_with_no_failed_cancel_pending_nor_running_one_blocked_in_jobs(
    job_ids, expected_submission_status
):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job6_completed", "job6_completed"], SubmissionStatus.COMPLETED),
        (["job6_completed", "job7_skipped"], SubmissionStatus.COMPLETED),
        (["job7_skipped", "job6_completed"], SubmissionStatus.COMPLETED),
        (["job7_skipped", "job7_skipped"], SubmissionStatus.COMPLETED),
    ],
)
def test_update_submission_status_with_only_completed_or_skipped_in_jobs(job_ids, expected_submission_status):
    __test_update_submission_status(job_ids, expected_submission_status)


@pytest.mark.parametrize(
    "job_ids, expected_submission_status",
    [
        (["job3_blocked", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job4_pending", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job5_running", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job6_completed", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job7_skipped", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job8_abandoned"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job3_blocked"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job4_pending"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job5_running"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job6_completed"], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job7_skipped"], SubmissionStatus.UNDEFINED),
    ],
)
def test_update_submission_status_with_wrong_case_abandoned_without_cancel_or_failed_in_jobs(
    job_ids, expected_submission_status
):
    __test_update_submission_status(job_ids, expected_submission_status)


def test_auto_set_and_reload():
    task = Task(config_id="name_1", properties={}, function=print, id=TaskId("task_1"))
    submission_1 = Submission(task.id, task._ID_PREFIX, task.config_id, properties={})
    job_1 = Job("job_1", task, submission_1.id, submission_1.entity_id)
    job_2 = Job("job_2", task, submission_1.id, submission_1.entity_id)

    _TaskManagerFactory._build_manager()._set(task)
    _SubmissionManagerFactory._build_manager()._set(submission_1)
    _JobManagerFactory._build_manager()._set(job_1)
    _JobManagerFactory._build_manager()._set(job_2)

    submission_2 = _SubmissionManagerFactory._build_manager()._get(submission_1)

    assert submission_1.id == submission_2.id
    assert submission_1.entity_id == submission_2.entity_id
    assert submission_1.creation_date == submission_2.creation_date
    assert submission_1.submission_status == submission_2.submission_status

    # auto set & reload on jobs attribute
    assert submission_1.jobs == []
    assert submission_2.jobs == []
    submission_1.jobs = [job_1]
    assert submission_1.jobs == [job_1]
    assert submission_2.jobs == [job_1]
    submission_2.jobs = [job_2]
    assert submission_1.jobs == [job_2]
    assert submission_2.jobs == [job_2]
    submission_1.jobs = [job_1, job_2]
    assert submission_1.jobs == [job_1, job_2]
    assert submission_2.jobs == [job_1, job_2]
    submission_2.jobs = [job_2, job_1]
    assert submission_1.jobs == [job_2, job_1]
    assert submission_2.jobs == [job_2, job_1]

    # auto set & reload on is_canceled attribute
    assert not submission_1.is_canceled
    assert not submission_2.is_canceled
    submission_1.is_canceled = True
    assert submission_1.is_canceled
    assert submission_2.is_canceled
    submission_2.is_canceled = False
    assert not submission_1.is_canceled
    assert not submission_2.is_canceled

    # auto set & reload on is_completed attribute
    assert not submission_1.is_completed
    assert not submission_2.is_completed
    submission_1.is_completed = True
    assert submission_1.is_completed
    assert submission_2.is_completed
    submission_2.is_completed = False
    assert not submission_1.is_completed
    assert not submission_2.is_completed

    # auto set & reload on is_abandoned attribute
    assert not submission_1.is_abandoned
    assert not submission_2.is_abandoned
    submission_1.is_abandoned = True
    assert submission_1.is_abandoned
    assert submission_2.is_abandoned
    submission_2.is_abandoned = False
    assert not submission_1.is_abandoned
    assert not submission_2.is_abandoned

    # auto set & reload on submission_status attribute
    assert submission_1.submission_status == SubmissionStatus.SUBMITTED
    assert submission_2.submission_status == SubmissionStatus.SUBMITTED
    submission_1.submission_status = SubmissionStatus.BLOCKED
    assert submission_1.submission_status == SubmissionStatus.BLOCKED
    assert submission_2.submission_status == SubmissionStatus.BLOCKED
    submission_2.submission_status = SubmissionStatus.COMPLETED
    assert submission_1.submission_status == SubmissionStatus.COMPLETED
    assert submission_2.submission_status == SubmissionStatus.COMPLETED

    with submission_1 as submission:
        assert submission.jobs == [job_2, job_1]
        assert submission.submission_status == SubmissionStatus.COMPLETED

        submission.jobs = [job_1]
        submission.submission_status = SubmissionStatus.PENDING

        assert submission.jobs == [job_2, job_1]
        assert submission.submission_status == SubmissionStatus.COMPLETED

    assert submission_1.jobs == [job_1]
    assert submission_1.submission_status == SubmissionStatus.PENDING
    assert submission_2.jobs == [job_1]
    assert submission_2.submission_status == SubmissionStatus.PENDING


def test_auto_set_and_reload_properties():
    task = Task(config_id="name_1", properties={}, function=print, id=TaskId("task_1"))
    submission_1 = Submission(task.id, task._ID_PREFIX, task.config_id, properties={})

    _TaskManagerFactory._build_manager()._set(task)
    _SubmissionManagerFactory._build_manager()._set(submission_1)

    submission_2 = _SubmissionManagerFactory._build_manager()._get(submission_1)

    # auto set & reload on properties attribute
    assert submission_1.properties == {}
    assert submission_2.properties == {}
    submission_1._properties["qux"] = 4
    assert submission_1.properties["qux"] == 4
    assert submission_2.properties["qux"] == 4

    assert submission_1.properties == {"qux": 4}
    assert submission_2.properties == {"qux": 4}
    submission_2._properties["qux"] = 5
    assert submission_1.properties["qux"] == 5
    assert submission_2.properties["qux"] == 5

    submission_1.properties["temp_key_1"] = "temp_value_1"
    submission_1.properties["temp_key_2"] = "temp_value_2"
    assert submission_1.properties == {"qux": 5, "temp_key_1": "temp_value_1", "temp_key_2": "temp_value_2"}
    assert submission_2.properties == {"qux": 5, "temp_key_1": "temp_value_1", "temp_key_2": "temp_value_2"}
    submission_1.properties.pop("temp_key_1")
    assert "temp_key_1" not in submission_1.properties.keys()
    assert "temp_key_1" not in submission_1.properties.keys()
    assert submission_1.properties == {"qux": 5, "temp_key_2": "temp_value_2"}
    assert submission_2.properties == {"qux": 5, "temp_key_2": "temp_value_2"}
    submission_2.properties.pop("temp_key_2")
    assert submission_1.properties == {"qux": 5}
    assert submission_2.properties == {"qux": 5}
    assert "temp_key_2" not in submission_1.properties.keys()
    assert "temp_key_2" not in submission_2.properties.keys()

    submission_1.properties["temp_key_3"] = 0
    assert submission_1.properties == {"qux": 5, "temp_key_3": 0}
    assert submission_2.properties == {"qux": 5, "temp_key_3": 0}
    submission_1.properties.update({"temp_key_3": 1})
    assert submission_1.properties == {"qux": 5, "temp_key_3": 1}
    assert submission_2.properties == {"qux": 5, "temp_key_3": 1}
    submission_1.properties.update({})
    assert submission_1.properties == {"qux": 5, "temp_key_3": 1}
    assert submission_2.properties == {"qux": 5, "temp_key_3": 1}
    submission_1.properties["temp_key_4"] = 0
    submission_1.properties["temp_key_5"] = 0

    with submission_1 as submission:
        assert submission.properties["qux"] == 5
        assert submission.properties["temp_key_3"] == 1
        assert submission.properties["temp_key_4"] == 0
        assert submission.properties["temp_key_5"] == 0

        submission.properties["qux"] = 9
        submission.properties.pop("temp_key_3")
        submission.properties.pop("temp_key_4")
        submission.properties.update({"temp_key_4": 1})
        submission.properties.update({"temp_key_5": 2})
        submission.properties.pop("temp_key_5")
        submission.properties.update({})

        assert submission.properties["qux"] == 5
        assert submission.properties["temp_key_3"] == 1
        assert submission.properties["temp_key_4"] == 0
        assert submission.properties["temp_key_5"] == 0

    assert submission_1.properties["qux"] == 9
    assert "temp_key_3" not in submission_1.properties.keys()
    assert submission_1.properties["temp_key_4"] == 1
    assert "temp_key_5" not in submission_1.properties.keys()


@pytest.mark.parametrize(
    "job_statuses, expected_submission_statuses",
    [
        (
            [Status.SUBMITTED, Status.PENDING, Status.RUNNING, Status.COMPLETED],
            [SubmissionStatus.PENDING, SubmissionStatus.PENDING, SubmissionStatus.RUNNING, SubmissionStatus.COMPLETED],
        ),
        (
            [Status.SUBMITTED, Status.PENDING, Status.RUNNING, Status.SKIPPED],
            [SubmissionStatus.PENDING, SubmissionStatus.PENDING, SubmissionStatus.RUNNING, SubmissionStatus.COMPLETED],
        ),
        (
            [Status.SUBMITTED, Status.PENDING, Status.RUNNING, Status.FAILED],
            [SubmissionStatus.PENDING, SubmissionStatus.PENDING, SubmissionStatus.RUNNING, SubmissionStatus.FAILED],
        ),
        (
            [Status.SUBMITTED, Status.PENDING, Status.CANCELED],
            [SubmissionStatus.PENDING, SubmissionStatus.PENDING, SubmissionStatus.CANCELED],
        ),
        (
            [Status.SUBMITTED, Status.PENDING, Status.RUNNING, Status.CANCELED],
            [SubmissionStatus.PENDING, SubmissionStatus.PENDING, SubmissionStatus.RUNNING, SubmissionStatus.CANCELED],
        ),
        ([Status.SUBMITTED, Status.BLOCKED], [SubmissionStatus.PENDING, SubmissionStatus.BLOCKED]),
        ([Status.SUBMITTED, Status.SKIPPED], [SubmissionStatus.PENDING, SubmissionStatus.COMPLETED]),
    ],
)
def test_update_submission_status_with_single_job_completed(job_statuses, expected_submission_statuses):
    job = MockJob("job_id", Status.SUBMITTED)
    submission = Submission("submission_id", "ENTITY_TYPE", "entity_config_id")
    _SubmissionManagerFactory._build_manager()._set(submission)

    assert submission.submission_status == SubmissionStatus.SUBMITTED

    for job_status, submission_status in zip(job_statuses, expected_submission_statuses):
        job.status = job_status
        submission._update_submission_status(job)
        assert submission.submission_status == submission_status


def __test_update_submission_status_with_two_jobs(job_ids, job_statuses, expected_submission_statuses):
    jobs = {job_id: MockJob(job_id, Status.SUBMITTED) for job_id in job_ids}
    submission = Submission("submission_id", "ENTITY_TYPE", "entity_config_id")
    _SubmissionManagerFactory._build_manager()._set(submission)

    assert submission.submission_status == SubmissionStatus.SUBMITTED

    for (job_id, job_status), submission_status in zip(job_statuses, expected_submission_statuses):
        job = jobs[job_id]
        job.status = job_status
        submission._update_submission_status(job)
        assert submission.submission_status == submission_status


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_statuses",
    [
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_2", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.COMPLETED),
                ("job_2", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.COMPLETED),
                ("job_2", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.BLOCKED),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_2", Status.COMPLETED),
                ("job_1", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_1", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.BLOCKED,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.COMPLETED,
            ],
        ),
    ],
)
def test_update_submission_status_with_two_jobs_completed(job_ids, job_statuses, expected_submission_statuses):
    __test_update_submission_status_with_two_jobs(job_ids, job_statuses, expected_submission_statuses)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_statuses",
    [
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_2", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.SKIPPED),
                ("job_1", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.PENDING),
                ("job_2", Status.SKIPPED),
                ("job_1", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.BLOCKED),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_2", Status.COMPLETED),
                ("job_1", Status.PENDING),
                ("job_1", Status.SKIPPED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.BLOCKED,
                SubmissionStatus.PENDING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_2", Status.PENDING),
                ("job_1", Status.SKIPPED),
                ("job_2", Status.SKIPPED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_1", Status.SKIPPED),
                ("job_2", Status.PENDING),
                ("job_2", Status.SKIPPED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.COMPLETED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.BLOCKED),
                ("job_2", Status.PENDING),
                ("job_2", Status.SKIPPED),
                ("job_1", Status.PENDING),
                ("job_1", Status.SKIPPED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.BLOCKED,
                SubmissionStatus.PENDING,
                SubmissionStatus.COMPLETED,
            ],
        ),
    ],
)
def test_update_submission_status_with_two_jobs_skipped(job_ids, job_statuses, expected_submission_statuses):
    __test_update_submission_status_with_two_jobs(job_ids, job_statuses, expected_submission_statuses)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_statuses",
    [
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_2", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.FAILED),
                ("job_2", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.FAILED,
                SubmissionStatus.FAILED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.COMPLETED),
                ("job_2", Status.FAILED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.FAILED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.BLOCKED),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_2", Status.FAILED),
                ("job_1", Status.ABANDONED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.FAILED,
                SubmissionStatus.FAILED,
            ],
        ),
    ],
)
def test_update_submission_status_with_two_jobs_failed(job_ids, job_statuses, expected_submission_statuses):
    __test_update_submission_status_with_two_jobs(job_ids, job_statuses, expected_submission_statuses)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_statuses",
    [
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_2", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.CANCELED),
                ("job_2", Status.COMPLETED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.CANCELED,
                SubmissionStatus.CANCELED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.PENDING),
                ("job_1", Status.RUNNING),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_1", Status.COMPLETED),
                ("job_2", Status.CANCELED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.CANCELED,
            ],
        ),
        (
            ["job_1", "job_2"],
            [
                ("job_1", Status.SUBMITTED),
                ("job_2", Status.SUBMITTED),
                ("job_1", Status.BLOCKED),
                ("job_2", Status.PENDING),
                ("job_2", Status.RUNNING),
                ("job_2", Status.CANCELED),
                ("job_1", Status.ABANDONED),
            ],
            [
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.PENDING,
                SubmissionStatus.RUNNING,
                SubmissionStatus.CANCELED,
                SubmissionStatus.CANCELED,
            ],
        ),
    ],
)
def test_update_submission_status_with_two_jobs_canceled(job_ids, job_statuses, expected_submission_statuses):
    __test_update_submission_status_with_two_jobs(job_ids, job_statuses, expected_submission_statuses)


def test_is_finished():
    submission_manager = _SubmissionManagerFactory._build_manager()

    submission = Submission("entity_id", "entity_type", "entity_config_id", "submission_id")
    submission_manager._set(submission)

    assert len(submission_manager._get_all()) == 1

    assert submission._submission_status == SubmissionStatus.SUBMITTED
    assert not submission.is_finished()

    submission.submission_status = SubmissionStatus.UNDEFINED
    assert submission.submission_status == SubmissionStatus.UNDEFINED
    assert not submission.is_finished()

    submission.submission_status = SubmissionStatus.CANCELED
    assert submission.submission_status == SubmissionStatus.CANCELED
    assert submission.is_finished()

    submission.submission_status = SubmissionStatus.FAILED
    assert submission.submission_status == SubmissionStatus.FAILED
    assert submission.is_finished()

    submission.submission_status = SubmissionStatus.BLOCKED
    assert submission.submission_status == SubmissionStatus.BLOCKED
    assert not submission.is_finished()

    submission.submission_status = SubmissionStatus.RUNNING
    assert submission.submission_status == SubmissionStatus.RUNNING
    assert not submission.is_finished()

    submission.submission_status = SubmissionStatus.PENDING
    assert submission.submission_status == SubmissionStatus.PENDING
    assert not submission.is_finished()

    submission.submission_status = SubmissionStatus.COMPLETED
    assert submission.submission_status == SubmissionStatus.COMPLETED
    assert submission.is_finished()
