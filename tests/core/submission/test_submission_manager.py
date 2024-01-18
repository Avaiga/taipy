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
from time import sleep

import pytest

from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.exceptions.exceptions import SubmissionNotDeletedException
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission import Submission
from taipy.core.submission.submission_status import SubmissionStatus
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def test_create_submission(scenario):
    submission_1 = _SubmissionManagerFactory._build_manager()._create(
        scenario.id, scenario._ID_PREFIX, scenario.config_id, debug=True, log="log_file", retry_note=5
    )

    assert isinstance(submission_1, Submission)
    assert submission_1.id is not None
    assert submission_1.entity_id == scenario.id
    assert submission_1.jobs == []
    assert submission_1.properties == {"debug": True, "log": "log_file", "retry_note": 5}
    assert isinstance(submission_1.creation_date, datetime)
    assert submission_1._submission_status == SubmissionStatus.SUBMITTED


def test_get_submission():
    submission_manager = _SubmissionManagerFactory._build_manager()

    assert submission_manager._get("random_submission_id") is None

    submission_1 = submission_manager._create(
        "entity_id", "ENTITY_TYPE", "entity_config_id", debug=True, log="log_file", retry_note=5
    )
    submission_2 = submission_manager._get(submission_1.id)

    assert submission_1.id == submission_2.id
    assert submission_1.entity_id == submission_2.entity_id == "entity_id"
    assert submission_1.jobs == submission_2.jobs
    assert submission_1.creation_date == submission_2.creation_date
    assert submission_1.submission_status == submission_2.submission_status
    assert submission_1.properties == {"debug": True, "log": "log_file", "retry_note": 5}
    assert submission_1.properties == submission_2.properties


def test_get_all_submission():
    submission_manager = _SubmissionManagerFactory._build_manager()
    version_manager = _VersionManagerFactory._build_manager()

    submission_manager._set(
        Submission(
            "entity_id",
            "entity_type",
            "entity_config_id",
            "submission_id",
            version=version_manager._get_latest_version(),
        )
    )
    for version_name in ["abc", "xyz"]:
        for i in range(10):
            submission_manager._set(
                Submission(
                    "entity_id",
                    "entity_type",
                    "entity_config_id",
                    f"submission_{version_name}_{i}",
                    version=f"{version_name}",
                )
            )

    assert len(submission_manager._get_all()) == 1

    version_manager._set_experiment_version("xyz")
    version_manager._set_experiment_version("abc")
    assert len(submission_manager._get_all()) == 10
    assert len(submission_manager._get_all("abc")) == 10
    assert len(submission_manager._get_all("xyz")) == 10


def test_get_latest_submission():
    task_1 = Task("task_config_1", {}, print, id="task_id_1")
    task_2 = Task("task_config_2", {}, print, id="task_id_2")

    submission_manager = _SubmissionManagerFactory._build_manager()
    submission_1 = submission_manager._create(task_1.id, task_1._ID_PREFIX, task_1.config_id)
    assert submission_manager._get_latest(task_1) == submission_1
    assert submission_manager._get_latest(task_2) is None

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    submission_2 = submission_manager._create(task_2.id, task_2._ID_PREFIX, task_2.config_id)
    assert submission_manager._get_latest(task_1) == submission_1
    assert submission_manager._get_latest(task_2) == submission_2

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    submission_3 = submission_manager._create(task_1.id, task_1._ID_PREFIX, task_1.config_id)
    assert submission_manager._get_latest(task_1) == submission_3
    assert submission_manager._get_latest(task_2) == submission_2

    sleep(0.01)  # Comparison is based on time, precision on Windows is not enough important
    submission_4 = submission_manager._create(task_2.id, task_2._ID_PREFIX, task_2.config_id)
    assert submission_manager._get_latest(task_1) == submission_3
    assert submission_manager._get_latest(task_2) == submission_4


def test_delete_submission():
    submission_manager = _SubmissionManagerFactory._build_manager()

    submission = Submission("entity_id", "entity_type", "entity_config_id", "submission_id")

    submission_manager._set(submission)

    with pytest.raises(SubmissionNotDeletedException):
        submission_manager._delete(submission.id)

    submission.submission_status = SubmissionStatus.COMPLETED

    for i in range(10):
        submission_manager._set(Submission("entity_id", "entity_type", "entity_config_id", f"submission_{i}"))

    assert len(submission_manager._get_all()) == 11
    assert isinstance(submission_manager._get(submission.id), Submission)

    submission_manager._delete(submission.id)
    assert len(submission_manager._get_all()) == 10
    assert submission_manager._get(submission.id) is None

    submission_manager._delete_all()
    assert len(submission_manager._get_all()) == 0


def test_is_deletable():
    submission_manager = _SubmissionManagerFactory._build_manager()

    submission = Submission("entity_id", "entity_type", "entity_config_id", "submission_id")
    submission_manager._set(submission)

    assert len(submission_manager._get_all()) == 1

    assert submission._submission_status == SubmissionStatus.SUBMITTED
    assert not submission.is_deletable()
    assert not submission_manager._is_deletable(submission)
    assert not submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.UNDEFINED
    assert submission.submission_status == SubmissionStatus.UNDEFINED
    assert submission.is_deletable()
    assert submission_manager._is_deletable(submission)
    assert submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.CANCELED
    assert submission.submission_status == SubmissionStatus.CANCELED
    assert submission.is_deletable()
    assert submission_manager._is_deletable(submission)
    assert submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.FAILED
    assert submission.submission_status == SubmissionStatus.FAILED
    assert submission.is_deletable()
    assert submission_manager._is_deletable(submission)
    assert submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.BLOCKED
    assert submission.submission_status == SubmissionStatus.BLOCKED
    assert not submission.is_deletable()
    assert not submission_manager._is_deletable(submission)
    assert not submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.RUNNING
    assert submission.submission_status == SubmissionStatus.RUNNING
    assert not submission.is_deletable()
    assert not submission_manager._is_deletable(submission)
    assert not submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.PENDING
    assert submission.submission_status == SubmissionStatus.PENDING
    assert not submission.is_deletable()
    assert not submission_manager._is_deletable(submission)
    assert not submission_manager._is_deletable(submission.id)

    submission.submission_status = SubmissionStatus.COMPLETED
    assert submission.submission_status == SubmissionStatus.COMPLETED
    assert submission.is_deletable()
    assert submission_manager._is_deletable(submission)
    assert submission_manager._is_deletable(submission.id)


def test_hard_delete():
    submission_manager = _SubmissionManagerFactory._build_manager()
    job_manager = _JobManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()

    task = Task("task_config_id", {}, print)
    submission = Submission(task.id, task._ID_PREFIX, task.config_id, "SUBMISSION_submission_id")
    job_1 = Job("JOB_job_id_1", task, submission.id, submission.entity_id)  # will be deleted with submission
    job_2 = Job("JOB_job_id_2", task, "SUBMISSION_submission_id_2", submission.entity_id)  # will not be deleted
    submission.jobs = [job_1]

    task_manager._set(task)
    submission_manager._set(submission)
    job_manager._set(job_1)
    job_manager._set(job_2)

    assert len(job_manager._get_all()) == 2
    assert len(submission_manager._get_all()) == 1
    submission_manager._hard_delete(submission.id)
    assert len(job_manager._get_all()) == 1
    assert len(submission_manager._get_all()) == 0
