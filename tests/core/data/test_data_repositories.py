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

from src.taipy.core.data._data_fs_repository import _DataFSRepository
from src.taipy.core.data._data_sql_repository import _DataSQLRepository
from src.taipy.core.data.data_node import DataNode, DataNodeId
from src.taipy.core.exceptions import ModelNotFound


class TestDataNodeRepository:
    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_save_and_load(self, data_node, repo, init_sql_repo):
        repository = repo()
        repository._save(data_node)

        obj = repository._load(data_node.id)
        assert isinstance(obj, DataNode)

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_exists(self, data_node, repo, init_sql_repo):
        repository = repo()
        repository._save(data_node)

        assert repository._exists(data_node.id)
        assert not repository._exists("not-existed-data-node")

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_load_all(self, data_node, repo, init_sql_repo):
        repository = repo()
        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_load_all_with_filters(self, data_node, repo, init_sql_repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node.owner_id = f"task-{i}"
            repository._save(data_node)
        objs = repository._load_all(filters=[{"owner_id": "task-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_delete(self, data_node, repo, init_sql_repo):
        repository = repo()
        repository._save(data_node)

        repository._delete(data_node.id)

        with pytest.raises(ModelNotFound):
            repository._load(data_node.id)

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_delete_all(self, data_node, repo, init_sql_repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_delete_many(self, data_node, repo, init_sql_repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_delete_by(self, data_node, repo, init_sql_repo):
        repository = repo()

        # Create 5 entities with version 1.0 and 5 entities with version 2.0
        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node._version = f"{(i+1) // 5}.0"
            repository._save(data_node)

        objs = repository._load_all()
        assert len(objs) == 10
        repository._delete_by("version", "1.0")

        assert len(repository._load_all()) == 5

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_search(self, data_node, repo, init_sql_repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node.owner_id = f"task-{i}"
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        objs = repository._search("owner_id", "task-2")
        assert len(objs) == 1
        assert isinstance(objs[0], DataNode)

        objs = repository._search("owner_id", "task-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], DataNode)

        assert repository._search("owner_id", "task-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [_DataFSRepository, _DataSQLRepository])
    def test_export(self, tmpdir, data_node, repo, init_sql_repo):
        repository = repo()
        repository._save(data_node)

        repository._export(data_node.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _DataFSRepository else os.path.join(tmpdir.strpath, "data_node")

        assert os.path.exists(os.path.join(dir_path, f"{data_node.id}.json"))
