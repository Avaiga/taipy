import os
import pathlib

import pytest

from taipy.data.entity import CSVDataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class TestCSVDataSourceEntity:
    def test_create(self):
        ds = CSVDataSourceEntity.create("foo", Scope.PIPELINE, "data/entity/path")

        assert isinstance(ds, CSVDataSourceEntity)
        assert ds.has_header is False
        assert ds.path == "data/entity/path"
        assert ds.type == "csv"

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
    def test_create(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, "ds_id", {"data": "Embedded Data Source"}
        )
        assert isinstance(ds, EmbeddedDataSourceEntity)
        assert ds.type == "embedded"

    def test_preview(self):
        ds = EmbeddedDataSourceEntity.create(
            "foo", Scope.PIPELINE, "ds_id", {"data": "Embedded Data Source"}
        )
        ds.preview()

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSourceEntity("foo", Scope.PIPELINE, "ds_id", {})
