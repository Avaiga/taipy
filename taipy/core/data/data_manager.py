from typing import List, Optional, Union

from taipy.core.common.alias import DataNodeId, PipelineId, ScenarioId
from taipy.core.common.logger import TaipyLogger
from taipy.core.common.manager import Manager
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node import DataNode
from taipy.core.data.data_repository import DataRepository
from taipy.core.data.excel import ExcelDataNode
from taipy.core.data.generic import GenericDataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.data.scope import Scope
from taipy.core.data.sql import SQLDataNode
from taipy.core.exceptions.data_node import InvalidDataNodeType, MultipleDataNodeFromSameConfigWithSameParent
from taipy.core.exceptions.repository import ModelNotFound


class DataManager(Manager[DataNode]):
    """
    A Data Manager is responsible for all managing data node related capabilities.

    In particular, it is exposing methods for creating, storing, updating, retrieving, deleting data nodes.
    """

    __DATA_NODE_CLASS_MAP = {c.storage_type(): c for c in DataNode.__subclasses__()}  # type: ignore
    _repository = DataRepository(__DATA_NODE_CLASS_MAP)
    ENTITY_NAME = DataNode.__name__

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
        dn_from_data_node_config = cls._get_all_by_config_name(data_node_config.name)
        dn_from_parent = [dn for dn in dn_from_data_node_config if dn.parent_id == parent_id]
        if len(dn_from_parent) == 1:
            return dn_from_parent[0]
        elif len(dn_from_parent) > 1:
            raise MultipleDataNodeFromSameConfigWithSameParent
        else:
            return cls._create_and_set(data_node_config, parent_id)

    @classmethod
    def _create_and_set(cls, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        data_node = cls.__create(data_node_config, parent_id)
        cls.set(data_node)
        return data_node

    @classmethod
    def __create(cls, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        try:
            props = data_node_config.properties.copy()
            validity_period = props.pop("validity_period", None)
            return cls.__DATA_NODE_CLASS_MAP[data_node_config.storage_type](  # type: ignore
                config_name=data_node_config.name,
                scope=data_node_config.scope or DataNodeConfig.DEFAULT_SCOPE,
                parent_id=parent_id,
                validity_period=validity_period,
                properties=props,
            )
        except KeyError:
            raise InvalidDataNodeType(data_node_config.storage_type)

    @classmethod
    def _get_all_by_config_name(cls, config_name: str) -> List[DataNode]:
        return cls._repository.search_all("config_name", config_name)
