import logging
from typing import Dict, List

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
    __DATA_SOURCE_DB: Dict[str, DataSourceConfig] = {}
    __ENTITY_CLASSES = {EmbeddedDataSource, CSVDataSource}
    __ENTITY_CLASS_MAP = {v.type(): v for v in __ENTITY_CLASSES}

    def delete_all(self):
        self.__DATA_SOURCE_MODEL_DB: Dict[str, DataSourceModel] = {}
        self.__DATA_SOURCE_DB: Dict[str, DataSourceConfig] = {}

    def register_data_source(self, data_source: DataSourceConfig):
        self.__DATA_SOURCE_DB[data_source.name] = data_source

    def get_data_source(self, name) -> DataSourceConfig:
        return self.__DATA_SOURCE_DB[name]

    def create_data_source_entity(self, data_source: DataSourceConfig) -> DataSource:
        data_source &= ConfigurationManager.data_manager_configuration
        try:
            data_source_entity = self.__ENTITY_CLASS_MAP[data_source.type](
                name=data_source.name,
                scope=data_source.scope,
                properties=data_source.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data source entity. " f"Type {data_source.type} does not exist.")
            raise InvalidDataSourceType(data_source.type)
        self.save_data_source_entity(data_source_entity)
        return data_source_entity

    def save_data_source_entity(self, data_source_entity):
        self.create_data_source_model(
            data_source_entity.id,
            data_source_entity.name,
            data_source_entity.scope,
            data_source_entity.type(),
            data_source_entity.properties,
        )

    def get_data_source_entity(self, data_source_id: str) -> DataSource:
        model = self.fetch_data_source_model(data_source_id)
        return self.__ENTITY_CLASS_MAP[model.type](
            name=model.name,
            scope=model.scope,
            id=model.id,
            properties=model.data_source_properties,
        )

    def get_data_source_entities(self) -> List[DataSource]:
        return [self.get_data_source_entity(model.id) for model in self.__DATA_SOURCE_MODEL_DB.values()]

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
