import logging
from functools import partial
from typing import Callable, List, Set

from taipy.common.alias import ScenarioId
from taipy.config import ScenarioConfig
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.exceptions.repository import ModelNotFound
from taipy.exceptions.scenario import NonExistingScenario
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

    __status_notifier: Set[Callable] = set()

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
        self.repository.delete_all()

    def create(self, config: ScenarioConfig, creation_date=None) -> Scenario:
        scenario_id = Scenario.new_id(config.name)
        pipelines = [self.pipeline_manager.create(p_config, scenario_id) for p_config in config.pipelines_configs]
        cycle = self.cycle_manager.get_or_create(config.frequency, creation_date) if config.frequency else None
        scenario = Scenario(config.name, pipelines, config.properties, scenario_id, cycle)
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
            logging.error(f"Scenario entity : {scenario_id} does not exist.")
            raise NonExistingScenario(scenario_id)

    def get_all(self) -> List[Scenario]:
        return self.repository.load_all()

    def submit(self, scenario_id: ScenarioId):
        scenario_to_submit = self.get(scenario_id)
        callbacks = self.__get_status_notifier_callbacks(scenario_to_submit)
        for pipeline in scenario_to_submit.pipelines.values():
            self.pipeline_manager.submit(pipeline.id, callbacks)

    def __get_status_notifier_callbacks(self, scenario: Scenario) -> List:
        if self.__status_notifier:
            return [partial(c, scenario) for c in self.__status_notifier]
        return []

    def get_all_scenarios_of_cycle(self, cycle):
        scenarios = []
        for scenario in self.get_all():
            if scenario.cycle == cycle:
                scenarios.append(scenario)
        return scenarios

    def get_all_master_scenarios(self):
        master_scenarios = []
        for scenario in self.get_all():
            if scenario.is_master_scenario():
                master_scenarios.append(scenario)
        return master_scenarios

    def set_master(self, scenario: Scenario):
        if scenario.cycle:
            # Doesn't belong to any cycle
            return
        if not scenario.is_master_scenario():
            scenarios = self.get_all_scenarios_of_cycle(scenario.cycle)
            for sc in scenarios:
                if sc.is_master_scenario():
                    sc.master_scenario = False
                    scenario.master_scenario = True
                    # TODO: test update master
                    self.set(sc)
                    self.set(scenario)
                    break

    def get_master(self, cycle: Cycle) -> Scenario:
        scenarios = self.get_all_scenarios_of_cycle(cycle)
        for scenario in scenarios:
            if scenario.is_master_scenario():
                master_scenario = scenario
        return master_scenario
