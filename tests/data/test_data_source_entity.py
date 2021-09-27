import dataclasses
import os
import pathlib

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

from taipy.data.entity import CSVDataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class TestCSVDataSourceEntity:
    def test_get(self):
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv"
        )
        csv = CSVDataSourceEntity.create("foo", Scope.PIPELINE, path)
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
        csv = CSVDataSourceEntity.create("foo", Scope.PIPELINE, csv_file)
        assert np.array_equal(csv.get().values, default_data_frame.values)

        if not columns:
            csv.write(content)
            df = pd.DataFrame(content)
        else:
            csv.write(content, columns)
            df = pd.DataFrame(content, columns=columns)

        assert np.array_equal(csv.get().values, df.values)

    def test_create(self):
        ds = CSVDataSourceEntity.create("foo", Scope.PIPELINE, "data/source/path")

        assert isinstance(ds, CSVDataSourceEntity)
        assert ds.has_header is False
        assert ds.path == "data/source/path"
        assert ds.type() == "csv"

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSourceEntity("foo", Scope.PIPELINE, "ds_id", {})

    def test_preview(self):
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv"
        )
        ds = CSVDataSourceEntity.create("foo", Scope.PIPELINE, path)
        ds.preview()


class TestEmbeddedDataSourceEntity:
    def test_get(self):
        embedded_str = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, "bar")
        assert isinstance(embedded_str.get(), str)
        assert embedded_str.get() == "bar"
        embedded_int = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, 197)
        assert isinstance(embedded_int.get(), int)
        assert embedded_int.get() == 197
        embedded_dict = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, {"bar": 12, "baz": "qux", "quux": [13]}
        )
        assert isinstance(embedded_dict.get(), dict)
        assert embedded_dict.get() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_create(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, data="Embedded Data Source"
        )
        assert isinstance(ds, EmbeddedDataSourceEntity)
        assert ds.type() == "embedded"

    def test_preview(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, data="Embedded Data Source"
        )
        ds.preview()

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSourceEntity("foo", Scope.PIPELINE, "ds_id", {})
