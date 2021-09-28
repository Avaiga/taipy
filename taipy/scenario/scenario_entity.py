""" Generic pipeline.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import uuid
from typing import Dict, List

from taipy.pipeline import PipelineEntity
from taipy.scenario.scenario_model import ScenarioId, ScenarioModel


class ScenarioEntity:
    __ID_PREFIX = "SCENARIO"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        pipeline_entities: List[PipelineEntity],
        properties: Dict[str, str],
        scenario_id: ScenarioId = None,
    ):
        self.name = name.strip().lower().replace(' ', '_')
        self.id: ScenarioId = scenario_id or ScenarioId(
            self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.pipeline_entities = pipeline_entities
        self.properties = properties

    def to_model(self) -> ScenarioModel:
        return ScenarioModel(
            self.id,
            self.name,
            [entity.id for entity in self.pipeline_entities],
            self.properties,
        )
