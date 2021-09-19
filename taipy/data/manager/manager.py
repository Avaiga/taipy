import sys
from typing import List

from taipy.data.entity import (
    CSVDataSourceEntity,
    DataSource,
    DataSourceEntity,
    EmbeddedDataSourceEntity,
)
from taipy.data.data_source_model import DataSourceModel
from taipy.data.scope import Scope

"""
A Data Manager is entity responsible for keeping track and retrieving Taipy DataSources. The Data Manager will
facilitate data access between Taipy Modules.
"""


class DataManager:
    # This represents a database table that maintains our DataSource References.
    __DATA_SOURCE_MODEL_DB: List[DataSourceModel] = []
    __DATA_SOURCE_DB: List[DataSource] = []
    __ENTITY_CLASSES = {EmbeddedDataSourceEntity, CSVDataSourceEntity}
    __ENTITY_CLASS_MAP = {v.type: v for v in __ENTITY_CLASSES}

    def register_data_source(self, data_source: DataSource):
        self.__DATA_SOURCE_DB.append(data_source)

    def get_data_source(self, name) -> DataSource:
        data_source = None
        for ds in self.__DATA_SOURCE_DB:
            # Not sure if we need to handle missing DataSource here or in the function that
            # calls fetch_data_source. Something to consider in the near future.
            if ds.name == name:
                data_source = ds
                break
        return data_source

    def create_data_source_entity(self, data_source: DataSource) -> DataSourceEntity:
        data_source_entity = self.__ENTITY_CLASS_MAP[data_source.type](
            data_source.name, data_source.scope, **data_source.properties
        )
        self.save_data_source_entity(data_source_entity)
        return data_source_entity

    def save_data_source_entity(self, data_source_entity):
        self.create_data_source_model(
            data_source_entity.id,
            data_source_entity.name,
            data_source_entity.type,
            data_source_entity.properties,
        )

    def get_data_source_entity(self, data_source_id: str) -> DataSourceEntity:
        model = self.fetch_data_source_model(data_source_id)
        return model.implementation_class_name(
            model.name,
            model.implementation_class_name,
            model.scope,
            model.id,
            model.properties,
        )

    def create_data_source_model(
        self, id: str, name: str, data_source_class: str, properties: dict
    ):
        self.__DATA_SOURCE_MODEL_DB.append(
            DataSourceModel(
                id,
                name,
                Scope.SCENARIO,
                data_source_class,
                properties,
            )
        )

    def fetch_data_source_model(self, id):
        data_source = None

        for ds in self.__DATA_SOURCE_MODEL_DB:
            # Not sure if we need to handle missing DataSource here or in the function that
            # calls fetch_data_source. Something to consider in the near future.
            if ds.id == id:
                data_source_class = getattr(sys.modules[__name__], ds.type)
                data_source = data_source_class(
                    ds.id, ds.name, ds.scope, ds.data_source_properties
                )
                break

        return data_source
