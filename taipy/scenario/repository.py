from taipy.common.alias import ScenarioId
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.manager.pipeline_manager import PipelineManager
from taipy.repository import FileSystemRepository
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioRepository(FileSystemRepository[ScenarioModel, Scenario]):
    def __init__(self, dir_name="scenario"):
        super().__init__(model=ScenarioModel, dir_name=dir_name)

    def to_model(self, scenario: Scenario):
        return ScenarioModel(
            id=scenario.id,
            name=scenario.config_name,
            pipelines=[pipeline.id for pipeline in scenario.pipelines.values()],
            properties=scenario.properties,
        )

    def from_model(self, model: ScenarioModel) -> Scenario:
        return Scenario(
            scenario_id=model.id,
            config_name=model.name,
            pipelines=self.__to_pipelines(model.pipelines),
            properties=model.properties,
        )

    def __to_pipelines(self, pipeline_ids):
        return [PipelineManager().get(i) for i in pipeline_ids]
