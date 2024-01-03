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

from taipy.core import Task
from taipy.core._repository.db._sql_connection import _SQLConnection
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.submission.submission import Submission
from taipy.core.submission.submission_status import SubmissionStatus


def init_managers():
    _VersionManagerFactory._build_manager()._delete_all()
    _SubmissionManagerFactory._build_manager()._delete_all()


def test_create_submission(scenario, init_sql_repo):
    init_managers()

    submission_1 = _SubmissionManagerFactory._build_manager()._create(
        scenario.id, scenario._ID_PREFIX, scenario.config_id
    )

    assert submission_1.id is not None
    assert submission_1.entity_id == scenario.id
    assert submission_1.jobs == []
    assert isinstance(submission_1.creation_date, datetime)
    assert submission_1._submission_status == SubmissionStatus.SUBMITTED


def test_get_submission(init_sql_repo):
    init_managers()

    submission_manager = _SubmissionManagerFactory._build_manager()

    submission_1 = submission_manager._create("entity_id", "ENTITY_TYPE", "entity_config_id")
    submission_2 = submission_manager._get(submission_1.id)

    assert submission_1.id == submission_2.id
    assert submission_1.entity_id == submission_2.entity_id == "entity_id"
    assert submission_1.jobs == submission_2.jobs
    assert submission_1.creation_date == submission_2.creation_date
    assert submission_1.submission_status == submission_2.submission_status


def test_get_all_submission(init_sql_repo):
    init_managers()

    submission_manager = _SubmissionManagerFactory._build_manager()
    version_manager = _VersionManagerFactory._build_manager()

    submission_manager._set(
        Submission("entity_id", "submission_id", "entity_config_id", version=version_manager._get_latest_version())
    )
    for version_name in ["abc", "xyz"]:
        for i in range(10):
            submission_manager._set(
                Submission("entity_id", f"submission_{version_name}_{i}", "entity_config_id", version=f"{version_name}")
            )
    assert len(submission_manager._get_all()) == 1

    version_manager._set_experiment_version("xyz")
    version_manager._set_experiment_version("abc")
    assert len(submission_manager._get_all()) == 10
    assert len(submission_manager._get_all("abc")) == 10
    assert len(submission_manager._get_all("xyz")) == 10


def test_get_latest_submission(init_sql_repo):
    init_managers()

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


def test_delete_submission(init_sql_repo):
    init_managers()

    submission_manager = _SubmissionManagerFactory._build_manager()

    submission = Submission("entity_id", "submission_id", "entity_config_id")
    submission_manager._set(submission)

    for i in range(10):
        submission_manager._set(Submission("entity_id", f"submission_{i}", "entity_config_id"))

    assert len(submission_manager._get_all()) == 11
    assert isinstance(submission_manager._get(submission.id), Submission)

    submission_manager._delete(submission.id)
    assert len(submission_manager._get_all()) == 10
    assert submission_manager._get(submission.id) is None

    submission_manager._delete_all()
    assert len(submission_manager._get_all()) == 0
