import logging
from typing import Any, Callable, Dict, List, Optional

from taipy.config import DataSourceConfig
from taipy.data import CSVDataSource, DataRepository, PickleDataSource
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
    __DATA_SOURCE_CLASSES = {InMemoryDataSource, PickleDataSource, CSVDataSource}
    __DATA_SOURCE_CLASS_MAP = {v.type(): v for v in __DATA_SOURCE_CLASSES}  # type: ignore

    def __init__(self):
        self.repository = DataRepository(model=DataSourceModel, dir_name="sources")

    def delete_all(self):
        self.repository.delete_all()

    def get_or_create(
        self, data_source_config: DataSourceConfig, scenario_id: Optional[str] = None, pipeline_id: Optional[str] = None
    ) -> DataSource:
        scope = data_source_config.scope
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        ds_from_data_source_config = self._get_all_by_config_name(data_source_config.name)
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
        model = DataSourceModel(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.type(),
            data_source.parent_id,
            data_source.properties,
        )
        self.repository.save(model)

    def get(self, data_source_id: str) -> DataSource:
        model = self.repository.get(data_source_id)
        return self.__to_data_source(model)

    def get_all(self) -> List[DataSource]:
        return [self.__to_data_source(model) for model in self.repository.get_all()]

    def _get_all_by_config_name(self, config_name: str) -> List[DataSource]:
        return [self.__to_data_source(model) for model in self.repository.search_all("config_name", config_name)]

    def _create_and_save_data_source(
        self, data_source_config: DataSourceConfig, parent_id: Optional[str]
    ) -> DataSource:
        data_source = self.__create_data_source(data_source_config, parent_id)
        self.save(data_source)
        return data_source

    def __to_data_source(self, model):
        return self.__DATA_SOURCE_CLASS_MAP[model.type](
            config_name=model.config_name,
            scope=model.scope,
            id=model.id,
            parent_id=model.parent_id,
            properties=model.data_source_properties,
        )

    def __create_data_source(self, data_source_config: DataSourceConfig, parent_id: Optional[str]) -> DataSource:
        try:
            return self.__DATA_SOURCE_CLASS_MAP[data_source_config.type](  # type: ignore
                config_name=data_source_config.name,
                scope=data_source_config.scope,
                parent_id=parent_id,
                properties=data_source_config.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data source. " f"Type {data_source_config.type} does not exist.")
            raise InvalidDataSourceType(data_source_config.type)
