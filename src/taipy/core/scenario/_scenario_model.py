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

from .._version._utils import _version_migration
from ..common.alias import CycleId, PipelineId, ScenarioId


@dataclass
class _ScenarioModel:
    id: ScenarioId
    config_id: str
    pipelines: List[PipelineId]
    properties: Dict[str, Any]
    creation_date: str
    primary_scenario: bool
    subscribers: List[Dict]
    tags: List[str]
    version: str
    cycle: Optional[CycleId] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _ScenarioModel(
            id=data["id"],
            config_id=data["config_id"],
            pipelines=data["pipelines"],
            properties=data["properties"],
            creation_date=data["creation_date"],
            primary_scenario=data["primary_scenario"],
            subscribers=data["subscribers"],
            tags=data["tags"],
            version=data["version"] if "version" in data.keys() else _version_migration(),
            cycle=CycleId(data["cycle"]) if "cycle" in data else None,
        )
