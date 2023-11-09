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
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from src.taipy.core.submission.submission import Submission
from src.taipy.core.submission.submission_status import SubmissionStatus
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task


def test_create_submission(scenario):
    _ScenarioManagerFactory._build_manager()._set(scenario)
    submission = _SubmissionManagerFactory._build_manager()._create(scenario.id)

    assert submission.id is not None
    assert submission.entity_id == scenario.id
    assert submission.jobs == []
    assert isinstance(submission.creation_date, datetime)
    assert submission._submission_status == SubmissionStatus.UNDEFINED


def test_update_submission_status():
    pass


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
