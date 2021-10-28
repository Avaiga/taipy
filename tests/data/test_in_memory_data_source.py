import pytest

from taipy.data.in_memory import InMemoryDataSource
from taipy.data.scope import Scope


class TestInMemoryDataSourceEntity:
    @pytest.fixture(scope="function", autouse=True)
    def empty_data_sources(self):
        yield

    def test_get(self):
        embedded_str = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data="bar")
        assert isinstance(embedded_str.get(), str)
        assert embedded_str.get() == "bar"
        assert embedded_str.data == "bar"
        embedded_int = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data=197)
        assert isinstance(embedded_int.get(), int)
        assert embedded_int.get() == 197
        embedded_dict = InMemoryDataSource.create(
            "foo", Scope.PIPELINE, None, data={"bar": 12, "baz": "qux", "quux": [13]}
        )
        assert isinstance(embedded_dict.get(), dict)
        assert embedded_dict.get() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = InMemoryDataSource.create("foobar BaZ", Scope.PIPELINE, None, data="In memory Data Source")
        assert ds.config_name == "foobar_baz"
        assert isinstance(ds, InMemoryDataSource)
        assert ds.type() == "in_memory"
        assert ds.id is not None
        assert ds.get() == "In memory Data Source"

    def test_write(self):
        in_mem_ds = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data="bar")
        assert isinstance(in_mem_ds.get(), str)
        assert in_mem_ds.get() == "bar"
        in_mem_ds.properties["data"] = "baz"  # this modifies the default data value but not the data value itself
        assert in_mem_ds.get() == "bar"
        in_mem_ds.write("qux")
        assert in_mem_ds.get() == "qux"
        in_mem_ds.write(1998)
        assert in_mem_ds.get() == 1998
