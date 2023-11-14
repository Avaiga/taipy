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

from datetime import datetime

import pytest

from src.taipy.core import TaskId
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.job.job import Job
from src.taipy.core.job.status import Status
from src.taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from src.taipy.core.submission.submission import Submission
from src.taipy.core.submission.submission_status import SubmissionStatus
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task


def test_create_submission(scenario, job, current_datetime):
    submission_1 = Submission(scenario.id)

    assert submission_1.id is not None
    assert submission_1.entity_id == scenario.id
    assert submission_1.jobs == []
    assert isinstance(submission_1.creation_date, datetime)
    assert submission_1._submission_status == SubmissionStatus.UNDEFINED
    assert submission_1._version is not None

    submission_2 = Submission(
        scenario.id, "submission_id", [job], current_datetime, SubmissionStatus.COMPLETED, "version_id"
    )

    assert submission_2.id == "submission_id"
    assert submission_2.entity_id == scenario.id
    assert submission_2._jobs == [job]
    assert submission_2.creation_date == current_datetime
    assert submission_2._submission_status == SubmissionStatus.COMPLETED
    assert submission_2._version == "version_id"


def __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task):
    _TaskManagerFactory._build_manager()._set(task)

    submission = Submission(task.id)
    jobs = []
    for job_id, job_status in zip(job_ids, job_statuses):
        job = Job(job_id, task, submission.id, submission.entity_id)
        job._status = job_status
        _JobManagerFactory._build_manager()._set(job)
        jobs.append(job)

    _SubmissionManagerFactory._build_manager()._set(submission)

    submission.jobs = jobs

    assert submission.submission_status == SubmissionStatus.UNDEFINED
    submission._update_submission_status()
    assert submission.submission_status == expected_submission_status


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job1_failed"], [Status.FAILED], SubmissionStatus.FAILED),
        (["job2_canceled"], [Status.CANCELED], SubmissionStatus.CANCELED),
        (["job3_blocked"], [Status.BLOCKED], SubmissionStatus.BLOCKED),
        (["job4_pending"], [Status.PENDING], SubmissionStatus.PENDING),
        (["job5_running"], [Status.RUNNING], SubmissionStatus.RUNNING),
        (["job6_completed"], [Status.COMPLETED], SubmissionStatus.COMPLETED),
        (["job7_skipped"], [Status.COMPLETED], SubmissionStatus.COMPLETED),
        (["job8_abandoned"], [Status.ABANDONED], SubmissionStatus.UNDEFINED),
    ],
)
def test_update_single_submission_status(job_ids, job_statuses, expected_submission_status, task):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job1_failed", "job1_failed"], [Status.FAILED, Status.FAILED], SubmissionStatus.FAILED),
        (["job1_failed", "job2_canceled"], [Status.FAILED, Status.CANCELED], SubmissionStatus.FAILED),
        (["job1_failed", "job3_blocked"], [Status.FAILED, Status.BLOCKED], SubmissionStatus.FAILED),
        (["job1_failed", "job4_pending"], [Status.FAILED, Status.PENDING], SubmissionStatus.FAILED),
        (["job1_failed", "job5_running"], [Status.FAILED, Status.RUNNING], SubmissionStatus.FAILED),
        (["job1_failed", "job6_completed"], [Status.FAILED, Status.COMPLETED], SubmissionStatus.FAILED),
        (["job1_failed", "job7_skipped"], [Status.FAILED, Status.SKIPPED], SubmissionStatus.FAILED),
        (["job1_failed", "job8_abandoned"], [Status.FAILED, Status.ABANDONED], SubmissionStatus.FAILED),
        (["job3_blocked", "job1_failed"], [Status.BLOCKED, Status.FAILED], SubmissionStatus.FAILED),
        (["job4_pending", "job1_failed"], [Status.PENDING, Status.FAILED], SubmissionStatus.FAILED),
        (["job5_running", "job1_failed"], [Status.RUNNING, Status.FAILED], SubmissionStatus.FAILED),
        (["job6_completed", "job1_failed"], [Status.COMPLETED, Status.FAILED], SubmissionStatus.FAILED),
        (["job7_skipped", "job1_failed"], [Status.SKIPPED, Status.FAILED], SubmissionStatus.FAILED),
        (["job8_abandoned", "job1_failed"], [Status.ABANDONED, Status.FAILED], SubmissionStatus.FAILED),
    ],
)
def test_update_submission_status_with_one_failed_job_in_jobs(job_ids, job_statuses, expected_submission_status, task):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job2_canceled", "job2_canceled"], [Status.CANCELED, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job2_canceled", "job3_blocked"], [Status.CANCELED, Status.BLOCKED], SubmissionStatus.CANCELED),
        (["job2_canceled", "job4_pending"], [Status.CANCELED, Status.PENDING], SubmissionStatus.CANCELED),
        (["job2_canceled", "job5_running"], [Status.CANCELED, Status.RUNNING], SubmissionStatus.CANCELED),
        (["job2_canceled", "job6_completed"], [Status.CANCELED, Status.COMPLETED], SubmissionStatus.CANCELED),
        (["job2_canceled", "job7_skipped"], [Status.CANCELED, Status.SKIPPED], SubmissionStatus.CANCELED),
        (["job2_canceled", "job8_abandoned"], [Status.CANCELED, Status.ABANDONED], SubmissionStatus.CANCELED),
        (["job2_canceled", "job1_failed"], [Status.CANCELED, Status.FAILED], SubmissionStatus.CANCELED),
        (["job3_blocked", "job2_canceled"], [Status.BLOCKED, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job4_pending", "job2_canceled"], [Status.PENDING, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job5_running", "job2_canceled"], [Status.RUNNING, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job6_completed", "job2_canceled"], [Status.COMPLETED, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job7_skipped", "job2_canceled"], [Status.SKIPPED, Status.CANCELED], SubmissionStatus.CANCELED),
        (["job8_abandoned", "job2_canceled"], [Status.ABANDONED, Status.CANCELED], SubmissionStatus.CANCELED),
    ],
)
def test_update_submission_status_with_one_canceled_job_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job4_pending", "job3_blocked"], [Status.PENDING, Status.BLOCKED], SubmissionStatus.PENDING),
        (["job4_pending", "job4_pending"], [Status.PENDING, Status.PENDING], SubmissionStatus.PENDING),
        (["job4_pending", "job6_completed"], [Status.PENDING, Status.COMPLETED], SubmissionStatus.PENDING),
        (["job4_pending", "job7_skipped"], [Status.PENDING, Status.SKIPPED], SubmissionStatus.PENDING),
        (["job3_blocked", "job4_pending"], [Status.BLOCKED, Status.PENDING], SubmissionStatus.PENDING),
        (["job6_completed", "job4_pending"], [Status.COMPLETED, Status.PENDING], SubmissionStatus.PENDING),
        (["job7_skipped", "job4_pending"], [Status.SKIPPED, Status.PENDING], SubmissionStatus.PENDING),
    ],
)
def test_update_submission_status_with_no_failed_or_cancel_one_pending_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job5_running", "job3_blocked"], [Status.RUNNING, Status.BLOCKED], SubmissionStatus.RUNNING),
        (["job5_running", "job4_pending"], [Status.RUNNING, Status.PENDING], SubmissionStatus.RUNNING),
        # (["job5_running", "job5_running"], [Status.RUNNING, Status.RUNNING], SubmissionStatus.RUNNING),
        # (["job5_running", "job6_completed"], [Status.RUNNING, Status.COMPLETED], SubmissionStatus.RUNNING),
        # (["job5_running", "job7_skipped"], [Status.RUNNING, Status.SKIPPED], SubmissionStatus.RUNNING),
        (["job3_blocked", "job5_running"], [Status.BLOCKED, Status.RUNNING], SubmissionStatus.RUNNING),
        (["job4_pending", "job5_running"], [Status.PENDING, Status.RUNNING], SubmissionStatus.RUNNING),
        # (["job6_completed", "job5_running"], [Status.COMPLETED, Status.RUNNING], SubmissionStatus.RUNNING),
        # (["job7_skipped", "job5_running"], [Status.SKIPPED, Status.RUNNING], SubmissionStatus.RUNNING),
    ],
)
def test_update_submission_status_with_no_failed_cancel_nor_pending_one_running_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job3_blocked", "job3_blocked"], [Status.BLOCKED, Status.BLOCKED], SubmissionStatus.BLOCKED),
        (["job3_blocked", "job6_completed"], [Status.BLOCKED, Status.COMPLETED], SubmissionStatus.BLOCKED),
        (["job3_blocked", "job7_skipped"], [Status.BLOCKED, Status.SKIPPED], SubmissionStatus.BLOCKED),
        (["job6_completed", "job3_blocked"], [Status.COMPLETED, Status.BLOCKED], SubmissionStatus.BLOCKED),
        (["job7_skipped", "job3_blocked"], [Status.SKIPPED, Status.BLOCKED], SubmissionStatus.BLOCKED),
    ],
)
def test_update_submission_status_with_no_failed_cancel_pending_nor_running_one_blocked_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job6_completed", "job6_completed"], [Status.COMPLETED, Status.COMPLETED], SubmissionStatus.COMPLETED),
        (["job6_completed", "job7_skipped"], [Status.COMPLETED, Status.SKIPPED], SubmissionStatus.COMPLETED),
        (["job7_skipped", "job6_completed"], [Status.SKIPPED, Status.COMPLETED], SubmissionStatus.COMPLETED),
        (["job7_skipped", "job7_skipped"], [Status.SKIPPED, Status.SKIPPED], SubmissionStatus.COMPLETED),
    ],
)
def test_update_submission_status_with_only_completed_or_skipped_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


@pytest.mark.parametrize(
    "job_ids, job_statuses, expected_submission_status",
    [
        (["job3_blocked", "job8_abandoned"], [Status.BLOCKED, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        (["job4_pending", "job8_abandoned"], [Status.PENDING, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        (["job5_running", "job8_abandoned"], [Status.RUNNING, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        (["job6_completed", "job8_abandoned"], [Status.COMPLETED, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        (["job7_skipped", "job8_abandoned"], [Status.SKIPPED, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        # (["job8_abandoned", "job8_abandoned"], [Status.ABANDONED, Status.ABANDONED], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job3_blocked"], [Status.ABANDONED, Status.BLOCKED], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job4_pending"], [Status.ABANDONED, Status.PENDING], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job5_running"], [Status.ABANDONED, Status.RUNNING], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job6_completed"], [Status.ABANDONED, Status.COMPLETED], SubmissionStatus.UNDEFINED),
        (["job8_abandoned", "job7_skipped"], [Status.ABANDONED, Status.SKIPPED], SubmissionStatus.UNDEFINED),
    ],
)
def test_update_submission_status_with_wrong_case_abandoned_without_cancel_or_failed_in_jobs(
    job_ids, job_statuses, expected_submission_status, task
):
    __test_update_submission_status(job_ids, job_statuses, expected_submission_status, task)


def test_auto_set_and_reload():
    task = Task(config_id="name_1", properties={}, function=print, id=TaskId("task_1"))
    submission_1 = Submission(task.id)
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

    # auto set & reload on submission_status attribute
    assert submission_1.submission_status == SubmissionStatus.UNDEFINED
    assert submission_2.submission_status == SubmissionStatus.UNDEFINED
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
