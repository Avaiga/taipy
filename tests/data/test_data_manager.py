import os
import pathlib

import pytest

from taipy.config import Config, DataSourceConfig
from taipy.data import CSVDataSource, Scope
from taipy.data.data_source_model import DataSourceModel
from taipy.data.manager import DataManager
from taipy.exceptions import InvalidDataSourceType, ModelNotFound


class TestDataManager:
    def test_create_data_source(self, tmpdir):
        dm = DataManager()
        dm.repository.base_path = tmpdir
        # Test we can instantiate a CsvDataSourceEntity from DataSource with type csv
        csv_ds_config = DataSourceConfig(name="foo", type="csv", path="bar", has_header=True)
        csv_1 = dm._create_and_save_data_source(csv_ds_config, None)
        fetched_ds = dm.get(csv_1.id)

        assert dm.get(csv_1.id).id == csv_1.id
        assert dm.get(csv_1.id).config_name == csv_1.config_name
        assert dm.get(csv_1.id).scope == csv_1.scope
        assert dm.get(csv_1.id).parent_id is None
        assert dm.get(csv_1.id).properties == csv_1.properties

        # Test we can instantiate a EmbeddedDataSource from DataSourceConfig

        # with type embedded
        in_memory_ds_config = DataSourceConfig(name="foo", type="in_memory", scope=Scope.SCENARIO, data="bar")
        in_mem_ds = dm._create_and_save_data_source(in_memory_ds_config, "Scenario_id")
        fetched_entity = dm.get(in_mem_ds.id)

        assert fetched_entity.id == in_mem_ds.id
        assert fetched_entity.config_name == in_mem_ds.config_name
        assert fetched_entity.scope == in_mem_ds.scope
        assert fetched_entity.parent_id == "Scenario_id"
        assert fetched_entity.properties == in_mem_ds.properties

        # Test an exception is raised if the type provided to the data source is wrong
        wrong_type_ds_config = DataSourceConfig(name="foo", type="bar")
        with pytest.raises(InvalidDataSourceType):
            dm._create_and_save_data_source(wrong_type_ds_config, None)

        # Test that each time we ask for a data source entity creation from the same
        # data source, a new id is created
        csv_2 = dm._create_and_save_data_source(csv_ds_config, None)
        assert csv_2.id != csv_1.id

    def test_create_data_source_with_config_file(self):
        Config.load(os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/config.toml"))

        dm = DataManager()
        csv_ds = Config.data_source_configs.create(name="foo", type="csv", path="bar", has_header=True)
        csv = dm._create_and_save_data_source(csv_ds, None)
        assert csv.config_name == "foo"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "path_from_config_file"
        assert csv.has_header is False

        csv_ds = Config.data_source_configs.create(name="bar", type="csv", path="bar", has_header=True)
        csv = dm._create_and_save_data_source(csv_ds, None)
        assert csv.config_name == "bar"
        assert isinstance(csv, CSVDataSource)
        assert csv.path == "bar"
        assert csv.has_header is False

    def test_create_and_fetch(self, tmpdir):
        dm = DataManager()
        dm.repository.base_path = tmpdir
        dm.repository.save(
            DataSourceModel(
                "ds_id",
                "test_data_source",
                Scope.PIPELINE,
                "in_memory",
                None,
                {"data": "In Memory Data Source"},
            )
        )
        ds = dm.repository.get("ds_id")

        assert isinstance(ds, DataSourceModel)

    def test_fetch_data_source_not_exists(self):
        dm = DataManager()
        with pytest.raises(ModelNotFound):
            dm.repository.get("test_data_source_2")


    def test_get_or_create(self):
        dm = DataManager()
        dm.delete_all()

        global_ds_config = Config.data_source_configs.create(name="test_data_source", type="in_memory",
                                                             scope=Scope.GLOBAL,
                                                             data="In memory Data Source")
        scenario_ds_config = Config.data_source_configs.create(name="test_data_source2", type="in_memory",
                                                               scope=Scope.SCENARIO,
                                                               data="In memory scenario")
        pipeline_ds_config = Config.data_source_configs.create(name="test_data_source2", type="in_memory",
                                                               scope=Scope.PIPELINE,
                                                               data="In memory pipeline")

        assert len(dm.get_all()) == 0
        global_ds = dm.get_or_create(global_ds_config, None, None)
        assert len(dm.get_all()) == 1
        global_ds_bis = dm.get_or_create(global_ds_config, None)
        assert len(dm.get_all()) == 1
        assert global_ds.id == global_ds_bis.id

        scenario_ds = dm.get_or_create(scenario_ds_config, "scenario_id")
        assert len(dm.get_all()) == 2
        scenario_ds_bis = dm.get_or_create(scenario_ds_config, "scenario_id")
        assert len(dm.get_all()) == 2
        assert scenario_ds.id == scenario_ds_bis.id
        scenario_ds_ter = dm.get_or_create(scenario_ds_config, "scenario_id_2")
        assert len(dm.get_all()) == 3
        assert scenario_ds.id != scenario_ds_ter.id

        pipeline_ds = dm.get_or_create(pipeline_ds_config, "scenario_id", "pipeline_1")
        assert len(dm.get_all()) == 4
        pipeline_ds_bis = dm.get_or_create(pipeline_ds_config, "scenario_id", "pipeline_1")
        assert len(dm.get_all()) == 4
        assert pipeline_ds.id == pipeline_ds_bis.id
        pipeline_ds_ter = dm.get_or_create(pipeline_ds_config, "scenario_id", "pipeline_2")
        assert len(dm.get_all()) == 5
        assert pipeline_ds.id != pipeline_ds_ter.id

        pipeline_ds_config.name = "test_data_source4"
        pipeline_ds_quater = dm.get_or_create(pipeline_ds_config, None)
        assert len(dm.get_all()) == 6
        assert pipeline_ds.id == pipeline_ds_bis.id
        assert pipeline_ds_bis.id != pipeline_ds_ter.id
        assert pipeline_ds_bis.id != pipeline_ds_quater.id
        assert pipeline_ds_ter.id != pipeline_ds_quater.id
