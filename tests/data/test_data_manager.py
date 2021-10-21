import os
import pathlib

import pytest

from taipy.config import Config, DataSourceConfig
from taipy.data import CSVDataSource, Scope
from taipy.data.data_source_model import DataSourceModel
from taipy.data.manager import DataManager
from taipy.exceptions import InvalidDataSourceType


class TestDataManager:
    def test_create_data_source(self):
        dm = DataManager()
        # Test we can instantiate a CsvDataSourceEntity from DataSource with type csv
        csv_ds_config = DataSourceConfig(name="foo", type="csv", path="bar", has_header=True)
        csv_1 = dm.create_data_source(csv_ds_config)
        assert dm.get_data_source(csv_1.id).id == csv_1.id
        assert dm.get_data_source(csv_1.id).config_name == csv_1.config_name
        assert dm.get_data_source(csv_1.id).scope == csv_1.scope
        assert dm.get_data_source(csv_1.id).properties == csv_1.properties

        # Test we can instantiate a EmbeddedDataSourceEntity from DataSource
        # with type embedded
        in_memory_ds_config = DataSourceConfig(name="foo", type="in_memory", data="bar")
        in_mem_ds = dm.create_data_source(in_memory_ds_config)
        fetched_entity = dm.get_data_source(in_mem_ds.id)

        assert fetched_entity.id == in_mem_ds.id
        assert fetched_entity.config_name == in_mem_ds.config_name
        assert fetched_entity.scope == in_mem_ds.scope
        assert fetched_entity.properties == in_mem_ds.properties

        # Test an exception is raised if the type provided to the data source is wrong
        wrong_type_ds_config = DataSourceConfig(name="foo", type="bar")
        with pytest.raises(InvalidDataSourceType):
            dm.create_data_source(wrong_type_ds_config)

        # Test that each time we ask for a data source entity creation from the same
        # data source, a new id is created
        csv_2 = dm.create_data_source(csv_ds_config)
        assert csv_2.id != csv_1.id

    def test_create_data_source_with_config_file(self):
        Config.load(os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/config.toml"))

        dm = DataManager()
        csv_ds_config = Config.data_source_configs.create(name="foo", type="csv", path="bar", has_header=True)
        csv = dm.create_data_source(csv_ds_config)
        assert csv.config_name == "foo"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "path_from_config_file"
        assert csv.has_header is False

        csv_ds_config = Config.data_source_configs.create(name="bar", type="csv", path="bar", has_header=True)
        csv = dm.create_data_source(csv_ds_config)
        assert csv.config_name == "bar"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "bar"
        assert csv.has_header is False

    def test_create_and_fetch(self):
        dm = DataManager()
        dm.create_data_source_model(
            "ds_id",
            "test_data_source",
            Scope.PIPELINE,
            "in_memory",
            {"data": "In Memory Data Source"},
        )

        ds = dm.fetch_data_source_model("ds_id")

        assert isinstance(ds, DataSourceModel)

    def test_fetch_data_source_not_exists(self):
        dm = DataManager()
        with pytest.raises(KeyError):
            dm.fetch_data_source_model("test_data_source_2")

    def test_get_or_create(self):
        dm = DataManager()
        dm.delete_all()

        global_ds_config = DataSourceConfig(name="test_data_source", type="in_memory", scope=Scope.GLOBAL,
                                            data="In memory Data Source")
        pipeline_ds_config = DataSourceConfig(name="test_data_source2", type="in_memory", scope=Scope.PIPELINE,
                                              data="In memory Data Source")

        global_ds = dm.get_or_create(global_ds_config)
        pipeline_ds = dm.get_or_create(pipeline_ds_config)

        pipeline_ds_config.name = "test_data_source3"
        pipeline_ds2 = dm.get_or_create(pipeline_ds_config)

        assert pipeline_ds.id != pipeline_ds2.id

        global_ds2 = dm.get_or_create(global_ds_config)
        assert global_ds.config_name == global_ds2.config_name
