import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.data import CSVDataSource, EmbeddedDataSource
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
        assert ds.name == "foo_bar"
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


class TestEmbeddedDataSourceEntity:
    def test_get(self):
        embedded_str = EmbeddedDataSource.create("foo", Scope.PIPELINE, "bar")
        assert isinstance(embedded_str.get(), str)
        assert embedded_str.get() == "bar"
        assert embedded_str.data == "bar"
        embedded_int = EmbeddedDataSource.create("foo", Scope.PIPELINE, 197)
        assert isinstance(embedded_int.get(), int)
        assert embedded_int.get() == 197
        embedded_dict = EmbeddedDataSource.create("foo", Scope.PIPELINE, {"bar": 12, "baz": "qux", "quux": [13]})
        assert isinstance(embedded_dict.get(), dict)
        assert embedded_dict.get() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = EmbeddedDataSource.create("foobar BaZ", Scope.PIPELINE, data="Embedded Data Source")
        assert ds.name == "foobar_baz"
        assert isinstance(ds, EmbeddedDataSource)
        assert ds.type() == "embedded"
        assert ds.id is not None

    def test_preview(self):
        ds = EmbeddedDataSource.create("foo", Scope.PIPELINE, data="Embedded Data Source")
        ds.preview()

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, "ds_id", {})
