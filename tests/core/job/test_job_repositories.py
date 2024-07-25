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

import os

import pytest

from taipy.core.data._data_fs_repository import _DataFSRepository
from taipy.core.exceptions import ModelNotFound
from taipy.core.job._job_fs_repository import _JobFSRepository
from taipy.core.job.job import Job, JobId
from taipy.core.task._task_fs_repository import _TaskFSRepository
from taipy.core.task.task import Task


class TestJobRepository:
    def test_save_and_load(self, data_node, job):
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        repository = _JobFSRepository()
        repository._save(job)

        obj = repository._load(job.id)
        assert isinstance(obj, Job)

    def test_exists(self, data_node, job):
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task
        repository = _JobFSRepository()
        repository._save(job)

        assert repository._exists(job.id)
        assert not repository._exists("not-existed-job")

    def test_load_all(self, data_node, job):
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task
        repository = _JobFSRepository()
        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)
        jobs = repository._load_all()

        assert len(jobs) == 10

    def test_load_all_with_filters(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)
        objs = repository._load_all(filters=[{"id": "job-2"}])

        assert len(objs) == 1

    def test_delete(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task
        repository._save(job)

        repository._delete(job.id)

        with pytest.raises(ModelNotFound):
            repository._load(job.id)

    def test_delete_all(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_delete_by(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        for i in range(10):
            job.id = JobId(f"job-{i}")
            job._version = f"{(i+1) // 5}.0"
            repository._save(job)

        objs = repository._load_all()
        assert len(objs) == 10
        repository._delete_by("version", "1.0")

        assert len(repository._load_all()) == 5

    def test_search(self, data_node, job):
        repository = _JobFSRepository()
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)

        assert len(repository._load_all()) == 10

        objs = repository._search("id", "job-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Job)

        objs = repository._search("id", "job-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Job)

        assert repository._search("id", "job-2", filters=[{"version": "non_existed_version"}]) == []

    def test_export(self, tmpdir, job):
        repository = _JobFSRepository()
        repository._save(job)

        repository._export(job.id, tmpdir.strpath)
        dir_path = repository.dir_path

        assert os.path.exists(os.path.join(dir_path, f"{job.id}.json"))
