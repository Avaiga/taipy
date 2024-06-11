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

from ..data.data_node import DataNodeId


def _build_data_node_is_being_edited_reason(dn_id: DataNodeId) -> str:
    return f"DataNode {dn_id} is being edited"


def _build_data_node_is_not_written(dn_id: DataNodeId) -> str:
    return f"DataNode {dn_id} is not written"


def _build_not_submittable_entity_reason(entity_id: str) -> str:
    return f"Entity {entity_id} is not a submittable entity"


def _build_config_can_not_create_reason(config_id: str) -> str:
    return f'Object "{config_id}" is not a valid config to be created'


def _build_not_global_datanode_config_reason(config_id: str) -> str:
    return f'Data node config "{config_id}" does not have GLOBAL scope'
