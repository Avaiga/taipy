import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.data import CSVDataSource, PickleDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class TestCSVDataSourceEntity:
    def test_get(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        csv = CSVDataSource.create("foo", Scope.PIPELINE, path)
        assert csv.path == path
        data = csv.get()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, csv_file, default_data_frame, content, columns):
        csv = CSVDataSource.create("foo", Scope.PIPELINE, csv_file)
        assert np.array_equal(csv.get().values, default_data_frame.values)

        if not columns:
            csv.write(content)
            df = pd.DataFrame(content)
        else:
            csv.write(content, columns)
            df = pd.DataFrame(content, columns=columns)

        assert np.array_equal(csv.get().values, df.values)

    def test_create(self):
        ds = CSVDataSource.create("fOo BAr", Scope.PIPELINE, "data/source/path")

        assert isinstance(ds, CSVDataSource)
        assert ds.config_name == "foo_bar"
        assert ds.has_header is False
        assert ds.path == "data/source/path"
        assert ds.type() == "csv"
        assert ds.id is not None
        with pytest.raises(AttributeError):
            ds.foo

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, "ds_id", {})

    def test_preview(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ds = CSVDataSource.create("foo", Scope.PIPELINE, path)
        ds.preview()


class TestPickleDataSourceEntity:

    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob, os
        for f in glob.glob("*.p"):
            print (f"deleting file {f}")
            os.remove(f)

    def test_get(self):
        embedded_str = PickleDataSource.create("foo", Scope.PIPELINE, "bar")
        assert isinstance(embedded_str.get(), str)
        assert embedded_str.get() == "bar"
        assert embedded_str.data == "bar"
        embedded_int = PickleDataSource.create("foo", Scope.PIPELINE, 197)
        assert isinstance(embedded_int.get(), int)
        assert embedded_int.get() == 197
        embedded_dict = PickleDataSource.create("foo", Scope.PIPELINE, {"bar": 12, "baz": "qux", "quux": [13]})
        assert isinstance(embedded_dict.get(), dict)
        assert embedded_dict.get() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = PickleDataSource.create("foobar BaZ", Scope.PIPELINE, data="Embedded Data Source")
        assert ds.config_name == "foobar_baz"
        assert isinstance(ds, PickleDataSource)
        assert ds.type() == "embedded"
        assert ds.id is not None
        assert ds.get() == "Embedded Data Source"

    def test_preview(self):
        ds = PickleDataSource.create("foo", Scope.PIPELINE, data="Embedded Data Source")
        ds.preview()
        import os
        os.remove(f"{ds.id}.p")

    def test_write(self):
        embedded_str = PickleDataSource.create("foo", Scope.PIPELINE, "bar")
        assert isinstance(embedded_str.get(), str)
        assert embedded_str.get() == "bar"
        embedded_str.properties["data"] = "baz"  # this modifies the default data value but not the data value itself
        assert embedded_str.get() == "bar"
        embedded_str.write("qux")
        assert embedded_str.get() == "qux"
        embedded_str.write(1998)
        assert embedded_str.get() == 1998

    def test_create_with_file_name(self):
        ds = PickleDataSource.create("foo", Scope.PIPELINE, data="bar", file_path="foo.EXISTING_FILE.p")
        import os
        assert os.path.isfile("foo.EXISTING_FILE.p")
        assert ds.get() == "bar"
        ds.write("qux")
        assert ds.get() == "qux"
        ds.write(1998)
        assert ds.get() == 1998
