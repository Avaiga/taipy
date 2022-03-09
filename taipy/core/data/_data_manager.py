from typing import List, Optional, Union

from taipy.core.common._manager import _Manager
from taipy.core.common.alias import PipelineId, ScenarioId
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data._data_repository import _DataRepository
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node import DataNode
from taipy.core.data.excel import ExcelDataNode
from taipy.core.data.generic import GenericDataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.data.scope import Scope
from taipy.core.data.sql import SQLDataNode
from taipy.core.exceptions.data_node import InvalidDataNodeType, MultipleDataNodeFromSameConfigWithSameParent


class _DataManager(_Manager[DataNode]):

    __DATA_NODE_CLASS_MAP = {c.storage_type(): c for c in DataNode.__subclasses__()}  # type: ignore
    _repository = _DataRepository(__DATA_NODE_CLASS_MAP)
    _ENTITY_NAME = DataNode.__name__

    @classmethod
    def _get_or_create(
        cls,
        data_node_config: DataNodeConfig,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> DataNode:
        scope = data_node_config.scope
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        dn_from_data_node_config = cls._get_all_by_config_id(data_node_config.id)
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
        cls._set(data_node)
        return data_node

    @classmethod
    def __create(cls, data_node_config: DataNodeConfig, parent_id: Optional[str]) -> DataNode:
        try:
            props = data_node_config.properties.copy()
            validity_period = props.pop("validity_period", None)
            return cls.__DATA_NODE_CLASS_MAP[data_node_config.storage_type](  # type: ignore
                config_id=data_node_config.id,
                scope=data_node_config.scope or DataNodeConfig._DEFAULT_SCOPE,
                parent_id=parent_id,
                validity_period=validity_period,
                properties=props,
            )
        except KeyError:
            raise InvalidDataNodeType(data_node_config.storage_type)

    @classmethod
    def _get_all_by_config_id(cls, config_id: str) -> List[DataNode]:
        return cls._repository._search_all("config_id", config_id)
