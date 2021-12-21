import logging
from typing import List, Optional

from taipy.common.alias import DataSourceId, PipelineId, ScenarioId
from taipy.config import DataSourceConfig
from taipy.data import CSVDataSource, PickleDataSource, SQLDataSource
from taipy.data.data_source import DataSource
from taipy.data.in_memory import InMemoryDataSource
from taipy.data.repository import DataRepository
from taipy.data.scope import Scope
from taipy.exceptions import InvalidDataSourceType
from taipy.exceptions.data_source import MultipleDataSourceFromSameConfigWithSameParent


class DataManager:
    """
    A Data Manager is responsible for all managing data source related capabilities.

    In particular, it is exposing methods for creating, storing, updating, retrieving, deleting data sources.
    """

    __DATA_SOURCE_CLASSES = {InMemoryDataSource, PickleDataSource, CSVDataSource, SQLDataSource}
    __DATA_SOURCE_CLASS_MAP = {ds_class.storage_type(): ds_class for ds_class in __DATA_SOURCE_CLASSES}  # type: ignore

    def __init__(self):
        self.repository = DataRepository(self.__DATA_SOURCE_CLASS_MAP)

    def delete_all(self):
        """Deletes all data sources."""
        self.repository.delete_all()

    def delete(self, data_source_id: str):
        """
        Deletes the data source provided as parameter.

        Parameters:
            data_source_id (str) : identifier of the data source to delete.

        Raises:
            ModelNotFound: Raised if no data source corresponds to data_source_id.
        """
        self.repository.delete(data_source_id)

    def get_or_create(
        self,
        data_source_config: DataSourceConfig,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> DataSource:
        """Gets or creates a Data Source.

        Returns the data source created from the data_source_config, by (pipeline_id and scenario_id) if it already
        exists, or creates and returns a new data_source.

        Parameters:
            data_source_config (DataSourceConfig) : data source configuration object.
            scenario_id (Optional[ScenarioId]) : id of the scenario creating the data source.
            pipeline_id (Optional[PipelineId]) : id of the pipeline creating the data source.

        Raises:
            MultipleDataSourceFromSameConfigWithSameParent: Raised if more than 1 data source already exist with same
                config, and the same parent id (scenario_id, or pipeline_id depending on the scope of the data source).
            InvalidDataSourceType: Raised if the type of the data source config is invalid.
        """
        scope = data_source_config.scope
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        ds_from_data_source_config = self._get_all_by_config_name(data_source_config.name)
        ds_from_parent = [ds for ds in ds_from_data_source_config if ds.parent_id == parent_id]
        if len(ds_from_parent) == 1:
            return ds_from_parent[0]
        elif len(ds_from_parent) > 1:
            logging.error("Multiple data sources from same config exist with the same parent_id.")
            raise MultipleDataSourceFromSameConfigWithSameParent
        else:
            return self._create_and_set(data_source_config, parent_id)

    def set(self, data_source: DataSource):
        """
        Saves or Updates the data source given as parameter.

        Parameters:
            data_source (DataSource) : data source to save or update.
        """
        self.repository.save(data_source)

    def get(self, data_source_id: DataSourceId) -> DataSource:
        """
        Gets the data source corresponding to the identifier given as parameter.

        Parameters:
            data_source_id (DataSourceId) : data source to get.

        Raises:
            ModelNotFound: Raised if no data source corresponds to data_source_id.
        """
        return self.repository.load(data_source_id)

    def get_all(self) -> List[DataSource]:
        """Returns the list of all existing data sources."""
        return self.repository.load_all()

    def _get_all_by_config_name(self, config_name: str) -> List[DataSource]:
        return self.repository.search_all("config_name", config_name)

    def _create_and_set(self, data_source_config: DataSourceConfig, parent_id: Optional[str]) -> DataSource:
        data_source = self.__create(data_source_config, parent_id)
        self.set(data_source)
        return data_source

    def __create(self, data_source_config: DataSourceConfig, parent_id: Optional[str]) -> DataSource:
        try:
            return self.__DATA_SOURCE_CLASS_MAP[data_source_config.storage_type](  # type: ignore
                config_name=data_source_config.name,
                scope=data_source_config.scope or DataSourceConfig.DEFAULT_SCOPE,
                parent_id=parent_id,
                properties=data_source_config.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data source. " f"Type {data_source_config.storage_type} does not exist.")
            raise InvalidDataSourceType(data_source_config.storage_type)
