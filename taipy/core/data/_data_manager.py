# Copyright 2021-2025 Avaiga Private Limited
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
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from taipy.common.config import Config
from taipy.common.config._config import _Config
from taipy.core.job.job_id import JobId

from .._manager._manager import _Manager
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_mixin import _VersionMixin
from ..common.scope import Scope
from ..config.data_node_config import DataNodeConfig
from ..cycle.cycle_id import CycleId
from ..exceptions.exceptions import InvalidDataNodeType, NoData
from ..notification import Event, EventEntityType, EventOperation, Notifier, _make_event
from ..reason import EntityDoesNotExist, NotGlobalScope, ReasonCollection, WrongConfigType
from ..reason.reason import DataIsNotDuplicable
from ..scenario.scenario_id import ScenarioId
from ..sequence.sequence_id import SequenceId
from ._data_duplicator import _DataDuplicator
from ._file_datanode_mixin import _FileDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId


class _DataManager(_Manager[DataNode], _VersionMixin):
    _DATA_NODE_CLASS_MAP = DataNode._class_map()  # type: ignore
    _ENTITY_NAME = DataNode.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.DATA_NODE
    _repository: _AbstractRepository

    @classmethod
    def _get_owner_id(
        cls, scope, cycle_id, scenario_id
    ) -> Union[Optional[SequenceId], Optional[ScenarioId], Optional[CycleId]]:
        if scope == Scope.SCENARIO:
            return scenario_id
        elif scope == Scope.CYCLE:
            return cycle_id
        else:
            return None

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
            owner_id = cls._get_owner_id(dn_config.scope, cycle_id, scenario_id)
            dn_configs_and_owner_id.append((dn_config, owner_id))
        data_nodes = cls._repository._get_by_configs_and_owner_ids(
            dn_configs_and_owner_id, cls._build_filters_with_version(None)
        )
        return {
            dn_config: data_nodes.get((dn_config, owner_id)) or cls._create(dn_config, owner_id, None)
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
    def _create(
        cls, data_node_config: DataNodeConfig, owner_id: Optional[str], parent_ids: Optional[Set[str]]
    ) -> DataNode:
        data_node = cls.__instantiate(data_node_config, owner_id, parent_ids)
        cls._repository._save(data_node)
        Notifier.publish(_make_event(data_node, EventOperation.CREATION))
        return data_node

    @classmethod
    def __instantiate(
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
    def _read(cls, data_node: DataNode) -> Any:
        """Read the data referenced by this data node.

        Returns:
            The data referenced by this data node.

        Raises:
            NoData^: If the data has not been written yet.
        """
        if not data_node.last_edit_date:
            raise NoData(f"Data node {data_node.id} from config {data_node.config_id} has not been written yet.")

        return data_node._read()

    @classmethod
    def _append(
        cls, data_node: DataNode, data, editor_id: Optional[str] = None, comment: Optional[str] = None, **kwargs: Any
    ):
        data_node._append(data)
        data_node.track_edit(editor_id=editor_id, comment=comment, **kwargs)
        data_node.unlock_edit()
        cls._update(data_node)

    @classmethod
    def _write(
        cls,
        data_node: DataNode,
        data,
        job_id: Optional[JobId] = None,
        editor_id: Optional[str] = None,
        comment: Optional[str] = None,
        **kwargs: Any,
    ):
        data_node._write(data)
        data_node.track_edit(job_id=job_id, editor_id=editor_id, comment=comment, **kwargs)
        data_node.unlock_edit()
        cls._update(data_node)

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
        Get all data nodes by its config id.
        """
        filters = cls._build_filters_with_version(version_number)
        if not filters:
            filters = [{}]
        for fil in filters:
            fil.update({"config_id": config_id})
        return cls._repository._load_all(filters)

    @classmethod
    def _can_duplicate(cls, dn: Union[DataNodeId, DataNode]) -> ReasonCollection:
        if isinstance(dn, DataNode):
            dn_id = dn.id
        else:
            dn_id = dn
        reason_collector = ReasonCollection()
        if not cls._repository._exists(dn_id):
            reason_collector._add_reason(dn_id, EntityDoesNotExist(dn_id))
            return reason_collector
        if not isinstance(dn, DataNode):
            dn = cls._get(dn)
        if not _DataDuplicator(dn).can_duplicate():
            reason_collector._add_reason(dn_id, DataIsNotDuplicable(dn_id))
        return reason_collector
