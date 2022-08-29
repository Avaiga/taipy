# Copyright 2022 Avaiga Private Limited
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

from src.taipy.core.common.alias import DataNodeId, JobId
from src.taipy.core.data._data_model import _DataNodeModel
from src.taipy.core.data._data_repository_factory import _DataRepositoryFactory
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.data.data_node import DataNode
from taipy.config.common.scope import Scope


class TestDataRepository:

    data_node = CSVDataNode(
        "test_data_node",
        Scope.PIPELINE,
        DataNodeId("my_dn_id"),
        "name",
        "parent_id",
        datetime.datetime(1985, 10, 14, 2, 30, 0),
        [JobId("job_id")],
        None,
        False,
        {"path": "/path", "has_header": True, "prop": "ENV[FOO]"},
    )

    data_node_model = _DataNodeModel(
        "my_dn_id",
        "test_data_node",
        Scope.PIPELINE,
        "csv",
        "name",
        "parent_id",
        datetime.datetime(1985, 10, 14, 2, 30, 0).isoformat(),
        [JobId("job_id")],
        None,
        None,
        False,
        {"path": "/path", "has_header": True, "prop": "ENV[FOO]"},
    )

    def test_save_and_load(self, tmpdir):
        repository = _DataRepositoryFactory._build_repository()
        repository.base_path = tmpdir
        repository._save(self.data_node)
        dn = repository.load("my_dn_id")

        assert isinstance(dn, CSVDataNode)
        assert isinstance(dn, DataNode)

    def test_from_and_to_model(self):
        repository = _DataRepositoryFactory._build_repository()
        assert repository._to_model(self.data_node) == self.data_node_model
        assert repository._from_model(self.data_node_model) == self.data_node

    def test_data_node_with_env_variable_value_not_serialized(self):
        with mock.patch.dict(os.environ, {"FOO": "bar"}):
            repository = _DataRepositoryFactory._build_repository()
            assert repository._to_model(self.data_node).data_node_properties["prop"] == "ENV[FOO]"
            assert self.data_node._properties.data["prop"] == "ENV[FOO]"
            assert self.data_node.properties["prop"] == "bar"
            assert self.data_node.prop == "bar"
