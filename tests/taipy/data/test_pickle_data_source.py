import pytest

from taipy.data import PickleDataSource
from taipy.data.scope import Scope
from taipy.exceptions.data_source import NoData


class TestPickleDataSourceEntity:
    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob
        import os

        for f in glob.glob("*.p"):
            print(f"deleting file {f}")
            os.remove(f)

    def test_create(self):
        ds = PickleDataSource("foobar BaZξyₓéà", Scope.PIPELINE, properties={"default_data": "Data"})
        assert isinstance(ds, PickleDataSource)
        assert ds.type() == "pickle"
        assert ds.config_name == "foobar_bazxyxea"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.last_edition_date is not None
        assert ds.job_ids == []
        assert ds.up_to_date
        assert ds.read() == "Data"
        assert ds.default_data == "Data"
        assert ds.last_edition_date is not None
        assert ds.job_ids == []

    def test_create_with_file_name(self):
        ds = PickleDataSource("foo", Scope.PIPELINE, properties={"default_data": "bar", "file_path": "foo.FILE.p"})
        import os

        assert os.path.isfile("foo.FILE.p")
        assert ds.read() == "bar"
        ds.write("qux")
        assert ds.read() == "qux"
        ds.write(1998)
        assert ds.read() == 1998

    def test_read_and_write(self):
        no_data_ds = PickleDataSource("foo", Scope.PIPELINE)
        with pytest.raises(NoData):
            no_data_ds.read()
        pickle_str = PickleDataSource("foo", Scope.PIPELINE, properties={"default_data": "bar"})
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        assert pickle_str.default_data == "bar"
        pickle_str.properties["default_data"] = "baz"  # this modifies the default data value but not the data itself
        assert pickle_str.read() == "bar"
        pickle_str.write("qux")
        assert pickle_str.read() == "qux"
        pickle_str.write(1998)
        assert pickle_str.read() == 1998
        assert isinstance(pickle_str.read(), int)
        pickle_int = PickleDataSource("foo", Scope.PIPELINE, properties={"default_data": 197})
        assert isinstance(pickle_int.read(), int)
        assert pickle_int.read() == 197
        pickle_dict = PickleDataSource(
            "foo", Scope.PIPELINE, properties={"default_data": {"bar": 12, "baz": "qux", "quux": [13]}}
        )
        assert isinstance(pickle_dict.read(), dict)
        assert pickle_dict.read() == {"bar": 12, "baz": "qux", "quux": [13]}
