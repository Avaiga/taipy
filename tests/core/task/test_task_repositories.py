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

from taipy.config.config import Config
from taipy.core.data._data_fs_repository import _DataFSRepository
from taipy.core.data._data_sql_repository import _DataSQLRepository
from taipy.core.exceptions import ModelNotFound
from taipy.core.task._task_fs_repository import _TaskFSRepository
from taipy.core.task._task_sql_repository import _TaskSQLRepository
from taipy.core.task.task import Task, TaskId


class TestTaskFSRepository:
    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_save_and_load(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        task_repository._save(task)

        loaded_task = task_repository._load(task.id)
        assert isinstance(loaded_task, Task)
        assert task._config_id == loaded_task._config_id
        assert task.id == loaded_task.id
        assert task._owner_id == loaded_task._owner_id
        assert task._parent_ids == loaded_task._parent_ids
        assert task._input == loaded_task._input
        assert task._output == loaded_task._output
        assert task._function == loaded_task._function
        assert task._version == loaded_task._version
        assert task._skippable == loaded_task._skippable
        assert task._properties == loaded_task._properties

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_exists(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        task_repository._save(task)

        assert task_repository._exists(task.id)
        assert not task_repository._exists("not-existed-task")

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_load_all(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task_repository._save(task)
        data_nodes = task_repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_load_all_with_filters(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task._owner_id = f"owner-{i}"
            task_repository._save(task)
        objs = task_repository._load_all(filters=[{"owner_id": "owner-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_delete(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        task_repository._save(task)

        task_repository._delete(task.id)

        with pytest.raises(ModelNotFound):
            task_repository._load(task.id)

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_delete_all(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task_repository._save(task)

        assert len(task_repository._load_all()) == 10

        task_repository._delete_all()

        assert len(task_repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_delete_many(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task_repository._save(task)

        objs = task_repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        task_repository._delete_many(ids)

        assert len(task_repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_delete_by(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task._version = f"{(i+1) // 5}.0"
            task_repository._save(task)

        objs = task_repository._load_all()
        assert len(objs) == 10
        task_repository._delete_by("version", "1.0")

        assert len(task_repository._load_all()) == 5

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_search(self, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node], version="random_version_number")

        for i in range(10):
            task.id = TaskId(f"task-{i}")
            task._owner_id = f"owner-{i}"
            task_repository._save(task)

        assert len(task_repository._load_all()) == 10

        objs = task_repository._search("owner_id", "owner-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Task)

        objs = task_repository._search("owner_id", "owner-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Task)

        assert task_repository._search("owner_id", "owner-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [(_TaskFSRepository, _DataFSRepository), (_TaskSQLRepository, _DataSQLRepository)])
    def test_export(self, tmpdir, data_node, repo, tmp_sqlite):
        if repo[1] == _DataSQLRepository:
            Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        task_repository, data_repository = repo[0](), repo[1]()
        data_repository._save(data_node)
        task = Task("task_config_id", {}, print, [data_node], [data_node])
        task_repository._save(task)

        task_repository._export(task.id, tmpdir.strpath)
        dir_path = task_repository.dir_path if repo[0] == _TaskFSRepository else os.path.join(tmpdir.strpath, "task")

        assert os.path.exists(os.path.join(dir_path, f"{task.id}.json"))
