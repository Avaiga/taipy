import logging
from typing import Dict, List, Set, Iterable

from taipy.data import DataSource
from taipy.data.data_source_config import DataSourceConfig
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.exceptions.scenario import NonExistingScenarioConfig, NonExistingScenario
from taipy.pipeline import PipelineManager
from taipy.pipeline.pipeline_model import PipelineId
from taipy.scenario import Scenario, ScenarioConfig, ScenarioId
from taipy.scenario.scenario_model import ScenarioModel


class ScenarioManager:
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager

    __SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
    __SCENARIO_CONFIG_DB: Dict[str, ScenarioConfig] = {}

    def delete_all(self):
        self.__SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
        self.__SCENARIO_CONFIG_DB: Dict[str, ScenarioConfig] = {}

    def register(self, scenario_config: ScenarioConfig):
        [self.pipeline_manager.register(pipeline) for pipeline in scenario_config.pipelines]
        self.__SCENARIO_CONFIG_DB[scenario_config.name] = scenario_config

    def get_scenario_config(self, config_name: str) -> ScenarioConfig:
        try:
            return self.__SCENARIO_CONFIG_DB[config_name]
        except KeyError:
            logging.error(f"Scenario : {config_name} does not exist.")
            raise NonExistingScenarioConfig(config_name)

    def get_scenario_configs(self) -> Iterable[ScenarioConfig]:
        return self.__SCENARIO_CONFIG_DB.values()

    def create(self,
               scenario_config: ScenarioConfig,
               data_sources: Dict[DataSourceConfig, DataSource] = None
               ) -> Scenario:
        if data_sources is None:
            all_ds_configs: Set[DataSourceConfig] = set()
            for pipeline_configs in scenario_config.pipelines:
                for task_config in pipeline_configs.tasks:
                    for ds_config in task_config.input:
                        all_ds_configs.add(ds_config)
                    for ds_config in task_config.output:
                        all_ds_configs.add(ds_config)
            data_sources = {ds_config: self.data_manager.create_data_source(ds_config) for ds_config in all_ds_configs}
        pipelines = [self.pipeline_manager.create(p_config, data_sources) for p_config in scenario_config.pipelines]
        scenario = Scenario(scenario_config.name, pipelines, scenario_config.properties)
        self.save(scenario)
        return scenario

    def save(self, scenario: Scenario):
        self.__SCENARIO_MODEL_DB[scenario.id] = scenario.to_model()

    def get_scenario(self, scenario_id: ScenarioId) -> Scenario:
        try:
            model = self.__SCENARIO_MODEL_DB[scenario_id]
            pipelines = [self.pipeline_manager.get_pipeline(PipelineId(pipeline_id)) for pipeline_id in model.pipelines]
            return Scenario(model.name, pipelines, model.properties, model.id)
        except NonExistingPipeline as err:
            logging.error(err.message)
            raise err
        except KeyError:
            logging.error(f"Scenario entity : {scenario_id} does not exist.")
            raise NonExistingScenario(scenario_id)

    def get_scenarios(self) -> Iterable[Scenario]:
        return [self.get_scenario(model.id) for model in self.__SCENARIO_MODEL_DB.values()]

    def submit(self, scenario_id: ScenarioId):
        scenario_to_submit = self.get_scenario(scenario_id)
        for pipeline in scenario_to_submit.pipelines.values():
            self.pipeline_manager.submit(pipeline.id)
