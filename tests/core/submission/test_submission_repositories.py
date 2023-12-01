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

import os

import pytest
from src.taipy.config.config import Config
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.exceptions import ModelNotFound
from src.taipy.core.job._job_manager_factory import _JobManagerFactory
from src.taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from src.taipy.core.submission.submission import Submission
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task
from tests.core.conftest import init_sql_repo


def configure_fs_repo():
    Config.configure_core(repository_type="default")


def configure_sql_repo():
    init_sql_repo


class TestSubmissionRepository:
    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_save_and_load(self, data_node, job, configure_repo):
        configure_repo()

        _DataManagerFactory._build_manager()._repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskManagerFactory._build_manager()._repository._save(task)
        job._task = task
        _JobManagerFactory._build_manager()._repository._save(job)

        submission = Submission(task.id)
        submission_repository = _SubmissionManagerFactory._build_manager()._repository
        submission_repository._save(submission)
        submission.jobs = [job]

        obj = submission_repository._load(submission.id)
        assert isinstance(obj, Submission)

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_exists(self, configure_repo):
        configure_repo()

        submission = Submission("entity_id")
        submission_repository = _SubmissionManagerFactory._build_manager()._repository
        submission_repository._save(submission)

        assert submission_repository._exists(submission.id)
        assert not submission_repository._exists("not-existed-submission")

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_load_all(self, configure_repo):
        configure_repo()

        repository = _SubmissionManagerFactory._build_manager()._repository
        submission = Submission("entity_id")
        for i in range(10):
            submission.id = f"submission-{i}"
            repository._save(submission)
        submissions = repository._load_all()

        assert len(submissions) == 10

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_delete(self, configure_repo):
        configure_repo()

        repository = _SubmissionManagerFactory._build_manager()._repository

        submission = Submission("entity_id")
        repository._save(submission)

        repository._delete(submission.id)

        with pytest.raises(ModelNotFound):
            repository._load(submission.id)

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_delete_all(self, configure_repo):
        configure_repo()

        submission_repository = _SubmissionManagerFactory._build_manager()._repository
        submission = Submission("entity_id")

        for i in range(10):
            submission.id = f"submission-{i}"
            submission_repository._save(submission)

        assert len(submission_repository._load_all()) == 10

        submission_repository._delete_all()

        assert len(submission_repository._load_all()) == 0

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_delete_many(self, configure_repo):
        configure_repo()

        submission = Submission("entity_id")
        submission_repository = _SubmissionManagerFactory._build_manager()._repository

        for i in range(10):
            submission.id = f"submission-{i}"
            submission_repository._save(submission)

        objs = submission_repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        submission_repository._delete_many(ids)

        assert len(submission_repository._load_all()) == 7

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_delete_by(self, configure_repo):
        configure_repo()

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        submission_repository = _SubmissionManagerFactory._build_manager()._repository
        submission = Submission("entity_id")

        for i in range(10):
            submission.id = f"submission-{i}"
            submission._version = f"{(i+1) // 5}.0"
            submission_repository._save(submission)

        objs = submission_repository._load_all()
        assert len(objs) == 10
        submission_repository._delete_by("version", "1.0")

        assert len(submission_repository._load_all()) == 5

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_search(self, configure_repo):
        configure_repo()

        submission_repository = _SubmissionManagerFactory._build_manager()._repository
        submission = Submission("entity_id", version="random_version_number")
        for i in range(10):
            submission.id = f"submission-{i}"
            submission_repository._save(submission)

        assert len(submission_repository._load_all()) == 10

        objs = submission_repository._search("id", "submission-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Submission)

        objs = submission_repository._search("id", "submission-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Submission)

        assert submission_repository._search("id", "submission-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("configure_repo", [configure_fs_repo, configure_sql_repo])
    def test_export(self, tmpdir, configure_repo):
        configure_repo()

        repository = _SubmissionManagerFactory._build_manager()._repository
        submission = Submission("entity_id")
        repository._save(submission)

        repository._export(submission.id, tmpdir.strpath)
        dir_path = (
            repository.dir_path
            if Config.core.repository_type == "default"
            else os.path.join(tmpdir.strpath, "submission")
        )

        assert os.path.exists(os.path.join(dir_path, f"{submission.id}.json"))
