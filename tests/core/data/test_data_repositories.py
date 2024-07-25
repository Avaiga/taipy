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
from taipy.core.data.data_node import DataNode, DataNodeId
from taipy.core.exceptions import ModelNotFound


class TestDataNodeRepository:
    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_save_and_load(self, data_node: DataNode, repo):
        repository = repo()
        repository._save(data_node)

        loaded_data_node = repository._load(data_node.id)
        assert isinstance(loaded_data_node, DataNode)
        assert data_node.id == loaded_data_node.id
        assert data_node._config_id == loaded_data_node._config_id
        assert data_node._owner_id == loaded_data_node._owner_id
        assert data_node._parent_ids == loaded_data_node._parent_ids
        assert data_node._scope == loaded_data_node._scope
        assert data_node._last_edit_date == loaded_data_node._last_edit_date
        assert data_node._edit_in_progress == loaded_data_node._edit_in_progress
        assert data_node._version == loaded_data_node._version
        assert data_node._validity_period == loaded_data_node._validity_period
        assert data_node._editor_id == loaded_data_node._editor_id
        assert data_node._editor_expiration_date == loaded_data_node._editor_expiration_date
        assert data_node._edits == loaded_data_node._edits
        assert data_node._properties == loaded_data_node._properties

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_exists(self, data_node, repo):
        repository = repo()
        repository._save(data_node)

        assert repository._exists(data_node.id)
        assert not repository._exists("not-existed-data-node")

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_load_all(self, data_node, repo):
        repository = repo()
        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_load_all_with_filters(self, data_node, repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node._owner_id = f"task-{i}"
            repository._save(data_node)
        objs = repository._load_all(filters=[{"owner_id": "task-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_delete(self, data_node, repo):
        repository = repo()
        repository._save(data_node)

        repository._delete(data_node.id)

        with pytest.raises(ModelNotFound):
            repository._load(data_node.id)

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_delete_all(self, data_node, repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_delete_many(self, data_node, repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_delete_by(self, data_node, repo):
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

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_search(self, data_node, repo):
        repository = repo()

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node._owner_id = f"task-{i}"
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        objs = repository._search("owner_id", "task-2")
        assert len(objs) == 1
        assert isinstance(objs[0], DataNode)

        objs = repository._search("owner_id", "task-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], DataNode)

        assert repository._search("owner_id", "task-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [_DataFSRepository])
    def test_export(self, tmpdir, data_node, repo):
        repository = repo()
        repository._save(data_node)

        repository._export(data_node.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _DataFSRepository else os.path.join(tmpdir.strpath, "data_node")

        assert os.path.exists(os.path.join(dir_path, f"{data_node.id}.json"))
