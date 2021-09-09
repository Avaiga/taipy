import os
import pathlib

import pytest

from taipy.data.data_source import CSVDataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.exceptions import MissingRequiredProperty


class TestCSVDataSource:
    def test_create(self):
        ds = CSVDataSourceEntity.create("foo", Scope.PIPELINE, "data/source/path")

        assert isinstance(ds, CSVDataSourceEntity)
        assert ds.has_header is False
        assert ds.path == "data/source/path"

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSourceEntity("foo", Scope.PIPELINE, "ds_id", {})

    def test_preview(self):
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv"
        )
        ds = CSVDataSourceEntity.create("foo", Scope.PIPELINE, path)
        ds.preview()


class TestEmbeddedDataSource:
    def test_create(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, "ds_id", {"data": "Embedded Data Source"}
        )
        assert isinstance(ds, EmbeddedDataSourceEntity)

    def test_preview(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, "ds_id", {"data": "Embedded Data Source"}
        )
        ds.preview()

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSourceEntity("foo", Scope.PIPELINE, "ds_id", {})
