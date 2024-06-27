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

from typing import Optional

from ..data.data_node import DataNodeId


class Reason:
    """
    TODO - NOT DOCUMENTED
    """
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason

    def __repr__(self):
        return self.reason


class _DataNodeReasonMixin:
    def __init__(self, datanode_id: DataNodeId):
        self.datanode_id = datanode_id

    @property
    def datanode(self):
        from ..data._data_manager_factory import _DataManagerFactory
        return _DataManagerFactory._build_manager()._get(self.datanode_id)


class DataNodeEditInProgress(Reason, _DataNodeReasonMixin):
    """
    TODO - NOT DOCUMENTED
    """
    def __init__(self, datanode_id: DataNodeId):
        Reason.__init__(self, f"DataNode {datanode_id} is being edited")
        _DataNodeReasonMixin.__init__(self, datanode_id)


class DataNodeIsNotWritten(Reason, _DataNodeReasonMixin):
    """
    TODO - NOT DOCUMENTED
    """
    def __init__(self, datanode_id: DataNodeId):
        Reason.__init__(self, f"DataNode {datanode_id} is not written")
        _DataNodeReasonMixin.__init__(self, datanode_id)


def _build_data_node_is_being_edited_reason(dn_id: DataNodeId) -> str:
    return f"DataNode {dn_id} is not written"


def _build_data_node_is_not_written(dn_id: DataNodeId) -> str:
    return f"DataNode {dn_id} is not written"


def _build_not_submittable_entity_reason(entity_id: str) -> str:
    return f"Entity {entity_id} is not a submittable entity"


def _build_wrong_config_type_reason(config_id: str, config_type: Optional[str]) -> str:
    if config_type:
        return f'Object "{config_id}" must be a valid {config_type}'

    return f'Object "{config_id}" is not a valid config to be created'


def _build_not_global_scope_reason(config_id: str) -> str:
    return f'Data node config "{config_id}" does not have GLOBAL scope'
