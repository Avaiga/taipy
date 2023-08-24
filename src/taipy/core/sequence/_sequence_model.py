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

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, String, Table

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry
from .._version._utils import _version_migration
from ..task.task_id import TaskId
from .sequence_id import SequenceId


@mapper_registry.mapped
@dataclass
class _SequenceModel(_BaseModel):
    __table__ = Table(
        "sequence",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("owner_id", String),
        Column("parent_ids", JSON),
        Column("properties", JSON),
        Column("tasks", JSON),
        Column("subscribers", JSON),
        Column("version", String),
    )
    id: SequenceId
    owner_id: Optional[str]
    parent_ids: List[str]
    properties: Dict[str, Any]
    tasks: List[TaskId]
    subscribers: List[Dict]
    version: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _SequenceModel(
            id=data["id"],
            # Migrate parent_id attribute for compatibility between <=2.0 to >=2.1 versions.
            owner_id=data.get("owner_id", data.get("parent_id")),
            parent_ids=data.get("parent_ids", []),
            properties=data["properties"],
            tasks=data["tasks"],
            subscribers=data["subscribers"],
            version=data["version"] if "version" in data.keys() else _version_migration(),
        )
