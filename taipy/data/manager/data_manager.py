import logging
from typing import Dict, List

from taipy.config import Config, DataSourceConfig
from taipy.data import CSVDataSource, DataRepository, EmbeddedDataSource
from taipy.data.data_source import DataSource
from taipy.data.data_source_model import DataSourceModel
from taipy.data.scope import Scope
from taipy.exceptions import InvalidDataSourceType

"""
A Data Manager is entity responsible for keeping track and retrieving Taipy DataSources.
The Data Manager will facilitate data access between Taipy Modules.
"""


class DataManager:
    # This represents a database table that maintains our DataSource References.
    __DATA_SOURCE_MODEL_DB: Dict[str, DataSourceModel] = {}
    __DATA_SOURCE_CLASSES = {EmbeddedDataSource, CSVDataSource}
    __DATA_SOURCE_CLASS_MAP = {v.type(): v for v in __DATA_SOURCE_CLASSES}

    def __init__(self):
        self.repository = DataRepository(model=DataSourceModel, dir_name="sources")

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

        return self.create_data_source(data_source_config)

    def create_data_source(self, data_source_config: DataSourceConfig) -> DataSource:
        data_source = self.__create_data_source(data_source_config)
        self.__persist_data_source(data_source_config, data_source)

        return data_source

    def save_data_source(self, data_source: DataSource):
        self.create_data_source_model(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.type(),
            data_source.properties,
        )

    def get_data_source(self, data_source_id: str) -> DataSource:
        model = self.fetch_data_source_model(data_source_id)
        return self.__DATA_SOURCE_CLASS_MAP[model.type](
            config_name=model.name,
            scope=model.scope,
            id=model.id,
            properties=model.data_source_properties,
        )

    def get_data_sources(self) -> List[DataSource]:
        return [self.get_data_source(model.id) for model in self.__DATA_SOURCE_MODEL_DB.values()]

    def create_data_source_model(self, id: str, name: str, scope: Scope, type: str, properties: dict):
        model = DataSourceModel(
            id,
            name,
            scope,
            type,
            properties,
        )
        # Old in memory storage system
        self.__DATA_SOURCE_MODEL_DB[id] = model

        # New Storage
        self.repository.save(model)

    def fetch_data_source_model(self, id) -> DataSourceModel:
        return self.repository.get(id)
