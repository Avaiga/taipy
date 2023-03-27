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
from src.taipy.core.task._task_fs_repository_v2 import _TaskFSRepository
from src.taipy.core.task.task import Task, TaskId


class TestTaskFSRepository:
    def test_save_and_load(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        repository._save(task)

        obj = repository._load(task.id)
        assert isinstance(obj, Task)

    def test_load_all(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    def test_load_all_with_filters(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task.owner_id = f"owner-{i}"
            repository._save(task)
        objs = repository._load_all(filters=[{"owner_id": "owner-2"}])

        assert len(objs) == 1

    def test_delete(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        repository._save(task)

        repository._delete(task.id)

        with pytest.raises(ModelNotFound):
            repository._load(task.id)

    def test_delete_all(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_search(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task.owner_id = f"owner-{i}"
            repository._save(task)

        assert len(repository._load_all()) == 10

        obj = repository._search("owner_id", "owner-2")

        assert isinstance(obj, Task)

    def test_export(self, tmpdir, data_node):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        _DataFSRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        repository._save(task)

        repository._export(task.id, tmpdir.strpath)
        assert os.path.exists(os.path.join(repository.dir_path, f"{task.id}.json"))
