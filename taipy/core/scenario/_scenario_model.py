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
from ..cycle.cycle_id import CycleId
from ..data.data_node_id import DataNodeId
from ..task.task_id import TaskId
from .scenario_id import ScenarioId


@dataclass
class _ScenarioModel(_BaseModel):
    id: ScenarioId
    config_id: str
    tasks: List[TaskId]
    additional_data_nodes: List[DataNodeId]
    properties: Dict[str, Any]
    creation_date: str
    primary_scenario: bool
    subscribers: List[Dict]
    tags: List[str]
    version: str
    sequences: Optional[Dict[str, Dict]] = None
    cycle: Optional[CycleId] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _ScenarioModel(
            id=data["id"],
            config_id=data["config_id"],
            tasks=_BaseModel._deserialize_attribute(data["tasks"]),
            additional_data_nodes=_BaseModel._deserialize_attribute(data["additional_data_nodes"]),
            properties=_BaseModel._deserialize_attribute(data["properties"]),
            creation_date=data["creation_date"],
            primary_scenario=data["primary_scenario"],
            subscribers=_BaseModel._deserialize_attribute(data["subscribers"]),
            tags=_BaseModel._deserialize_attribute(data["tags"]),
            version=data["version"],
            sequences=_BaseModel._deserialize_attribute(data["sequences"]),
            cycle=CycleId(data["cycle"]) if "cycle" in data else None,
        )

    def to_list(self):
        return [
            self.id,
            self.config_id,
            _BaseModel._serialize_attribute(self.tasks),
            _BaseModel._serialize_attribute(self.additional_data_nodes),
            _BaseModel._serialize_attribute(self.properties),
            self.creation_date,
            self.primary_scenario,
            _BaseModel._serialize_attribute(self.subscribers),
            _BaseModel._serialize_attribute(self.tags),
            self.version,
            _BaseModel._serialize_attribute(self.sequences),
            self.cycle,
        ]
