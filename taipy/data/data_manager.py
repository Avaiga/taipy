import logging
from typing import List, Optional, Union

from taipy.common.alias import DataNodeId, PipelineId, ScenarioId
from taipy.config.data_node_config import DataNodeConfig
from taipy.data.csv import CSVDataNode
from taipy.data.data_node import DataNode
from taipy.data.data_repository import DataRepository
from taipy.data.excel import ExcelDataNode
from taipy.data.in_memory import InMemoryDataNode
from taipy.data.pickle import PickleDataNode
from taipy.data.scope import Scope
from taipy.data.sql import SQLDataNode
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
    repository = DataRepository(__DATA_NODE_CLASS_MAP)

    @classmethod
    def delete_all(cls):
        """Deletes all data nodes."""
        cls.repository.delete_all()

    @classmethod
    def delete(cls, data_node_id: str):
        """
        Deletes the data node provided as parameter.

        Parameters:
            data_node_id (str) : identifier of the data node to delete.

        Raises:
            ModelNotFound: Raised if no data node corresponds to data_node_id.
        """
        cls.repository.delete(data_node_id)

    @classmethod
    def get_or_create(
        cls,
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
        ds_from_data_node_config = cls._get_all_by_config_name(data_node_config.name)
        ds_from_parent = [ds for ds in ds_from_data_node_config if ds.parent_id == parent_id]
        if len(ds_from_parent) == 1:
            return ds_from_parent[0]
        elif len(ds_from_parent) > 1:
            logging.error("Multiple data nodes from same config exist with the same parent_id.")
            raise MultipleDataNodeFromSameConfigWithSameParent
        else:
            return cls._create_and_set(data_node_config, parent_id)

    @classmethod
    def set(cls, data_node: DataNode):
        """
        Saves or Updates the data node given as parameter.

        Parameters:
            data_node (DataNode) : data node to save or update.
        """
        cls.repository.save(data_node)

    @classmethod
    def get(cls, data_node: Union[DataNode, DataNodeId]) -> DataNode:
        """
        Gets the data node corresponding to the DataNode or the identifier given as parameter.

        Parameters:
            data_node (Union[DataNode, DataNodeId]) : data node to get.

        Raises:
            ModelNotFound: Raised if no data node corresponds to data_node_id.
        """
        try:
            data_node_id = data_node.id if isinstance(data_node, DataNode) else data_node
            return cls.repository.load(data_node_id)
        except ModelNotFound:
            logging.error(f"DataNode: {data_node_id} does not exist.")
            raise NonExistingDataNode(data_node_id)

    @classmethod
    def get_all(cls) -> List[DataNode]:
        """Returns the list of all existing data nodes."""
        return cls.repository.load_all()

    @classmethod
    def _get_all_by_config_name(cls, config_name: str) -> List[DataNode]:
        return cls.repository.search_all("config_name", config_name)

    @classmethod
    def _create_and_set(cls, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        data_node = cls.__create(data_node_config, parent_id)
        cls.set(data_node)
        return data_node

    @classmethod
    def __create(cls, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        try:
            props = data_node_config.properties.copy()
            days = props.pop("validity_days", None)
            hours = props.pop("validity_hours", None)
            minutes = props.pop("validity_minutes", None)
            return cls.__DATA_NODE_CLASS_MAP[data_node_config.storage_type](  # type: ignore
                config_name=data_node_config.name,
                scope=data_node_config.scope or DataNodeConfig.DEFAULT_SCOPE,
                parent_id=parent_id,
                validity_days=days,
                validity_hours=hours,
                validity_minutes=minutes,
                properties=props,

            )
        except KeyError:
            logging.error(f"Cannot create Data node. " f"Type {data_node_config.storage_type} does not exist.")
            raise InvalidDataNodeType(data_node_config.storage_type)
