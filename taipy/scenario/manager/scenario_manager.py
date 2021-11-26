import logging
from functools import partial
from typing import Callable, List, Optional, Set

from taipy.common.alias import ScenarioId
from taipy.config import ScenarioConfig
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.exceptions.repository import ModelNotFound
from taipy.exceptions.scenario import DoesNotBelongToACycle, NonExistingScenario
from taipy.pipeline import PipelineManager
from taipy.scenario import Scenario
from taipy.scenario.repository import ScenarioRepository
from taipy.task import Job


class ScenarioManager:
    pipeline_manager = PipelineManager()
    cycle_manager = CycleManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager
    repository = ScenarioRepository(dir_name="scenarios")

    def subscribe(self, callback: Callable[[Scenario, Job], None], scenario: Scenario):
        """
        Subscribes a function to be called when the status of a Job changes.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        scenario.add_subscriber(callback)
        self.set(scenario)

    def unsubscribe(self, callback: Callable[[Scenario, Job], None], scenario: Scenario):
        """
        Unsubscribes a function that is called when the status of a Job changes.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        scenario.remove_subscriber(callback)
        self.set(scenario)

    def delete_all(self):
        self.repository.delete_all()

    def create(self, config: ScenarioConfig, creation_date=None) -> Scenario:
        scenario_id = Scenario.new_id(config.name)
        pipelines = [
            self.pipeline_manager.get_or_create(p_config, scenario_id) for p_config in config.pipelines_configs
        ]
        cycle = self.cycle_manager.get_or_create(config.frequency, creation_date) if config.frequency else None
        scenario = Scenario(config.name, pipelines, config.properties, scenario_id, cycle=cycle)
        self.set(scenario)
        return scenario

    def set(self, scenario: Scenario):
        self.repository.save(scenario)

    def get(self, scenario_id: ScenarioId) -> Scenario:
        try:
            if scenario := self.repository.load(scenario_id):
                return scenario
            raise ModelNotFound
        except ModelNotFound:
            logging.error(f"Scenario entity: {scenario_id} does not exist.")
            raise NonExistingScenario(scenario_id)

    def get_all(self) -> List[Scenario]:
        return self.repository.load_all()

    def submit(self, scenario_id: ScenarioId):
        scenario_to_submit = self.get(scenario_id)
        callbacks = self.__get_status_notifier_callbacks(scenario_to_submit)
        for pipeline in scenario_to_submit.pipelines.values():
            self.pipeline_manager.submit(pipeline.id, callbacks)

    def __get_status_notifier_callbacks(self, scenario: Scenario) -> List:
        return [partial(c, scenario) for c in scenario.subscribers]

    def get_master(self, cycle: Cycle) -> Optional[Scenario]:
        scenarios = self.get_all_scenarios_of_cycle(cycle)
        for scenario in scenarios:
            if scenario.is_master_scenario():
                return scenario
        return None

    def get_all_scenarios_of_cycle(self, cycle: Cycle) -> List[Scenario]:
        scenarios = []
        for scenario in self.get_all():
            if scenario.cycle == cycle:
                scenarios.append(scenario)
        return scenarios

    def get_all_master_scenarios(self) -> List[Scenario]:
        master_scenarios = []
        for scenario in self.get_all():
            if scenario.is_master_scenario():
                master_scenarios.append(scenario)
        return master_scenarios

    def set_master(self, scenario: Scenario):
        if scenario.cycle:
            master_scenario = self.get_master(scenario.cycle)
            if master_scenario:
                master_scenario.master_scenario = False
                self.set(master_scenario)
            scenario.master_scenario = True
            self.set(scenario)
        else:
            raise DoesNotBelongToACycle
