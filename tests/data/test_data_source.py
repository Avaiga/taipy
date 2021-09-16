import json
import os
import pathlib

import pytest

from taipy.data.data_source import (
    CSVDataSourceEntity,
    DataSource,
    EmbeddedDataSourceEntity,
)
from taipy.data.data_source.models import Scope
from taipy.exceptions import InvalidDataSourceType, MissingRequiredProperty


class TestDataSource:
    @pytest.mark.parametrize(
        "name,type,properties,expected_instance",
        [
            (
                "csv_ds",
                "csv",
                {"path": "data/source/path", "has_header": False},
                CSVDataSourceEntity,
            ),
            ("embedded_ds", "embedded", {"data": "42"}, EmbeddedDataSourceEntity),
        ],
    )
    def test_create_ds(self, name, type, properties, expected_instance):
        ds = DataSource(name=name, type=type, **properties)
        assert isinstance(ds, expected_instance)

    def test_invalid_ds_type(self):
        with pytest.raises(InvalidDataSourceType):
            DataSource(name="foo", type="invalid")

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            DataSource(name="csv_ds", type="csv")

    @pytest.mark.parametrize(
        "name,type,properties",
        [
            ("csv_ds", "csv", {"path": "data/source/path", "has_header": False}),
            ("embedded_ds", "embedded", {"data": "42"}),
        ],
    )
    def test_to_json(self, name, type, properties):
        ds = DataSource(name=name, type=type, **properties)
        ds_json = ds.to_json()

        expected_json = {"name": name, "type": type, "scope": "PIPELINE"}
        expected_json.update(**properties)

        assert json.dumps(expected_json) == ds_json

    def test_from_json(self):
        path = os.path.join(
            pathlib.Path(__file__).parent.resolve(),
            "data_sample/data_source_template.json",
        )
        ds = DataSource.from_json(json_path=path)
        assert isinstance(ds, CSVDataSourceEntity)
