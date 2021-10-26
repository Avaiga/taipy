import logging
from functools import partial
from typing import Callable, Dict, List, Set

from taipy.common.alias import PipelineId, ScenarioId
from taipy.config import ScenarioConfig
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.exceptions.scenario import NonExistingScenario
from taipy.pipeline import PipelineManager
from taipy.scenario import Scenario
from taipy.scenario.scenario_model import ScenarioModel
from taipy.task import Job


class ScenarioManager:
    pipeline_manager = PipelineManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager

    __status_notifier: Set[Callable] = set()
    __SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}
    __SCENARIO_CONFIG_DB: Dict[str, ScenarioConfig] = {}

    def subscribe(self, callback: Callable[[Scenario, Job], None]):
        """
        Subscribe a function to be called when the status of a Job changes

        Note:
            - Notification will be available only for Jobs created after this subscription
        """
        self.__status_notifier.add(callback)

    def unsubscribe(self, callback: Callable[[Scenario, Job], None]):
        """
        Unsubscribe a function called when the status of a Job changes

        Note:
            - The function will continue to be called for ongoing Jobs
        """
        self.__status_notifier.remove(callback)

    def delete_all(self):
        self.__SCENARIO_MODEL_DB: Dict[ScenarioId, ScenarioModel] = {}

    def create(self, config: ScenarioConfig) -> Scenario:
        scenario_id = Scenario.new_id(config.name)
        pipelines = [self.pipeline_manager.create(p_config, scenario_id) for p_config in config.pipelines]
        scenario = Scenario(config.name, pipelines, config.properties, scenario_id)
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

    def get_scenarios(self) -> List[Scenario]:
        return [self.get_scenario(model.id) for model in self.__SCENARIO_MODEL_DB.values()]

    def submit(self, scenario_id: ScenarioId):
        scenario_to_submit = self.get_scenario(scenario_id)
        callbacks = self.__get_status_notifier_callbacks(scenario_to_submit)
        for pipeline in scenario_to_submit.pipelines.values():
            self.pipeline_manager.submit(pipeline.id, callbacks)

    def __get_status_notifier_callbacks(self, scenario: Scenario) -> List:
        if self.__status_notifier:
            return [partial(c, scenario) for c in self.__status_notifier]
        return []
