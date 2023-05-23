# Copyright 2023 Avaiga Private Limited
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

from taipy.config._config import _Config
from taipy.config.common.scope import Scope
from taipy.config.config import Config

from .._backup._backup import append_to_backup_file, remove_from_backup_file
from .._manager._manager import _Manager
from .._version._version_manager_factory import _VersionManagerFactory
from ..config.data_node_config import DataNodeConfig
from ..cycle.cycle_id import CycleId
from ..exceptions.exceptions import InvalidDataNodeType
from ..notification import EventEntityType, EventOperation, _publish_event
from ..pipeline.pipeline_id import PipelineId
from ..scenario.scenario_id import ScenarioId
from ._data_repository_factory import _DataRepositoryFactory
from .abstract_file import _AbstractFileDataNode
from .data_node import DataNode
from .data_node_id import DataNodeId
from .pickle import PickleDataNode


class _DataManager(_Manager[DataNode]):
    __DATA_NODE_CLASS_MAP = DataNode._class_map()  # type: ignore
    _repository = _DataRepositoryFactory._build_repository()  # type: ignore
    _ENTITY_NAME = DataNode.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.DATA_NODE

    @classmethod
    def _bulk_get_or_create(
        cls,
        data_node_configs: Set[DataNodeConfig],
        cycle_id: Optional[CycleId] = None,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> Dict[DataNodeConfig, DataNode]:
        dn_configs_and_owner_id = []
        for dn_config in data_node_configs:
            scope = dn_config.scope
            owner_id: Union[Optional[PipelineId], Optional[ScenarioId], Optional[CycleId]]
            if scope == Scope.PIPELINE:
                owner_id = pipeline_id
            elif scope == Scope.SCENARIO:
                owner_id = scenario_id
            elif scope == Scope.CYCLE:
                owner_id = cycle_id
            else:
                owner_id = None
            dn_configs_and_owner_id.append((dn_config, owner_id))

        data_nodes = cls._repository._get_by_configs_and_owner_ids(dn_configs_and_owner_id)  # type: ignore

        return {
            dn_config: data_nodes.get((dn_config, owner_id)) or cls._create_and_set(dn_config, owner_id, None)
            for dn_config, owner_id in dn_configs_and_owner_id
        }

    @classmethod
    def _create_and_set(
        cls, data_node_config: DataNodeConfig, owner_id: Optional[str], parent_ids: Optional[Set[str]]
    ) -> DataNode:
        data_node = cls.__create(data_node_config, owner_id, parent_ids)
        cls._set(data_node)
        if isinstance(data_node, _AbstractFileDataNode):
            append_to_backup_file(new_file_path=data_node._path)
        _publish_event(cls._EVENT_ENTITY_TYPE, data_node.id, EventOperation.CREATION, None)
        return data_node

    @classmethod
    def __create(
        cls, data_node_config: DataNodeConfig, owner_id: Optional[str], parent_ids: Optional[Set[str]]
    ) -> DataNode:
        try:
            version = _VersionManagerFactory._build_manager()._get_latest_version()
            props = data_node_config._properties.copy()
            validity_period = props.pop("validity_period", None)

            if data_node_config.storage_type:
                storage_type = data_node_config.storage_type
            else:
                storage_type = Config.sections[DataNodeConfig.name][_Config.DEFAULT_KEY].storage_type

            return cls.__DATA_NODE_CLASS_MAP[storage_type](
                config_id=data_node_config.id,
                scope=data_node_config.scope or DataNodeConfig._DEFAULT_SCOPE,
                owner_id=owner_id,
                parent_ids=parent_ids,
                version=version,
                validity_period=validity_period,
                properties=props,
            )
        except KeyError:
            raise InvalidDataNodeType(data_node_config.storage_type)

    @classmethod
    def _clean_pickle_file(cls, data_node: DataNode):
        if not isinstance(data_node, PickleDataNode):
            return
        if data_node.is_generated and os.path.exists(data_node.path):
            os.remove(data_node.path)

    @classmethod
    def _clean_pickle_files(cls, data_nodes: Iterable[DataNode]):
        for data_node in data_nodes:
            cls._clean_pickle_file(data_node)

    @classmethod
    def _remove_dn_file_path_in_backup_file(cls, data_node: DataNode):
        if isinstance(data_node, _AbstractFileDataNode):
            remove_from_backup_file(to_remove_file_path=data_node.path)

    @classmethod
    def _remove_dn_file_paths_in_backup_file(cls, data_nodes: Iterable[DataNode]):
        for data_node in data_nodes:
            if isinstance(data_node, _AbstractFileDataNode):
                remove_from_backup_file(to_remove_file_path=data_node.path)

    @classmethod
    def _delete(cls, data_node_id: DataNodeId):
        data_node = cls._get(data_node_id, None)
        super()._delete(data_node_id)
        if data_node:
            cls._clean_pickle_file(data_node)
            cls._remove_dn_file_path_in_backup_file(data_node)

    @classmethod
    def _delete_many(cls, data_node_ids: Iterable[DataNodeId]):
        data_nodes = []
        for data_node_id in data_node_ids:
            if data_node := cls._get(data_node_id):
                data_nodes.append(data_node)
        super()._delete_many(data_node_ids)
        cls._clean_pickle_files(data_nodes)
        cls._remove_dn_file_paths_in_backup_file(data_nodes)

    @classmethod
    def _delete_all(cls):
        data_nodes = cls._get_all()
        super()._delete_all()
        cls._clean_pickle_files(data_nodes)
        cls._remove_dn_file_paths_in_backup_file(data_nodes)

    @classmethod
    def _delete_by_version(cls, version_number: str):
        data_nodes = cls._get_all(version_number)
        cls._repository._delete_by(attribute="version", value=version_number, version_number="all")
        cls._clean_pickle_files(data_nodes)
        cls._remove_dn_file_paths_in_backup_file(data_nodes)
        _publish_event(cls._EVENT_ENTITY_TYPE, None, EventOperation.DELETION, None)
