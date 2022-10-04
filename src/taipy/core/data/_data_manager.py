# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
from typing import Dict, Iterable, Optional, Set, Union

from taipy.config.common.scope import Scope

from .._manager._manager import _Manager
from ..common.alias import DataNodeId, PipelineId, ScenarioId
from ..config.data_node_config import DataNodeConfig
from ..exceptions.exceptions import InvalidDataNodeType
from ._data_repository_factory import _DataRepositoryFactory
from .data_node import DataNode
from .pickle import PickleDataNode


class _DataManager(_Manager[DataNode]):

    __DATA_NODE_CLASS_MAP = DataNode._class_map()  # type: ignore
    _repository = _DataRepositoryFactory._build_repository()  # type: ignore
    _ENTITY_NAME = DataNode.__name__

    @classmethod
    def _bulk_get_or_create(
        cls,
        data_node_configs: Set[DataNodeConfig],
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> Dict[DataNodeConfig, DataNode]:
        dn_configs_and_owner_id = []

        for dn_config in data_node_configs:
            scope = dn_config.scope
            owner_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
            dn_configs_and_owner_id.append((dn_config, owner_id))

        data_nodes = cls._repository._get_by_configs_and_owner_ids(dn_configs_and_owner_id)  # type: ignore

        return {
            dn_config: data_nodes.get((dn_config, owner_id)) or cls._create_and_set(dn_config, owner_id)
            for dn_config, owner_id in dn_configs_and_owner_id
        }

    @classmethod
    def _create_and_set(cls, data_node_config: DataNodeConfig, owner_id: Optional[str]) -> DataNode:
        data_node = cls.__create(data_node_config, owner_id)
        cls._set(data_node)
        return data_node

    @classmethod
    def __create(cls, data_node_config: DataNodeConfig, owner_id: Optional[str]) -> DataNode:
        try:
            props = data_node_config._properties.copy()
            validity_period = props.pop("validity_period", None)
            return cls.__DATA_NODE_CLASS_MAP[data_node_config.storage_type](  # type: ignore
                config_id=data_node_config.id,
                scope=data_node_config.scope or DataNodeConfig._DEFAULT_SCOPE,
                owner_id=owner_id,
                cacheable=data_node_config.cacheable,
                validity_period=validity_period,
                properties=props,
            )
        except KeyError:
            raise InvalidDataNodeType(data_node_config.storage_type)

    @classmethod
    def _clean_pickle_file(cls, data_node: Union[DataNode, DataNodeId]):
        data_node = cls._get(data_node) if isinstance(data_node, str) else data_node
        if not isinstance(data_node, PickleDataNode):
            return
        if data_node.is_generated and os.path.exists(data_node.path):
            os.remove(data_node.path)

    @classmethod
    def _clean_pickle_files(cls, data_nodes: Iterable[Union[DataNode, DataNodeId]]):
        for data_node in data_nodes:
            cls._clean_pickle_file(data_node)

    @classmethod
    def _delete(cls, data_node_id: DataNodeId):  # type:ignore
        cls._clean_pickle_file(data_node_id)
        super()._delete(data_node_id)

    @classmethod
    def _delete_many(cls, data_node_ids: Iterable[DataNodeId]):  # type:ignore
        cls._clean_pickle_files(data_node_ids)
        super()._delete_many(data_node_ids)

    @classmethod
    def _delete_all(cls):
        cls._clean_pickle_files(cls._get_all())
        super()._delete_all()
