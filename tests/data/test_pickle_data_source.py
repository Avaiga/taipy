import pytest

from taipy.data import PickleDataSource
from taipy.data.scope import Scope


class TestPickleDataSourceEntity:
    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob
        import os

        for f in glob.glob("*.p"):
            print(f"deleting file {f}")
            os.remove(f)

    def test_get(self):
        pickle_str = PickleDataSource.create("foo", Scope.PIPELINE, None, "bar")
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        assert pickle_str.default_data == "bar"
        pickle_int = PickleDataSource.create("foo", Scope.PIPELINE, None, 197)
        assert isinstance(pickle_int.read(), int)
        assert pickle_int.read() == 197
        pickle_dict = PickleDataSource.create("foo", Scope.PIPELINE, None, {"bar": 12, "baz": "qux", "quux": [13]})
        assert isinstance(pickle_dict.read(), dict)
        assert pickle_dict.read() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = PickleDataSource.create("foobar BaZ", Scope.PIPELINE, None, data="Pickle Data Source")
        assert ds.config_name == "foobar_baz"
        assert isinstance(ds, PickleDataSource)
        assert ds.type() == "pickle"
        assert ds.id is not None
        assert ds.read() == "Pickle Data Source"

    def test_preview(self):
        ds = PickleDataSource.create("foo", Scope.PIPELINE, None, data="Pickle Data Source")
        ds.preview()
        import os

        os.remove(f"{ds.id}.p")

    def test_write(self):
        pickle_str = PickleDataSource.create("foo", Scope.PIPELINE, None, data="bar")
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        pickle_str.properties["data"] = "baz"  # this modifies the default data value but not the data value itself
        assert pickle_str.read() == "bar"
        pickle_str.write("qux")
        assert pickle_str.read() == "qux"
        pickle_str.write(1998)
        assert pickle_str.read() == 1998

    def test_create_with_file_name(self):
        ds = PickleDataSource.create("foo", Scope.PIPELINE, None, data="bar", file_path="foo.EXISTING_FILE.p")
        import os

        assert os.path.isfile("foo.EXISTING_FILE.p")
        assert ds.read() == "bar"
        ds.write("qux")
        assert ds.read() == "qux"
        ds.write(1998)
        assert ds.read() == 1998
