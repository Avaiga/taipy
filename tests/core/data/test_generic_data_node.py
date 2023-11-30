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

import pytest

from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.data_node_id import DataNodeId
from src.taipy.core.data.generic import GenericDataNode
from src.taipy.core.exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction
from taipy.config.common.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


def read_fct():
    return TestGenericDataNode.data


def read_fct_with_args(inp):
    return [i + inp for i in TestGenericDataNode.data]


def write_fct(data):
    data.append(data[-1] + 1)


def write_fct_with_args(data, inp):
    for _ in range(inp):
        data.append(data[-1] + 1)


def read_fct_modify_data_node_name(data_node_id: DataNodeId, name: str):
    import src.taipy.core as tp

    data_node = tp.get(data_node_id)
    assert isinstance(data_node, DataNode)
    data_node.name = name  # type:ignore
    return data_node


def reset_data():
    TestGenericDataNode.data = [i for i in range(10)]


class TestGenericDataNode:
    data = [i for i in range(10)]

    def test_create(self):
        dn = GenericDataNode(
            "foo_bar", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": write_fct, "name": "super name"}
        )
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] == read_fct
        assert dn.properties["write_fct"] == write_fct

        dn_1 = GenericDataNode(
            "foo", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": None, "name": "foo"}
        )
        assert isinstance(dn, GenericDataNode)
        assert dn_1.storage_type() == "generic"
        assert dn_1.config_id == "foo"
        assert dn_1.name == "foo"
        assert dn_1.scope == Scope.SCENARIO
        assert dn_1.id is not None
        assert dn_1.owner_id is None
        assert dn_1.last_edit_date is not None
        assert dn_1.job_ids == []
        assert dn_1.is_ready_for_reading
        assert dn_1.properties["read_fct"] == read_fct
        assert dn_1.properties["write_fct"] is None

        dn_2 = GenericDataNode(
            "xyz", Scope.SCENARIO, properties={"read_fct": None, "write_fct": write_fct, "name": "xyz"}
        )
        assert isinstance(dn, GenericDataNode)
        assert dn_2.storage_type() == "generic"
        assert dn_2.config_id == "xyz"
        assert dn_2.name == "xyz"
        assert dn_2.scope == Scope.SCENARIO
        assert dn_2.id is not None
        assert dn_2.owner_id is None
        assert dn_2.last_edit_date is not None
        assert dn_2.job_ids == []
        assert dn_2.is_ready_for_reading
        assert dn_2.properties["read_fct"] is None
        assert dn_2.properties["write_fct"] == write_fct

        dn_3 = GenericDataNode("xyz", Scope.SCENARIO, properties={"read_fct": read_fct, "name": "xyz"})
        assert isinstance(dn, GenericDataNode)
        assert dn_3.storage_type() == "generic"
        assert dn_3.config_id == "xyz"
        assert dn_3.name == "xyz"
        assert dn_3.scope == Scope.SCENARIO
        assert dn_3.id is not None
        assert dn_3.owner_id is None
        assert dn_3.last_edit_date is not None
        assert dn_3.job_ids == []
        assert dn_3.is_ready_for_reading
        assert dn_3.properties["read_fct"] == read_fct
        assert dn_3.properties["write_fct"] is None

        dn_4 = GenericDataNode("xyz", Scope.SCENARIO, properties={"write_fct": write_fct, "name": "xyz"})
        assert isinstance(dn, GenericDataNode)
        assert dn_4.storage_type() == "generic"
        assert dn_4.config_id == "xyz"
        assert dn_4.name == "xyz"
        assert dn_4.scope == Scope.SCENARIO
        assert dn_4.id is not None
        assert dn_4.owner_id is None
        assert dn_4.last_edit_date is not None
        assert dn_4.job_ids == []
        assert dn_4.is_ready_for_reading
        assert dn_4.properties["read_fct"] is None
        assert dn_4.properties["write_fct"] == write_fct

        with pytest.raises(InvalidConfigurationId):
            GenericDataNode("foo bar", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": write_fct})

    def test_get_user_properties(self):
        dn_1 = GenericDataNode(
            "dn_1",
            Scope.SCENARIO,
            properties={
                "read_fct": read_fct,
                "write_fct": write_fct,
                "read_fct_args": 1,
                "write_fct_args": 2,
                "foo": "bar",
            },
        )

        # read_fct, read_fct_args, write_fct, write_fct_args are filtered out
        assert dn_1._get_user_properties() == {"foo": "bar"}

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.SCENARIO, DataNodeId("dn_id"), properties={})

    def test_read_write_generic_datanode(self):
        generic_dn = GenericDataNode("foo", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": write_fct})

        assert generic_dn.read() == self.data
        assert len(generic_dn.read()) == 10

        generic_dn.write(self.data)
        assert generic_dn.read() == self.data
        assert len(generic_dn.read()) == 11

        generic_dn_1 = GenericDataNode("bar", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": None})

        assert generic_dn_1.read() == self.data
        assert len(generic_dn_1.read()) == 11

        with pytest.raises(MissingWriteFunction):
            generic_dn_1.write(self.data)

        generic_dn_2 = GenericDataNode("xyz", Scope.SCENARIO, properties={"read_fct": None, "write_fct": write_fct})

        generic_dn_2.write(self.data)
        assert len(self.data) == 12

        with pytest.raises(MissingReadFunction):
            generic_dn_2.read()

        generic_dn_3 = GenericDataNode("bar", Scope.SCENARIO, properties={"read_fct": None, "write_fct": None})

        with pytest.raises(MissingReadFunction):
            generic_dn_3.read()
        with pytest.raises(MissingWriteFunction):
            generic_dn_3.write(self.data)

        reset_data()

    def test_read_write_generic_datanode_with_arguments(self):
        generic_dn = GenericDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "read_fct": read_fct_with_args,
                "write_fct": write_fct_with_args,
                "read_fct_args": [1],
                "write_fct_args": [2],
            },
        )

        assert all([a + 1 == b for a, b in zip(self.data, generic_dn.read())])
        assert len(generic_dn.read()) == 10

        generic_dn.write(self.data)
        assert len(generic_dn.read()) == 12

        reset_data()

    def test_read_write_generic_datanode_with_non_list_arguments(self):
        generic_dn = GenericDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "read_fct": read_fct_with_args,
                "write_fct": write_fct_with_args,
                "read_fct_args": 1,
                "write_fct_args": 2,
            },
        )

        assert all([a + 1 == b for a, b in zip(self.data, generic_dn.read())])
        assert len(generic_dn.read()) == 10

        generic_dn.write(self.data)
        assert len(generic_dn.read()) == 12

        reset_data()

    def test_save_data_node_when_read(self):
        generic_dn = GenericDataNode(
            "foo", Scope.SCENARIO, properties={"read_fct": read_fct_modify_data_node_name, "write_fct": write_fct}
        )
        generic_dn._properties["read_fct_args"] = (generic_dn.id, "bar")
        generic_dn.read()
        assert generic_dn.name == "bar"
