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

from .._repository._base_taipy_model import _BaseModel


@dataclass
class _TaskModel(_BaseModel):
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

    def to_list(self):
        return [
            self.id,
            self.owner_id,
            _BaseModel._serialize_attribute(self.parent_ids),
            self.config_id,
            _BaseModel._serialize_attribute(self.input_ids),
            self.function_name,
            self.function_module,
            _BaseModel._serialize_attribute(self.output_ids),
            self.version,
            self.skippable,
            _BaseModel._serialize_attribute(self.properties),
        ]
