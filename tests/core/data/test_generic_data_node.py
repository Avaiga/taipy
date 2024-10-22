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

import pytest

from taipy.common.config import Config
from taipy.common.config.common.scope import Scope
from taipy.common.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node import DataNode
from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.generic import GenericDataNode
from taipy.core.exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction


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
    import taipy.core as tp

    data_node = tp.get(data_node_id)
    assert isinstance(data_node, DataNode)
    data_node.name = name  # type:ignore
    return data_node


def reset_data():
    TestGenericDataNode.data = list(range(10))


class TestGenericDataNode:
    data = list(range(10))

    def test_create_with_both_read_fct_and_write_fct(self):
        data_manager = _DataManagerFactory._build_manager()
        generic_dn_config = Config.configure_generic_data_node(
            id="foo_bar", read_fct=read_fct, write_fct=write_fct, name="super name"
        )
        dn = data_manager._create_and_set(generic_dn_config, None, None)
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

        with pytest.raises(InvalidConfigurationId):
            GenericDataNode("foo bar", Scope.SCENARIO, properties={"read_fct": read_fct, "write_fct": write_fct})

    def test_create_with_read_fct_and_none_write_fct(self):
        data_manager = _DataManagerFactory._build_manager()
        generic_dn_config = Config.configure_generic_data_node(id="foo", read_fct=read_fct, write_fct=None, name="foo")
        dn = data_manager._create_and_set(generic_dn_config, None, None)
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "foo"
        assert dn.name == "foo"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] == read_fct
        assert dn.properties["write_fct"] is None

    def test_create_with_write_fct_and_none_read_fct(self):
        data_manager = _DataManagerFactory._build_manager()
        generic_dn_config = Config.configure_generic_data_node(id="xyz", read_fct=None, write_fct=write_fct, name="xyz")
        dn = data_manager._create_and_set(generic_dn_config, None, None)
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "xyz"
        assert dn.name == "xyz"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] is None
        assert dn.properties["write_fct"] == write_fct

    def test_create_with_read_fct(self):
        data_manager = _DataManagerFactory._build_manager()
        generic_dn_config = Config.configure_generic_data_node(id="acb", read_fct=read_fct, name="acb")
        dn = data_manager._create_and_set(generic_dn_config, None, None)
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "acb"
        assert dn.name == "acb"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] == read_fct
        assert dn.properties["write_fct"] is None

    def test_create_with_write_fct(self):
        data_manager = _DataManagerFactory._build_manager()
        generic_dn_config = Config.configure_generic_data_node(id="mno", write_fct=write_fct, name="mno")
        dn = data_manager._create_and_set(generic_dn_config, None, None)
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "mno"
        assert dn.name == "mno"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] is None
        assert dn.properties["write_fct"] == write_fct

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

        assert all(a + 1 == b for a, b in zip(self.data, generic_dn.read()))
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

        assert all(a + 1 == b for a, b in zip(self.data, generic_dn.read()))
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
