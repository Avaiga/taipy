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
from typing import Any, Dict

from sqlalchemy import Boolean, Column, String, Table

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry


@mapper_registry.mapped
@dataclass
class _VersionModel(_BaseModel):
    __table__ = Table(
        "version",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("config", String),  # config is store as a json string
        Column("creation_date", String),
        Column("is_production", Boolean),
        Column("is_development", Boolean),
        Column("is_latest", Boolean),
    )
    id: str
    config: Dict[str, Any]
    creation_date: str

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _VersionModel(
            id=data["id"],
            config=data["config"],
            creation_date=data["creation_date"],
        )
