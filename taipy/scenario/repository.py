from typing import List, Optional

from taipy.common import utils
from taipy.common.alias import CycleId, PipelineId
from taipy.config import Config
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager import CycleManager
from taipy.pipeline.manager.pipeline_manager import PipelineManager
from taipy.pipeline.pipeline import Pipeline
from taipy.repository import FileSystemRepository
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioRepository(FileSystemRepository[ScenarioModel, Scenario]):
    def __init__(self, dir_name="scenarios", base_path=Config.global_config().storage_folder):
        super().__init__(model=ScenarioModel, dir_name=dir_name, base_path=base_path)

    def to_model(self, scenario: Scenario):
        return ScenarioModel(
            id=scenario.id,
            name=scenario.config_name,
            pipelines=self.__to_pipeline_ids(scenario.pipelines.values()),
            properties=scenario.properties,
            master_scenario=scenario.master_scenario,
            subscribers=utils.fcts_to_dict(scenario.subscribers),
            cycle=self.__to_cycle_id(scenario.cycle),
        )

    def from_model(self, model: ScenarioModel) -> Scenario:
        scenario = Scenario(
            scenario_id=model.id,
            config_name=model.name,
            pipelines=self.__to_pipelines(model.pipelines),
            properties=model.properties,
            is_master=model.master_scenario,
            cycle=self.__to_cycle(model.cycle),
        )
        scenario.subscribers = {utils.load_fct(it["fct_module"], it["fct_name"]) for it in model.subscribers}
        return scenario

    @staticmethod
    def __to_pipeline_ids(pipelines) -> List[PipelineId]:
        return [pipeline.id for pipeline in pipelines]

    @staticmethod
    def __to_pipelines(pipeline_ids) -> List[Pipeline]:
        return [PipelineManager().get(i) for i in pipeline_ids]

    @staticmethod
    def __to_cycle(cycle_id: CycleId = None) -> Optional[Cycle]:
        return CycleManager().get(cycle_id) if cycle_id else None

    @staticmethod
    def __to_cycle_id(cycle: Cycle = None) -> Optional[CycleId]:
        return cycle.id if cycle else None
