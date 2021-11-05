import pytest

from taipy.data.in_memory import InMemoryDataSource
from taipy.data.scope import Scope


class TestInMemoryDataSourceEntity:
    @pytest.fixture(scope="function", autouse=True)
    def empty_data_sources(self):
        yield

    def test_get(self):
        embedded_str = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data="bar")
        assert isinstance(embedded_str.read(), str)
        assert embedded_str.read() == "bar"
        assert embedded_str.default_data == "bar"
        embedded_int = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data=197)
        assert isinstance(embedded_int.read(), int)
        assert embedded_int.read() == 197
        embedded_dict = InMemoryDataSource.create(
            "foo", Scope.PIPELINE, None, data={"bar": 12, "baz": "qux", "quux": [13]}
        )
        assert isinstance(embedded_dict.read(), dict)
        assert embedded_dict.read() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = InMemoryDataSource.create("foobar BaZ", Scope.PIPELINE, None, data="In memory Data Source")
        assert ds.config_name == "foobar_baz"
        assert isinstance(ds, InMemoryDataSource)
        assert ds.type() == "in_memory"
        assert ds.id is not None
        assert ds.read() == "In memory Data Source"
        assert ds.last_edition_date is not None
        assert ds.job_ids == []

    def test_write(self):
        in_mem_ds = InMemoryDataSource.create("foo", Scope.PIPELINE, None, data="bar")
        assert isinstance(in_mem_ds.read(), str)
        assert in_mem_ds.read() == "bar"
        in_mem_ds.properties["data"] = "baz"  # this modifies the default data value but not the data value itself
        assert in_mem_ds.read() == "bar"
        in_mem_ds.write("qux")
        assert in_mem_ds.read() == "qux"
        in_mem_ds.write(1998)
        assert in_mem_ds.read() == 1998
