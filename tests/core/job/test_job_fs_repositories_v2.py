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

from src.taipy.core.data._data_fs_repository_v2 import _DataFSRepository
from src.taipy.core.exceptions import ModelNotFound
from src.taipy.core.job._job_fs_repository_v2 import _JobFSRepository
from src.taipy.core.job.job import Job
from src.taipy.core.task._task_fs_repository_v2 import _TaskFSRepository
from taipy.config import Scope
from taipy.core import JobId, Task


class TestJobFSRepository:
    def test_save_and_load(self, tmpdir, data_node, job):
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        repository = _JobFSRepository()
        repository.base_path = tmpdir
        repository._save(job)

        obj = repository._load(job.id)
        assert isinstance(obj, Job)

    def test_load_all(self, tmpdir, data_node, job):
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)
        jobs = repository._load_all()

        assert len(jobs) == 10

    def test_load_all_with_filters(self, tmpdir, data_node, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)
        objs = repository._load_all(filters=[{"id": "job-2"}])

        assert len(objs) == 1

    def test_delete(self, tmpdir, data_node, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task
        repository._save(job)

        repository._delete(job.id)

        with pytest.raises(ModelNotFound):
            repository._load(job.id)

    def test_delete_all(self, tmpdir, data_node, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
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

    def test_delete_many(self, tmpdir, data_node, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
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

    def test_search(self, tmpdir, data_node, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        _TaskFSRepository()._save(task)
        job._task = task

        for i in range(10):
            job.id = JobId(f"job-{i}")
            repository._save(job)

        assert len(repository._load_all()) == 10

        obj = repository._search("id", "job-2")

        assert isinstance(obj, Job)

    def test_export(self, tmpdir, job):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        repository._save(job)

        repository._export(job.id, tmpdir.strpath)
        assert os.path.exists(os.path.join(repository.dir_path, f"{job.id}.json"))
