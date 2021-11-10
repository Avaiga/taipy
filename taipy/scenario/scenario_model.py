from dataclasses import dataclass
from typing import List, Optional

from taipy.common.alias import CycleId, PipelineId, ScenarioId


@dataclass
class ScenarioModel:
    id: ScenarioId
    name: str
    pipelines: List[PipelineId]
    properties: dict
    cycle: Optional[CycleId] = None
