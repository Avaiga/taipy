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
from taipy.core.data._data_sql_repository import _DataSQLRepository
from taipy.core.exceptions import ModelNotFound
from taipy.core.task._task_fs_repository import _TaskFSRepository
from taipy.core.task._task_sql_repository import _TaskSQLRepository
from taipy.core.task.task import Task, TaskId


class TestTaskFSRepository:
    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_save_and_load(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        repository._save(task)

        obj = repository._load(task.id)
        assert isinstance(obj, Task)

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_exists(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        repository._save(task)

        assert repository._exists(task.id)
        assert not repository._exists("not-existed-task")

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_load_all(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_load_all_with_filters(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task.owner_id = f"owner-{i}"
            repository._save(task)
        objs = repository._load_all(filters=[{"owner_id": "owner-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_delete(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        repository._save(task)

        repository._delete(task.id)

        with pytest.raises(ModelNotFound):
            repository._load(task.id)

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_delete_all(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_delete_many(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            repository._save(task)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_delete_by(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task._version = f"{(i+1) // 5}.0"
            repository._save(task)

        objs = repository._load_all()
        assert len(objs) == 10
        repository._delete_by("version", "1.0")

        assert len(repository._load_all()) == 5

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_search(self, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node], version="random_version_number")

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task.owner_id = f"owner-{i}"
            repository._save(task)

        assert len(repository._load_all()) == 10

        objs = repository._search("owner_id", "owner-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Task)

        objs = repository._search("owner_id", "owner-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Task)

        assert repository._search("owner_id", "owner-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [_TaskFSRepository, _TaskSQLRepository])
    def test_export(self, tmpdir, data_node, repo, init_sql_repo):
        repository = repo()
        _DataSQLRepository()._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        repository._save(task)

        repository._export(task.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _TaskFSRepository else os.path.join(tmpdir.strpath, "task")

        assert os.path.exists(os.path.join(dir_path, f"{task.id}.json"))
