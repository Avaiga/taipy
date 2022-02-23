import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.core.common.alias import DataNodeId
from taipy.core.config.config import Config
from taipy.core.data.data_manager import DataManager
from taipy.core.data.generic import GenericDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions import MissingRequiredProperty
from taipy.core.exceptions.data_node import NoData


def read_fct():
    return TestGenericDataNode.data

def read_fct_with_params(inp):
    return [i + inp for i in TestGenericDataNode.data] 

def write_fct(data):
    data.append(data[-1] + 1)

def write_fct_with_params(data, inp):
    for i in range(inp):
        data.append(data[-1] + 1)
    

class TestGenericDataNode:
    def test_exists_in_data_manager(self):
        assert GenericDataNode in DataManager._DATA_NODE_CLASSES

    data = [i for i in range(10)]

    def test_create(self):

        dn = GenericDataNode(
            "fOo BAr", Scope.PIPELINE, name="super name", properties={"read_fct": read_fct, "write_fct": write_fct}
        )
        assert isinstance(dn, GenericDataNode)
        assert dn.storage_type() == "generic"
        assert dn.config_name == "foo_bar"
        assert dn.name == "super name"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.parent_id is None
        assert dn.last_edition_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.properties["read_fct"] == read_fct
        assert dn.properties["write_fct"] == write_fct

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
        
    def test_read_write_generic_datanode_with_parameters(self):
        generic_dn = GenericDataNode("foo", Scope.PIPELINE, properties={"read_fct": read_fct_with_params, "write_fct": write_fct_with_params, "read_fct_params": {"inp": 1}, "write_fct_params": {"inp": 2}})

        assert all([a + 1 == b for a, b in zip(self.data, generic_dn.read())])
        assert len(generic_dn.read()) == 11

        generic_dn.write(self.data)
        assert len(generic_dn.read()) == 13
