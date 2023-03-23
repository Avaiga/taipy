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
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.exceptions import ModelNotFound
from taipy.core import DataNodeId


class TestDataNodeFSRepository:
    def test_save_and_load(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir
        repository._save(data_node)

        obj = repository._load(data_node.id)
        assert isinstance(obj, DataNode)

    def test_load_all(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir
        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    def test_load_all_with_filters(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node.name = f"data_node-{i}"
            repository._save(data_node)
        objs = repository._load_all(filters=[{"name": "data_node-2"}])

        assert len(objs) == 1

    def test_delete(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir
        repository._save(data_node)

        repository._delete(data_node.id)

        with pytest.raises(ModelNotFound):
            repository._load(data_node.id)

    def test_delete_all(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            repository._save(data_node)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_search(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            data_node.id = DataNodeId(f"data_node-{i}")
            data_node.name = f"data_node-{i}"
            repository._save(data_node)

        assert len(repository._load_all()) == 10

        obj = repository._search("name", "data_node-2")

        assert isinstance(obj, DataNode)

    def test_export(self, tmpdir, data_node):
        repository = _DataFSRepository()
        repository.base_path = tmpdir
        repository._save(data_node)

        repository._export(data_node.id, tmpdir.strpath)
        assert os.path.exists(os.path.join(repository.dir_path, f"{data_node.id}.json"))
