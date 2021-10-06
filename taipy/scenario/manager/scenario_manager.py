import logging
from typing import Dict, List, Set

from taipy.data import DataSource
from taipy.data.data_source_config import DataSourceConfig
from taipy.exceptions.pipeline import NonExistingPipelineEntity
from taipy.exceptions.scenario import (
    NonExistingScenario,
    NonExistingScenarioEntity,
)
from taipy.pipeline import PipelineManager
from taipy.pipeline.pipeline_model import PipelineId
from taipy.scenario import ScenarioConfig, Scenario, ScenarioId
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioManager:
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager

    __SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
    __SCENARIOS: Dict[str, ScenarioConfig] = {}

    def delete_all(self):
        self.__SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
        self.__SCENARIOS: Dict[str, ScenarioConfig] = {}

    def register_scenario(self, scenario: ScenarioConfig):
        [
            self.pipeline_manager.register_pipeline(pipeline)
            for pipeline in scenario.pipelines
        ]
        self.__SCENARIOS[scenario.name] = scenario

    def get_scenario(self, name: str) -> ScenarioConfig:
        try:
            return self.__SCENARIOS[name]
        except KeyError:
            logging.error(f"Scenario : {name} does not exist.")
            raise NonExistingScenario(name)

    def get_scenarios(self) -> List[ScenarioConfig]:
        return [
            self.get_scenario(scenario.name) for scenario in self.__SCENARIOS.values()
        ]

    def create_scenario_entity(
        self, scenario: ScenarioConfig, ds_entities: Dict[DataSourceConfig, DataSource] = None
    ) -> Scenario:
        if ds_entities is None:
            all_ds: Set[DataSourceConfig] = set()
            for pipeline in scenario.pipelines:
                for task in pipeline.tasks:
                    for ds in task.input:
                        all_ds.add(ds)
                    for ds in task.output:
                        all_ds.add(ds)
            ds_entities = {
                data_source: self.data_manager.create_data_source_entity(data_source)
                for data_source in all_ds
            }
        p_entities = [
            self.pipeline_manager.create_pipeline_entity(pipeline, ds_entities)
            for pipeline in scenario.pipelines
        ]
        scenario_entity = Scenario(scenario.name, p_entities, scenario.properties)
        self.save_scenario_entity(scenario_entity)
        return scenario_entity

    def save_scenario_entity(self, scenario_entity: Scenario):
        self.__SCENARIO_MODEL_DB[scenario_entity.id] = scenario_entity.to_model()

    def get_scenario_entity(self, scenario_id: ScenarioId) -> Scenario:
        try:
            model = self.__SCENARIO_MODEL_DB[scenario_id]
            pipeline_entities = [
                self.pipeline_manager.get_pipeline_entity(PipelineId(pipeline_id))
                for pipeline_id in model.pipelines
            ]
            return Scenario(
                model.name, pipeline_entities, model.properties, model.id
            )
        except NonExistingPipelineEntity as err:
            logging.error(err.message)
            raise err
        except KeyError:
            logging.error(f"Scenario entity : {scenario_id} does not exist.")
            raise NonExistingScenarioEntity(scenario_id)

    def get_scenario_entities(self) -> List[Scenario]:
        return [
            self.get_scenario_entity(model.id)
            for model in self.__SCENARIO_MODEL_DB.values()
        ]

    def submit(self, scenario_id: ScenarioId):
        scenario_entity_to_submit = self.get_scenario_entity(scenario_id)
        for pipeline in scenario_entity_to_submit.pipeline_entities.values():
            self.pipeline_manager.submit(pipeline.id)
