from time import sleep

import pytest

from taipy.common.alias import DataNodeId
from taipy.data.in_memory import InMemoryDataNode
from taipy.data.manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.data_node import NoData


class TestInMemoryDataNodeEntity:
    def test_create(self):
        ds = InMemoryDataNode(
            "foobar BaZy",
            Scope.SCENARIO,
            DataNodeId("id_uio"),
            "my name",
            "parent_id",
            properties={"default_data": "In memory Data Node"},
        )
        assert isinstance(ds, InMemoryDataNode)
        assert ds.storage_type() == "in_memory"
        assert ds.config_name == "foobar_bazy"
        assert ds.scope == Scope.SCENARIO
        assert ds.id == "id_uio"
        assert ds.name == "my name"
        assert ds.parent_id == "parent_id"
        assert ds.last_edition_date is not None
        assert ds.job_ids == []
        assert ds.is_ready_for_reading
        assert ds.read() == "In memory Data Node"
        assert ds.default_data == "In memory Data Node"

        ds_2 = InMemoryDataNode("foo", Scope.PIPELINE)
        assert ds_2.last_edition_date is None
        assert not ds_2.is_ready_for_reading

    def test_read_and_write(self):
        no_data_ds = InMemoryDataNode("foo", Scope.PIPELINE, DataNodeId("ds_id"))
        with pytest.raises(NoData):
            no_data_ds.read()
        in_mem_ds = InMemoryDataNode("foo", Scope.PIPELINE, properties={"default_data": "bar"})
        assert isinstance(in_mem_ds.read(), str)
        assert in_mem_ds.read() == "bar"
        in_mem_ds.properties["default_data"] = "baz"  # this modifies the default data value but not the data itself
        assert in_mem_ds.read() == "bar"
        in_mem_ds.write("qux")
        assert in_mem_ds.read() == "qux"
        in_mem_ds.write(1998)
        assert isinstance(in_mem_ds.read(), int)
        assert in_mem_ds.read() == 1998
