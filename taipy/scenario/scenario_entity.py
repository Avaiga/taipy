""" Generic pipeline.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import logging
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
        self.name = self.__protect_name(name)
        self.id: ScenarioId = scenario_id or ScenarioId(
            self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.pipeline_entities = {p.name: p for p in pipeline_entities}
        self.properties = properties

    @staticmethod
    def __protect_name(name):
        return name.strip().lower().replace(' ', '_')

    def __getattr__(self, attribute_name):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        if protected_attribute_name in self.pipeline_entities:
            return self.pipeline_entities[protected_attribute_name]
        for pipeline in self.pipeline_entities.values():
            if protected_attribute_name in pipeline.task_entities:
                return pipeline.task_entities[protected_attribute_name]
            for task in pipeline.task_entities.values():
                if protected_attribute_name in task.input:
                    return task.input[protected_attribute_name]
                if protected_attribute_name in task.output:
                    return task.output[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of scenario {self.id}")
        raise AttributeError

    def to_model(self) -> ScenarioModel:
        return ScenarioModel(
            self.id,
            self.name,
            [entity.id for entity in self.pipeline_entities.values()],
            self.properties,
        )
