import logging
from typing import List, Optional, Union

from taipy.common.alias import DataNodeId, PipelineId, ScenarioId
from taipy.config.data_node_config import DataNodeConfig
from taipy.data import CSVDataNode, PickleDataNode, SQLDataNode
from taipy.data.data_node import DataNode
from taipy.data.excel import ExcelDataNode
from taipy.data.in_memory import InMemoryDataNode
from taipy.data.repository import DataRepository
from taipy.data.scope import Scope
from taipy.exceptions import ModelNotFound
from taipy.exceptions.data_node import (
    InvalidDataNodeType,
    MultipleDataNodeFromSameConfigWithSameParent,
    NonExistingDataNode,
)


class DataManager:
    """
    A Data Manager is responsible for all managing data node related capabilities.

    In particular, it is exposing methods for creating, storing, updating, retrieving, deleting data nodes.
    """

    __DATA_NODE_CLASSES = {InMemoryDataNode, PickleDataNode, CSVDataNode, SQLDataNode, ExcelDataNode}
    __DATA_NODE_CLASS_MAP = {ds_class.storage_type(): ds_class for ds_class in __DATA_NODE_CLASSES}  # type: ignore

    def __init__(self):
        self.repository = DataRepository(self.__DATA_NODE_CLASS_MAP)

    def delete_all(self):
        """Deletes all data nodes."""
        self.repository.delete_all()

    def delete(self, data_node_id: str):
        """
        Deletes the data node provided as parameter.

        Parameters:
            data_node_id (str) : identifier of the data node to delete.

        Raises:
            ModelNotFound: Raised if no data node corresponds to data_node_id.
        """
        self.repository.delete(data_node_id)

    def get_or_create(
        self,
        data_node_config: DataNodeConfig,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> DataNode:
        """Gets or creates a Data Node.

        Returns the data node created from the data_node_config, by (pipeline_id and scenario_id) if it already
        exists, or creates and returns a new data_node.

        Parameters:
            data_node_config (DataNodeConfig) : data node configuration object.
            scenario_id (Optional[ScenarioId]) : id of the scenario creating the data node.
            pipeline_id (Optional[PipelineId]) : id of the pipeline creating the data node.

        Raises:
            MultipleDataNodeFromSameConfigWithSameParent: Raised if more than 1 data node already exist with same
                config, and the same parent id (scenario_id, or pipeline_id depending on the scope of the data node).
            InvalidDataNodeType: Raised if the type of the data node config is invalid.
        """
        scope = data_node_config.scope
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        ds_from_data_node_config = self._get_all_by_config_name(data_node_config.name)
        ds_from_parent = [ds for ds in ds_from_data_node_config if ds.parent_id == parent_id]
        if len(ds_from_parent) == 1:
            return ds_from_parent[0]
        elif len(ds_from_parent) > 1:
            logging.error("Multiple data nodes from same config exist with the same parent_id.")
            raise MultipleDataNodeFromSameConfigWithSameParent
        else:
            return self._create_and_set(data_node_config, parent_id)

    def set(self, data_node: DataNode):
        """
        Saves or Updates the data node given as parameter.

        Parameters:
            data_node (DataNode) : data node to save or update.
        """
        self.repository.save(data_node)

    def get(self, data_node: Union[DataNode, DataNodeId]) -> DataNode:
        """
        Gets the data node corresponding to the DataNode or the identifier given as parameter.

        Parameters:
            data_node (Union[DataNode, DataNodeId]) : data node to get.

        Raises:
            ModelNotFound: Raised if no data node corresponds to data_node_id.
        """
        try:
            data_node_id = data_node.id if isinstance(data_node, DataNode) else data_node
            return self.repository.load(data_node_id)
        except ModelNotFound:
            logging.error(f"DataNode: {data_node_id} does not exist.")
            raise NonExistingDataNode(data_node_id)

    def get_all(self) -> List[DataNode]:
        """Returns the list of all existing data nodes."""
        return self.repository.load_all()

    def _get_all_by_config_name(self, config_name: str) -> List[DataNode]:
        return self.repository.search_all("config_name", config_name)

    def _create_and_set(self, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        data_node = self.__create(data_node_config, parent_id)
        self.set(data_node)
        return data_node

    def __create(self, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        try:
            return self.__DATA_NODE_CLASS_MAP[data_node_config.storage_type](  # type: ignore
                config_name=data_node_config.name,
                scope=data_node_config.scope or DataNodeConfig.DEFAULT_SCOPE,
                parent_id=parent_id,
                properties=data_node_config.properties,
            )
        except KeyError:
            logging.error(f"Cannot create Data node. " f"Type {data_node_config.storage_type} does not exist.")
            raise InvalidDataNodeType(data_node_config.storage_type)
