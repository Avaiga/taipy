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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Column, Enum, Float, String, Table, UniqueConstraint

from taipy.config.common.scope import Scope

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry
from .data_node_id import Edit


@mapper_registry.mapped
@dataclass
class _DataNodeModel(_BaseModel):
    __table__ = Table(
        "data_node",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("config_id", String),
        Column("scope", Enum(Scope)),
        Column("storage_type", String),
        Column("name", String),
        Column("owner_id", String),
        Column("parent_ids", JSON),
        Column("last_edit_date", String),
        Column("edits", JSON),
        Column("version", String),
        Column("validity_days", Float),
        Column("validity_seconds", Float),
        Column("edit_in_progress", Boolean),
        Column("editor_id", String),
        Column("editor_expiration_date", String),
        Column("data_node_properties", JSON),
    )
    __table_args__ = (UniqueConstraint("config_id", "owner_id", name="_config_owner_uc"),)

    id: str
    config_id: str
    scope: Scope
    storage_type: str
    name: Optional[str]
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
        dn_properties = data["data_node_properties"]
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data.get("name"),
            owner_id=data.get("owner_id"),
            parent_ids=data.get("parent_ids", []),
            last_edit_date=data.get("last_edit_date"),
            edits=data["edits"],
            version=data["version"],
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            edit_in_progress=bool(data.get("edit_in_progress", False)),
            editor_id=data.get("editor_id", None),
            editor_expiration_date=data.get("editor_expiration_date"),
            data_node_properties=dn_properties,
        )
