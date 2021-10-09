import os
import pathlib

import pytest

from taipy.configuration import ConfigurationManager
from taipy.data import CSVDataSource, DataSourceConfig, Scope
from taipy.data.data_source_model import DataSourceModel
from taipy.data.manager import DataManager
from taipy.exceptions import InvalidDataSourceType


class TestDataManager:
    def test_create_data_source_entity(self):
        dm = DataManager()
        # Test we can instantiate a CsvDataSourceEntity from DataSource with type csv
        csv_ds = DataSourceConfig(name="foo", type="csv", path="bar", has_header=True)
        csv_entity_1 = dm.create_data_source(csv_ds)
        assert dm.get_data_source(csv_entity_1.id).id == csv_entity_1.id
        assert dm.get_data_source(csv_entity_1.id).name == csv_entity_1.name
        assert dm.get_data_source(csv_entity_1.id).scope == csv_entity_1.scope
        assert dm.get_data_source(csv_entity_1.id).properties == csv_entity_1.properties

        # Test we can instantiate a EmbeddedDataSourceEntity from DataSource
        # with type embedded
        embedded_ds = DataSourceConfig(name="foo", type="embedded", data="bar")
        embedded_entity = dm.create_data_source(embedded_ds)
        fetched_entity = dm.get_data_source(embedded_entity.id)

        assert fetched_entity.id == embedded_entity.id
        assert fetched_entity.name == embedded_entity.name
        assert fetched_entity.scope == embedded_entity.scope
        assert fetched_entity.properties == embedded_entity.properties

        # Test an exception is raised if the type provided to the data source is wrong
        wrong_type_ds = DataSourceConfig(name="foo", type="bar")
        with pytest.raises(InvalidDataSourceType):
            dm.create_data_source(wrong_type_ds)

        # Test that each time we ask for a data source entity creation from the same
        # data source, a new id is created
        csv_entity_2 = dm.create_data_source(csv_ds)
        assert csv_entity_2.id != csv_entity_1.id

    def test_create_data_source_with_config_file(self):
        ConfigurationManager.load(os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/config.toml"))

        dm = DataManager()
        csv_ds = DataSourceConfig(name="foo", type="csv", path="bar", has_header=True)
        csv = dm.create_data_source(csv_ds)
        assert csv.name == "foo"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "path_from_config_file"
        assert csv.has_header is False

        csv_ds = DataSourceConfig(name="bar", type="csv", path="bar", has_header=True)
        csv = dm.create_data_source(csv_ds)
        assert csv.name == "bar"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "bar"
        assert csv.has_header is False

    def test_create_and_fetch(self):
        dm = DataManager()
        dm.create_data_source_model(
            "ds_id",
            "test_data_source",
            Scope.PIPELINE,
            "embedded",
            {"data": "Embedded Data Source"},
        )

        ds = dm.fetch_data_source_model("ds_id")

        assert isinstance(ds, DataSourceModel)

    def test_fetch_data_source_not_exists(self):
        dm = DataManager()
        with pytest.raises(KeyError):
            dm.fetch_data_source_model("test_data_source_2")
