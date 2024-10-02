# Copyright 2021-2024 Avaiga Private Limited
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
from typing import Dict, Iterable, List, Optional, Set, Union

from taipy.common.config import Config
from taipy.common.config._config import _Config
from taipy.common.config.common.scope import Scope

from .._manager._manager import _Manager
from .._version._version_mixin import _VersionMixin
from ..config.data_node_config import DataNodeConfig
from ..cycle.cycle_id import CycleId
from ..exceptions.exceptions import InvalidDataNodeType
from ..notification import Event, EventEntityType, EventOperation, Notifier, _make_event
from ..reason import NotGlobalScope, ReasonCollection, WrongConfigType
from ..scenario.scenario_id import ScenarioId
from ..sequence.sequence_id import SequenceId
from ._data_fs_repository import _DataFSRepository
from ._file_datanode_mixin import _FileDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId


class _DataManager(_Manager[DataNode], _VersionMixin):
    _DATA_NODE_CLASS_MAP = DataNode._class_map()  # type: ignore
    _ENTITY_NAME = DataNode.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.DATA_NODE
    _repository: _DataFSRepository

    @classmethod
    def _bulk_get_or_create(
        cls,
        data_node_configs: List[DataNodeConfig],
        cycle_id: Optional[CycleId] = None,
        scenario_id: Optional[ScenarioId] = None,
    ) -> Dict[DataNodeConfig, DataNode]:
        data_node_configs = [Config.data_nodes[dnc.id] for dnc in data_node_configs]
        dn_configs_and_owner_id = []
        for dn_config in data_node_configs:
            scope = dn_config.scope
            owner_id: Union[Optional[SequenceId], Optional[ScenarioId], Optional[CycleId]]
            if scope == Scope.SCENARIO:
                owner_id = scenario_id
            elif scope == Scope.CYCLE:
                owner_id = cycle_id
            else:
                owner_id = None
            dn_configs_and_owner_id.append((dn_config, owner_id))

        data_nodes = cls._repository._get_by_configs_and_owner_ids(
            dn_configs_and_owner_id, cls._build_filters_with_version(None)
        )

        return {
            dn_config: data_nodes.get((dn_config, owner_id)) or cls._create_and_set(dn_config, owner_id, None)
            for dn_config, owner_id in dn_configs_and_owner_id
        }

    @classmethod
    def _can_create(cls, config: Optional[DataNodeConfig] = None) -> ReasonCollection:
        config_id = getattr(config, "id", None) or str(config)
        reason_collection = ReasonCollection()

        if config is not None:
            if not isinstance(config, DataNodeConfig):
                reason_collection._add_reason(config_id, WrongConfigType(config_id, DataNodeConfig.__name__))
            elif config.scope is not Scope.GLOBAL:
                reason_collection._add_reason(config_id, NotGlobalScope(config_id))

        return reason_collection

    @classmethod
    def _create_and_set(
        cls, data_node_config: DataNodeConfig, owner_id: Optional[str], parent_ids: Optional[Set[str]]
    ) -> DataNode:
        data_node = cls.__create(data_node_config, owner_id, parent_ids)
        cls._set(data_node)
        Notifier.publish(_make_event(data_node, EventOperation.CREATION))
        return data_node

    @classmethod
    def __create(
        cls, data_node_config: DataNodeConfig, owner_id: Optional[str], parent_ids: Optional[Set[str]]
    ) -> DataNode:
        try:
            version = cls._get_latest_version()
            props = data_node_config._properties.copy()

            if data_node_config.storage_type:
                storage_type = data_node_config.storage_type
            else:
                storage_type = Config.sections[DataNodeConfig.name][_Config.DEFAULT_KEY].storage_type

            return cls._DATA_NODE_CLASS_MAP[storage_type](
                config_id=data_node_config.id,
                scope=data_node_config.scope or DataNodeConfig._DEFAULT_SCOPE,
                validity_period=data_node_config.validity_period,
                owner_id=owner_id,
                parent_ids=parent_ids,
                version=version,
                properties=props,
            )
        except KeyError:
            raise InvalidDataNodeType(data_node_config.storage_type) from None

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[DataNode]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    @classmethod
    def _clean_generated_file(cls, data_node: DataNode) -> None:
        if not isinstance(data_node, _FileDataNodeMixin):
            return
        if data_node.is_generated and os.path.exists(data_node.path):
            os.remove(data_node.path)

    @classmethod
    def _clean_generated_files(cls, data_nodes: Iterable[DataNode]) -> None:
        for data_node in data_nodes:
            cls._clean_generated_file(data_node)

    @classmethod
    def _delete(cls, data_node_id: DataNodeId) -> None:
        if data_node := cls._get(data_node_id, None):
            cls._clean_generated_file(data_node)
        super()._delete(data_node_id)

    @classmethod
    def _delete_many(cls, data_node_ids: Iterable[DataNodeId]) -> None:
        data_nodes = []
        for data_node_id in data_node_ids:
            if data_node := cls._get(data_node_id):
                data_nodes.append(data_node)
        cls._clean_generated_files(data_nodes)
        super()._delete_many(data_node_ids)

    @classmethod
    def _delete_all(cls) -> None:
        data_nodes = cls._get_all()
        cls._clean_generated_files(data_nodes)
        super()._delete_all()

    @classmethod
    def _delete_by_version(cls, version_number: str) -> None:
        data_nodes = cls._get_all(version_number)
        cls._clean_generated_files(data_nodes)
        cls._repository._delete_by(attribute="version", value=version_number)
        Notifier.publish(
            Event(EventEntityType.DATA_NODE, EventOperation.DELETION, metadata={"delete_by_version": version_number})
        )

    @classmethod
    def _get_by_config_id(cls, config_id: str, version_number: Optional[str] = None) -> List[DataNode]:
        """
        Get all datanodes by its config id.
        """
        filters = cls._build_filters_with_version(version_number)
        if not filters:
            filters = [{}]
        for fil in filters:
            fil.update({"config_id": config_id})
        return cls._repository._load_all(filters)
