import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import CycleId, PipelineId, ScenarioId


@dataclass
class _ScenarioModel:
    id: ScenarioId
    config_id: str
    pipelines: List[PipelineId]
    properties: Dict[str, Any]
    creation_date: str
    master_scenario: bool
    subscribers: List[Dict]
    tags: List[str]
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
            master_scenario=data["master_scenario"],
            subscribers=data["subscribers"],
            tags=data["tags"],
            cycle=CycleId(data["cycle"]) if "cycle" in data else None,
        )
