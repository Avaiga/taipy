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

import datetime
import os
from unittest import mock

from src.taipy.core.data._data_converter import _DataNodeConverter
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.data_node_id import DataNodeId
from taipy.config.common.scope import Scope
from taipy.config.config import Config


class TestDataRepository:
    data_node = CSVDataNode(
        "test_data_node",
        Scope.PIPELINE,
        DataNodeId("my_dn_id"),
        "name",
        "owner_id",
        set(["parent_id_1", "parent_id_2"]),
        datetime.datetime(1985, 10, 14, 2, 30, 0),
        [dict(timestamp=datetime.datetime(1985, 10, 14, 2, 30, 0), job_id="job_id")],
        "latest",
        None,
        False,
        {"path": "/path", "has_header": True, "prop": "ENV[FOO]", "exposed_type": "pandas"},
    )

    def test_save_and_load(self, tmpdir):
        repository = _DataManagerFactory._build_repository()
        repository.base_path = tmpdir
        repository._save(self.data_node)
        dn = repository._load("my_dn_id")

        assert isinstance(dn, CSVDataNode)
        assert isinstance(dn, DataNode)

    def test_from_and_to_model(self, data_node_model):
        assert _DataNodeConverter._entity_to_model(self.data_node) == data_node_model
        assert _DataNodeConverter._model_to_entity(data_node_model) == self.data_node

    def test_data_node_with_env_variable_value_not_serialized(self):
        with mock.patch.dict(os.environ, {"FOO": "bar"}):
            assert _DataNodeConverter._entity_to_model(self.data_node).data_node_properties["prop"] == "ENV[FOO]"
            assert self.data_node._properties.data["prop"] == "ENV[FOO]"
            assert self.data_node.properties["prop"] == "bar"
            assert self.data_node.prop == "bar"

    def test_save_and_load_with_sql_repo(self, tmpdir):
        Config.configure_global_app(repository_type="sql")

        repository = _DataManagerFactory._build_repository()

        repository._save(self.data_node)
        dn = repository._load("my_dn_id")

        assert isinstance(dn, CSVDataNode)
        assert isinstance(dn, DataNode)

    def test_from_and_to_model_with_sql_repo(self, data_node_model):
        Config.configure_global_app(repository_type="sql")

        repository = _DataManagerFactory._build_repository().repo._table
        assert repository._to_model(self.data_node) == data_node_model
        assert repository._from_model(data_node_model) == self.data_node

    def test_data_node_with_env_variable_value_not_serialized_with_sql_repo(self):
        Config.configure_global_app(repository_type="sql")

        with mock.patch.dict(os.environ, {"FOO": "bar"}):
            repository = _DataManagerFactory._build_repository().repo._table
            assert repository._to_model(self.data_node).data_node_properties["prop"] == "ENV[FOO]"
            assert self.data_node._properties.data["prop"] == "ENV[FOO]"
            assert self.data_node.properties["prop"] == "bar"
            assert self.data_node.prop == "bar"
