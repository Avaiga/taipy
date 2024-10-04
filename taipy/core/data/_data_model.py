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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.common.config.common.scope import Scope

from .._repository._base_taipy_model import _BaseModel
from .data_node_id import Edit


@dataclass
class _DataNodeModel(_BaseModel):
    id: str
    config_id: str
    scope: Scope
    storage_type: str
    owner_id: Optional[str]
    parent_ids: List[str]
    last_edit_date: Optional[str]
    edits: List[Edit]
    version: str
    validity_days: Optional[float]
    validity_seconds: Optional[float]
    edit_in_progress: bool
    editor_id: Optional[str]
    editor_expiration_date: Optional[str]
    data_node_properties: Dict[str, Any]

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
            storage_type=data["storage_type"],
            owner_id=data.get("owner_id"),
            parent_ids=_BaseModel._deserialize_attribute(data.get("parent_ids", [])),
            last_edit_date=data.get("last_edit_date"),
            edits=_BaseModel._deserialize_attribute(data["edits"]),
            version=data["version"],
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            edit_in_progress=bool(data.get("edit_in_progress", False)),
            editor_id=data.get("editor_id", None),
            editor_expiration_date=data.get("editor_expiration_date"),
            data_node_properties=_BaseModel._deserialize_attribute(data["data_node_properties"]),
        )

    def to_list(self):
        return [
            self.id,
            self.config_id,
            repr(self.scope),
            self.storage_type,
            self.owner_id,
            _BaseModel._serialize_attribute(self.parent_ids),
            self.last_edit_date,
            _BaseModel._serialize_attribute(self.edits),
            self.version,
            self.validity_days,
            self.validity_seconds,
            self.edit_in_progress,
            self.editor_id,
            self.editor_expiration_date,
            _BaseModel._serialize_attribute(self.data_node_properties),
        ]
