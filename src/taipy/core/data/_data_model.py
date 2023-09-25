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
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from sqlalchemy import JSON, Boolean, Column, Enum, Float, String, Table, UniqueConstraint

from taipy.config.common.scope import Scope

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry
from .._version._utils import _version_migration
from ..common._warnings import _warn_deprecated
from .data_node_id import Edit


def _to_edits_migration(job_ids: Optional[List[str]]) -> List[Edit]:
    """Migrate a list of job IDs to a list of Edits. Used to migrate data model from <=2.0 to >=2.1 version."""
    _warn_deprecated("job_ids", suggest="edits")
    if not job_ids:
        return []
    # We can't guess what is the timestamp corresponding to a modification from its job_id...
    # So let's use the current time...
    timestamp = datetime.now()
    return [cast(Edit, dict(timestamp=timestamp, job_id=job_id)) for job_id in job_ids]


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
        # Migrate cacheable attribute for compatibility between <=2.0 to >=2.1 versions.
        if data.get("cacheable"):
            dn_properties["cacheable"] = True
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data.get("name"),
            # Migrate parent_id attribute for compatibility between <=2.0 to >=2.1 versions.
            owner_id=data.get("owner_id", data.get("parent_id")),
            parent_ids=data.get("parent_ids", []),
            # Migrate last_edition_date attribute for compatibility between <2.0 to >=2.0 versions.
            last_edit_date=data.get("last_edit_date", data.get("last_edition_date")),
            edits=data["edits"] if "edits" in data.keys() else _to_edits_migration(data.get("job_ids")),
            version=data["version"] if "version" in data.keys() else _version_migration(),
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            # Migrate edition_in_progress attribute for compatibility between <2.0 to >=2.0 versions.
            edit_in_progress=bool(data.get("edit_in_progress", data.get("edition_in_progress", False))),
            editor_id=data.get("editor_id", None),
            editor_expiration_date=data.get("editor_expiration_date"),
            data_node_properties=dn_properties,
        )
