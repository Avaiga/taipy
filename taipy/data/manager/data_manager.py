import logging
from typing import Dict, List

from taipy.config import Config, DataSourceConfig
from taipy.data import CSVDataSource, PickleDataSource
from taipy.data.data_source import DataSource
from taipy.data.data_source_model import DataSourceModel
from taipy.data.in_memory import InMemoryDataSource
from taipy.data.scope import Scope
from taipy.exceptions import InvalidDataSourceType
from taipy.exceptions.data_source import MultipleDataSourceFromSameConfigWithSameParent

"""
A Data Manager is entity responsible for keeping track and retrieving Taipy DataSources.
The Data Manager will facilitate data access between Taipy Modules.
"""


class DataManager:
    # This represents a database table that maintains our DataSource References.
    __DATA_SOURCE_MODEL_DB: Dict[str, DataSourceModel] = {}
    __DATA_SOURCE_CLASSES = {InMemoryDataSource, PickleDataSource, CSVDataSource}
    __DATA_SOURCE_CLASS_MAP = {v.type(): v for v in __DATA_SOURCE_CLASSES}

    def __create_data_source(self, data_source_config: DataSourceConfig) -> DataSource:
        try:
            return self.__DATA_SOURCE_CLASS_MAP[data_source_config.type](
                config_name=data_source_config.name,
                scope=data_source_config.scope,
                properties=data_source_config.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data source. " f"Type {data_source_config.type} does not exist.")
            raise InvalidDataSourceType(data_source_config.type)

    def __persist_data_source(self, data_source_config: DataSourceConfig, data_source: DataSource):
        self.save_data_source(data_source)

    def delete_all(self):
        self.__DATA_SOURCE_MODEL_DB: Dict[str, DataSourceModel] = {}

    def get_or_create(self, data_source_config: DataSourceConfig) -> DataSource:
        ds = Config.data_source_configs.get(data_source_config.name)
        if ds is not None and ds.scope > Scope.PIPELINE:
            return self.__create_data_source(data_source_config)

    def get_or_create(self,
                      data_source_config: DataSourceConfig,
                      scenario_id: Optional[str] = None,
                      pipeline_id: Optional[str] = None) -> DataSource:
        scope = data_source_config.scope
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        ds_from_data_source_config = self._find_by_config_name(data_source_config.name)
        ds_from_parent = [ds for ds in ds_from_data_source_config if ds.parent_id == parent_id]
        if len(ds_from_parent) == 1:
            return ds_from_parent[0]
        elif len(ds_from_parent) == 2:
            logging.error("Multiple data sources from same config exists with the same parent_id.")
            raise MultipleDataSourceFromSameConfigWithSameParent
        else:
            return self._create_and_save_data_source(data_source_config, parent_id)

    def save(self, data_source: DataSource):
        # TODO Check if we should create the model or if it already exist
        self._create_data_source_model(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.type(),
            data_source.parent_id,
            data_source.properties,
        )

    def get(self, data_source_id: str) -> DataSource:
        model = self._fetch_data_source_model(data_source_id)
        return self.__DATA_SOURCE_CLASS_MAP[model.type](
            config_name=model.config_name,
            scope=model.scope,
            id=model.id,
            parent_id=model.parent_id,
            properties=model.data_source_properties,
        )

    def get_all(self) -> List[DataSource]:
        return [self.get(model.id) for model in self.__DATA_SOURCE_MODEL_DB.values()]

    def _find_by_config_name(self, config_name: str) -> List[DataSource]:
        return [self.get(model.id) for model in self.__DATA_SOURCE_MODEL_DB.values()
                if model.config_name == config_name]

    def _fetch_data_source_model(self, id) -> DataSourceModel:
        return self.__DATA_SOURCE_MODEL_DB[id]

    def _create_data_source_model(self,
                                  id: str,
                                  name: str,
                                  scope: Scope,
                                  type: str,
                                  parent_id: Optional[str],
                                  properties: dict):
        self.__DATA_SOURCE_MODEL_DB[id] = DataSourceModel(
            id,
            name,
            scope,
            type,
            parent_id or None,
            properties,
        )

    def _create_and_save_data_source(self, data_source_config: DataSourceConfig, parent_id: Optional[str]) -> DataSource:
        data_source = self.__create_data_source(data_source_config, parent_id)
        self.save(data_source)
        return data_source

    def __create_data_source(self, data_source_config: DataSourceConfig, parent_id: Optional[str]) -> DataSource:
        data_source_config &= ConfigurationManager.data_manager_configuration
        try:
            return self.__DATA_SOURCE_CLASS_MAP[data_source_config.type](
                config_name=data_source_config.name,
                scope=data_source_config.scope,
                parent_id=parent_id,
                properties=data_source_config.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data source. " f"Type {data_source_config.type} does not exist.")
            raise InvalidDataSourceType(data_source_config.type)
