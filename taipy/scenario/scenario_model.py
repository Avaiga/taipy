from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from taipy.common.alias import PipelineId, ScenarioId


@dataclass_json
@dataclass
class ScenarioModel:
    id: ScenarioId
    name: str
    pipelines: List[PipelineId]
    properties: dict
