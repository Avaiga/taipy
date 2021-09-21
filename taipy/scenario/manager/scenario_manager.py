import logging
from typing import Dict, List

from taipy.data import DataSourceEntity
from taipy.data.data_source import DataSource
from taipy.exceptions.pipeline import NonExistingPipelineEntity
from taipy.exceptions.scenario import NonExistingScenario, NonExistingScenarioEntity
from taipy.pipeline import PipelineManager
from taipy.pipeline.pipeline_model import PipelineId
from taipy.scenario import ScenarioId, Scenario, ScenarioEntity
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioManager:
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager

    __SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
    __SCENARIOS: Dict[str, Scenario] = {}

    def delete_all(self):
        self.__SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
        self.__SCENARIOS: Dict[str, Scenario] = {}

    def register_scenario(self, scenario: Scenario):
        [self.pipeline_manager.register_pipeline(pipeline) for pipeline in scenario.pipelines]
        self.__SCENARIOS[scenario.name] = scenario

    def get_scenario(self, name: str) -> Scenario:
        try:
            return self.__SCENARIOS[name]
        except KeyError:
            logging.error(f"Scenario : {name} does not exist.")
            raise NonExistingScenario(name)

    def get_scenarios(self) -> List[Scenario]:
        return [
            self.get_scenario(scenario.name)
            for scenario in self.__SCENARIOS.values()
        ]

    def create_scenario_entity(self, scenario: Scenario, ds_entities: Dict[DataSource, DataSourceEntity] = None) -> ScenarioEntity:
        if ds_entities is None:
            all_ds: set[DataSource] = set()
            for pipeline in scenario.pipelines:
                for task in pipeline.tasks:
                        all_ds.extend(task.input)
                        all_ds.extend(task.output)
            ds_entities = {data_source: self.data_manager.create_data_source_entity(data_source) for data_source in all_ds}
        p_entities = [self.pipeline_manager.create_pipeline_entity(pipeline, ds_entities) for pipeline in scenario.pipelines]
        scenario_entity = ScenarioEntity(scenario.name, p_entities, scenario.properties)
        self.save_scenario_entity(scenario_entity)
        return scenario_entity

    def save_scenario_entity(self, scenario_entity: ScenarioEntity):
        self.__SCENARIO_MODEL_DB[scenario_entity.id] = scenario_entity.to_model()

    def get_scenario_entity(self, scenario_id: ScenarioId) -> ScenarioEntity:
        try:
            model = self.__SCENARIO_MODEL_DB[scenario_id]
            pipeline_entities = [
                self.pipeline_manager.get_pipeline_entity(PipelineId(pipeline_id))
                for pipeline_id in model.pipelines
            ]
            return ScenarioEntity(model.name, pipeline_entities, model.properties, model.id)
        except NonExistingPipelineEntity as err:
            logging.error(
                f"Pipeline entity : {err.pipeline_id} from scenario entity {scenario_id} does not exist."
            )
            raise err
        except KeyError:
            logging.error(f"Scenario entity : {scenario_id} does not exist.")
            raise NonExistingScenarioEntity(scenario_id)

    def get_scenario_entities(self) -> List[ScenarioEntity]:
        return [
            self.get_scenario_entity(model.id)
            for model in self.__SCENARIO_MODEL_DB.values()
        ]

    def submit(self, scenario_id: ScenarioId):
        scenario_entity_to_submit = self.get_scenario_entity(scenario_id)
        for pipeline in scenario_entity_to_submit.pipeline_entities:
            self.pipeline_manager.submit(pipeline.id)
