# Copyright 2022 Avaiga Private Limited
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

from taipy.config.common.scope import Scope

from ..common.alias import JobId


@dataclass
class _DataNodeModel:

    id: str
    config_id: str
    scope: Scope
    storage_type: str
    name: str
    parent_id: Optional[str]
    last_edit_date: Optional[str]
    job_ids: List[JobId]
    validity_days: Optional[float]
    validity_seconds: Optional[float]
    edit_in_progress: bool
    data_node_properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "scope": repr(self.scope)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data["name"],
            parent_id=data["parent_id"],
            last_edit_date=data.get("last_edit_date", data.get("last_edition_date")),
            job_ids=data["job_ids"],
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            edit_in_progress=bool(data.get("edit_in_progress", data.get("edition_in_progress", False))),
            data_node_properties=data["data_node_properties"],
        )
