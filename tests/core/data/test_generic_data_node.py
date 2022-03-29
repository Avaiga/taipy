import pytest

from taipy.core.common.alias import DataNodeId
from taipy.core.common.scope import Scope
from taipy.core.data.data_node import DataNode
from taipy.core.data.generic import GenericDataNode
from taipy.core.exceptions.exceptions import (
    InvalidConfigurationId,
    MissingReadFunction,
    MissingRequiredProperty,
    MissingWriteFunction,
)


def read_fct():
    return TestGenericDataNode.data


def read_fct_with_params(inp):
    return [i + inp for i in TestGenericDataNode.data]


def write_fct(data):
    data.append(data[-1] + 1)


def write_fct_with_params(data, inp):
    for i in range(inp):
        data.append(data[-1] + 1)


def read_fct_modify_data_node_name(data_node_id: DataNodeId, name: str):
    import taipy.core as tp

    data_node = tp.get(data_node_id)
    assert isinstance(data_node, DataNode)
    data_node.name = name  # type:ignore
    return data_node


class TestGenericDataNode:
    data = [i for i in range(10)]

    def test_create(self):

        dn = GenericDataNode(
            "foo_bar", Scope.PIPELINE, name="super name", properties={"read_fct": read_fct, "write_fct": write_fct}
        )
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_id == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.last_edition_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] == read_fct
        assert dn.properties["write_fct"] == write_fct

        dn_1 = GenericDataNode("foo", Scope.PIPELINE, name="foo", properties={"read_fct": read_fct, "write_fct": None})
        assert isinstance(dn, GenericDataNode)
        assert dn_1.storage_type() == "generic"
        assert dn_1.config_id == "foo"
        assert dn_1.name == "foo"
        assert dn_1.scope == Scope.PIPELINE
        assert dn_1.id is not None
        assert dn_1.parent_id is None
        assert dn_1.last_edition_date is not None
        assert dn_1.job_ids == []
        assert dn_1.is_ready_for_reading
        assert dn_1.properties["read_fct"] == read_fct
        assert dn_1.properties["write_fct"] is None

        dn_2 = GenericDataNode("xyz", Scope.PIPELINE, name="xyz", properties={"read_fct": None, "write_fct": write_fct})
        assert isinstance(dn, GenericDataNode)
        assert dn_2.storage_type() == "generic"
        assert dn_2.config_id == "xyz"
        assert dn_2.name == "xyz"
        assert dn_2.scope == Scope.PIPELINE
        assert dn_2.id is not None
        assert dn_2.parent_id is None
        assert dn_2.last_edition_date is not None
        assert dn_2.job_ids == []
        assert dn_2.is_ready_for_reading
        assert dn_2.properties["read_fct"] is None
        assert dn_2.properties["write_fct"] == write_fct

        with pytest.raises(InvalidConfigurationId):
            GenericDataNode("foo bar", Scope.PIPELINE, properties={"read_fct": read_fct, "write_fct": write_fct})

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"))
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"read_fct": None})
        with pytest.raises(MissingRequiredProperty):
            GenericDataNode("foo", Scope.PIPELINE, DataNodeId("dn_id"), properties={"write_fct": None})

    def test_read_write_generic_datanode(self):

        generic_dn = GenericDataNode("foo", Scope.PIPELINE, properties={"read_fct": read_fct, "write_fct": write_fct})

        assert generic_dn.read() == self.data
        assert len(generic_dn.read()) == 10

        generic_dn.write(self.data)
        assert generic_dn.read() == self.data
        assert len(generic_dn.read()) == 11

        generic_dn_1 = GenericDataNode("bar", Scope.PIPELINE, properties={"read_fct": read_fct, "write_fct": None})

        assert generic_dn_1.read() == self.data
        assert len(generic_dn_1.read()) == 11

        with pytest.raises(MissingWriteFunction):
            generic_dn_1.write(self.data)

        generic_dn_2 = GenericDataNode("xyz", Scope.PIPELINE, properties={"read_fct": None, "write_fct": write_fct})

        generic_dn_2.write(self.data)
        assert len(self.data) == 12

        with pytest.raises(MissingReadFunction):
            generic_dn_2.read()

        generic_dn_3 = GenericDataNode("bar", Scope.PIPELINE, properties={"read_fct": None, "write_fct": None})

        with pytest.raises(MissingReadFunction):
            generic_dn_3.read()
        with pytest.raises(MissingWriteFunction):
            generic_dn_3.write(self.data)

    def test_read_write_generic_datanode_with_parameters(self):
        generic_dn = GenericDataNode(
            "foo",
            Scope.PIPELINE,
            properties={
                "read_fct": read_fct_with_params,
                "write_fct": write_fct_with_params,
                "read_fct_params": tuple([1]),
                "write_fct_params": tuple([2]),
            },
        )

        assert all([a + 1 == b for a, b in zip(self.data, generic_dn.read())])
        assert len(generic_dn.read()) == 12

        generic_dn.write(self.data)
        assert len(generic_dn.read()) == 14

    def test_save_data_node_when_read(self):
        generic_dn = GenericDataNode(
            "foo", Scope.PIPELINE, properties={"read_fct": read_fct_modify_data_node_name, "write_fct": write_fct}
        )
        generic_dn._properties["read_fct_params"] = (generic_dn.id, "bar")
        generic_dn.read()
        assert generic_dn.name == "bar"
