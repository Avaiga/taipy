import dataclasses
import os
import pathlib

import pandas
import pytest

from taipy.data.data_source import CSVDataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.exceptions import MissingRequiredProperty


class TestCSVDataSourceEntity:
    def test_get(self):
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv"
        )
        csv = CSVDataSourceEntity.create("foo", Scope.PIPELINE, path)
        data = csv.get()
        assert isinstance(data, pandas.DataFrame)

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
        embedded_dict = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE,
                                                        {"bar": 12, "baz": "qux", "quux": [13]})
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
