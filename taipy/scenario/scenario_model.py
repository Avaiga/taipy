from dataclasses import dataclass
from typing import List, NewType

from taipy.pipeline import PipelineId

ScenarioId = NewType("ScenarioId", str)


@dataclass
class ScenarioModel:
    id: ScenarioId
    name: str
    pipelines: List[PipelineId]
    properties: dict
