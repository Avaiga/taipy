from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from taipy.common.alias import CycleId, PipelineId, ScenarioId


@dataclass_json
@dataclass
class ScenarioModel:
    id: ScenarioId
    name: str
    pipelines: List[PipelineId]
    properties: dict
    master_scenario: bool
    cycle: Optional[CycleId] = None
