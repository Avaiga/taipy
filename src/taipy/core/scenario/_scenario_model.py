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
from datetime import datetime
from typing import Any, Dict, List, Optional

from .._version._utils import _version_migration
from ..common import _utils
from ..common._utils import _Subscriber
from ..common.alias import CycleId, PipelineId, ScenarioId
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle
from ..pipeline.pipeline import Pipeline
from ..scenario.scenario import Scenario


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

    @classmethod
    def _from_entity(cls, scenario: Scenario):
        return _ScenarioModel(
            id=scenario.id,
            config_id=scenario.config_id,
            pipelines=[p.id if isinstance(p, Pipeline) else p for p in scenario._pipelines],
            properties=scenario._properties.data,
            creation_date=scenario._creation_date.isoformat(),
            primary_scenario=scenario._primary_scenario,
            subscribers=_utils._fcts_to_dict(scenario._subscribers),
            tags=list(scenario._tags),
            version=scenario.version,
            cycle=scenario._cycle.id if scenario._cycle else None,
        )

    def _to_entity(self) -> Scenario:
        scenario = Scenario(
            scenario_id=self.id,
            config_id=self.config_id,
            pipelines=self.pipelines,  # type: ignore
            properties=self.properties,
            creation_date=datetime.fromisoformat(self.creation_date),
            is_primary=self.primary_scenario,
            tags=set(self.tags),
            cycle=self.__to_cycle(self.cycle),
            subscribers=[
                _Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                for it in self.subscribers
            ],
            version=self.version,
        )
        return scenario

    @staticmethod
    def __to_cycle(cycle_id: CycleId = None) -> Optional[Cycle]:
        return _CycleManagerFactory._build_manager()._get(cycle_id) if cycle_id else None
