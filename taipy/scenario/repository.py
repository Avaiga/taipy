from typing import List

from taipy.common.alias import PipelineId, ScenarioId
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.manager.pipeline_manager import PipelineManager
from taipy.pipeline.pipeline import Pipeline
from taipy.repository import FileSystemRepository
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioRepository(FileSystemRepository[ScenarioModel, Scenario]):
    def __init__(self, dir_name="scenarios"):
        super().__init__(model=ScenarioModel, dir_name=dir_name)

    def to_model(self, scenario: Scenario):
        return ScenarioModel(
            id=scenario.id,
            name=scenario.config_name,
            pipelines=self.__to_pipeline_ids(scenario.pipelines.values()),
            properties=scenario.properties,
        )

    def from_model(self, model: ScenarioModel) -> Scenario:
        return Scenario(
            scenario_id=model.id,
            config_name=model.name,
            pipelines=self.__to_pipelines(model.pipelines),
            properties=model.properties,
        )

    @staticmethod
    def __to_pipeline_ids(pipelines) -> List[PipelineId]:
        return [pipeline.id for pipeline in pipelines]

    @staticmethod
    def __to_pipelines(pipeline_ids):
        return [PipelineManager().get(i) for i in pipeline_ids]
