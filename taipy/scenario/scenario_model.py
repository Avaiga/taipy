from dataclasses import dataclass
from typing import List

from taipy.common.alias import PipelineId, ScenarioId


@dataclass
class ScenarioModel:
    id: ScenarioId
    name: str
    pipelines: List[PipelineId]
    properties: dict
