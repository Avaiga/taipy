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
from ..cycle.cycle_id import CycleId
from ..data.data_node_id import DataNodeId
from ..task.task_id import TaskId
from .scenario_id import ScenarioId


@mapper_registry.mapped
@dataclass
class _ScenarioModel(_BaseModel):
    __table__ = Table(
        "scenario",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("config_id", String),
        Column("tasks", JSON),
        Column("additional_data_nodes", JSON),
        Column("properties", JSON),
        Column("creation_date", String),
        Column("primary_scenario", Boolean),
        Column("subscribers", JSON),
        Column("tags", JSON),
        Column("version", String),
        Column("sequences", JSON),
        Column("cycle", String),
    )
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
            tasks=data.get("tasks", None),
            additional_data_nodes=data.get("additional_data_nodes", None),
            properties=data["properties"],
            creation_date=data["creation_date"],
            primary_scenario=data["primary_scenario"],
            subscribers=data["subscribers"],
            tags=data["tags"],
            version=data["version"],
            sequences=data.get("sequences", None),
            cycle=CycleId(data["cycle"]) if "cycle" in data else None,
        )
