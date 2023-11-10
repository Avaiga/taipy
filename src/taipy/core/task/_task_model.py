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

from sqlalchemy import JSON, Boolean, Column, String, Table

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry


@mapper_registry.mapped
@dataclass
class _TaskModel(_BaseModel):
    __table__ = Table(
        "task",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("owner_id", String),
        Column("parent_ids", JSON),
        Column("config_id", String),
        Column("input_ids", JSON),
        Column("function_name", String),
        Column("function_module", String),
        Column("output_ids", JSON),
        Column("version", String),
        Column("skippable", Boolean),
        Column("properties", JSON),
    )
    id: str
    owner_id: Optional[str]
    parent_ids: List[str]
    config_id: str
    input_ids: List[str]
    function_name: str
    function_module: str
    output_ids: List[str]
    version: str
    skippable: bool
    properties: Dict[str, Any]

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _TaskModel(
            id=data["id"],
            owner_id=data.get("owner_id"),
            parent_ids=_BaseModel._deserialize_attribute(data.get("parent_ids", [])),
            config_id=data["config_id"],
            input_ids=_BaseModel._deserialize_attribute(data["input_ids"]),
            function_name=data["function_name"],
            function_module=data["function_module"],
            output_ids=_BaseModel._deserialize_attribute(data["output_ids"]),
            version=data["version"],
            skippable=data["skippable"],
            properties=_BaseModel._deserialize_attribute(data["properties"] if "properties" in data.keys() else {}),
        )

    @staticmethod
    def to_list(model):
        return [
            model.id,
            model.owner_id,
            _BaseModel._serialize_attribute(model.parent_ids),
            model.config_id,
            _BaseModel._serialize_attribute(model.input_ids),
            model.function_name,
            model.function_module,
            _BaseModel._serialize_attribute(model.output_ids),
            model.version,
            model.skippable,
            _BaseModel._serialize_attribute(model.properties),
        ]
