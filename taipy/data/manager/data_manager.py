import logging
from typing import Dict, List, Optional

from taipy.configuration import ConfigurationManager

from taipy.data import CSVDataSource, EmbeddedDataSource
from taipy.data.data_source import DataSource
from taipy.data.data_source_config import DataSourceConfig
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
    __DATA_SOURCE_CONFIG_DB: Dict[str, DataSourceConfig] = {}
    __DATA_SOURCE_CLASSES = {EmbeddedDataSource, CSVDataSource}
    __DATA_SOURCE_CLASS_MAP = {v.type(): v for v in __DATA_SOURCE_CLASSES}

    def __fetch_data_source(self, data_source_config: DataSourceConfig) -> DataSource:
        data_source_config &= ConfigurationManager.data_manager_configuration
        return self.__DATA_SOURCE_CLASS_MAP[data_source_config.type](
            name=data_source_config.name,
            scope=data_source_config.scope,
            properties=data_source_config.properties,
        )

    def __persist_data_source(self, data_source_config: DataSourceConfig) -> DataSource:
        try:
            data_source = self.__fetch_data_source(data_source_config)
        except KeyError:
            logging.error(f"Cannot create Data source entity. " f"Type {data_source_config.type} does not exist.")
            raise InvalidDataSourceType(data_source_config.type)
        self.save_data_source(data_source)
        self.register_data_source_config(data_source_config)
        return data_source

    def get_all(self) -> Dict[str, DataSourceConfig]:
        return self.__DATA_SOURCE_CONFIG_DB

    def delete_all(self):
        self.__DATA_SOURCE_MODEL_DB: Dict[str, DataSourceModel] = {}
        self.__DATA_SOURCE_CONFIG_DB: Dict[str, DataSourceConfig] = {}

    def register_data_source_config(self, data_source: DataSourceConfig):
        self.__DATA_SOURCE_CONFIG_DB[data_source.name] = data_source

    def get_data_source_config(self, name) -> Optional[DataSourceConfig]:
        return self.__DATA_SOURCE_CONFIG_DB.get(name)

    def get_or_create(self, data_source_config: DataSourceConfig) -> DataSource:
        ds = self.get_data_source_config(data_source_config.name)
        if ds is not None and ds.scope > Scope.PIPELINE:
            return self.__fetch_data_source(data_source_config)

        return self.__persist_data_source(data_source_config)

    def create_data_source(self, data_source_config: DataSourceConfig) -> DataSource:
        return self.__persist_data_source(data_source_config)

    def save_data_source(self, data_source):
        self.create_data_source_model(
            data_source.id,
            data_source.name,
            data_source.scope,
            data_source.type(),
            data_source.properties,
        )

    def get_data_source(self, data_source_id: str) -> DataSource:
        model = self.fetch_data_source_model(data_source_id)
        return self.__DATA_SOURCE_CLASS_MAP[model.type](
            name=model.name,
            scope=model.scope,
            id=model.id,
            properties=model.data_source_properties,
        )

    def get_data_sources(self) -> List[DataSource]:
        return [self.get_data_source(model.id) for model in self.__DATA_SOURCE_MODEL_DB.values()]

    def create_data_source_model(self, id: str, name: str, scope: Scope, type: str, properties: dict):
        self.__DATA_SOURCE_MODEL_DB[id] = DataSourceModel(
            id,
            name,
            scope,
            type,
            properties,
        )

    def fetch_data_source_model(self, id) -> DataSourceModel:
        return self.__DATA_SOURCE_MODEL_DB[id]
