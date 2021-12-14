import datetime
import logging
from functools import partial
from typing import Callable, List, Optional

from taipy.common.alias import ScenarioId
from taipy.config import Config, ScenarioConfig
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.exceptions.repository import ModelNotFound
from taipy.exceptions.scenario import (
    DeletingMasterScenario,
    DifferentScenarioConfigs,
    DoesNotBelongToACycle,
    InsufficientScenarioToCompare,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
)
from taipy.pipeline import PipelineManager
from taipy.scenario import Scenario
from taipy.scenario.repository import ScenarioRepository
from taipy.task import Job


class ScenarioManager:
    """
    Scenario Manager is responsible for all managing scenario related capabilities. In particular, it is exposing
    methods for creating, storing, updating, retrieving, deleting, submitting scenarios.
    """

    pipeline_manager = PipelineManager()
    cycle_manager = CycleManager()
    task_manager = pipeline_manager.task_manager
    data_manager = pipeline_manager.data_manager
    repository = ScenarioRepository(dir_name="scenarios")

    def subscribe(self, callback: Callable[[Scenario, Job], None], scenario: Scenario):
        """
        Subscribes a function to be called each time one of the provided scenario jobs changes status.

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
        """Deletes all data sources."""
        self.repository.delete_all()

    def create(self, config: ScenarioConfig, creation_date: Optional[datetime.datetime] = None) -> Scenario:
        """
        Creates and returns a new scenario from the scenario configuration provided as parameter.

        If the scenario belongs to a work cycle, the cycle (corresponding to the creation_date and the configuration
        frequency attribute) is created if it does not exist yet.

        Parameters:
            config (ScenarioConfig) : scenario configuration object.
            creation_date (Optional[datetime.datetime]) : Creation date of the scenario. Current date time is used as
                default value.
        """
        scenario_id = Scenario.new_id(config.name)
        pipelines = [
            self.pipeline_manager.get_or_create(p_config, scenario_id) for p_config in config.pipelines_configs
        ]
        cycle = self.cycle_manager.get_or_create(config.frequency, creation_date) if config.frequency else None
        is_master_scenario = len(self.get_all_by_cycle(cycle)) == 0 if cycle else False
        scenario = Scenario(
            config.name, pipelines, config.properties, scenario_id, is_master=is_master_scenario, cycle=cycle
        )

        self.set(scenario)
        return scenario

    def set(self, scenario: Scenario):
        """
        Saves or Updates the scenario given as parameter.

        Parameters:
            scenario (Scenario) : Scenario to save or update.
        """
        self.repository.save(scenario)

    def get(self, scenario_id: ScenarioId) -> Scenario:
        """
        Returns the scenario corresponding to the identifier given as parameter.

        Parameters:
            scenario_id (ScenarioId) : scenario to get.
        Raises:
            NonExistingScenario : No scenario corresponds to scenario_id.
        """
        try:
            if scenario := self.repository.load(scenario_id):
                return scenario
            raise ModelNotFound
        except ModelNotFound:
            logging.error(f"Scenario entity: {scenario_id} does not exist.")
            raise NonExistingScenario(scenario_id)

    def get_all(self) -> List[Scenario]:
        """
        Returns the list of all existing scenarios.
        """
        return self.repository.load_all()

    def submit(self, scenario_id: ScenarioId):
        """
        Submits the scenario corresponding to the identifier given as parameter for execution.

        All the tasks of scenario will be submitted for execution.

        Parameters:
            scenario_id (ScenarioId) : identifier of the scenario to submit.
        """
        scenario_to_submit = self.get(scenario_id)
        callbacks = self.__get_status_notifier_callbacks(scenario_to_submit)
        for pipeline in scenario_to_submit.pipelines.values():
            self.pipeline_manager.submit(pipeline.id, callbacks)

    def __get_status_notifier_callbacks(self, scenario: Scenario) -> List:
        return [partial(c, scenario) for c in scenario.subscribers]

    def get_master(self, cycle: Cycle) -> Optional[Scenario]:
        """
        Returns the master scenario of the cycle given as parameter. None is the cycle has no master scenario.

        Parameters:
             cycle (Cycle) : cycle of the master scenario to return.
        """
        scenarios = self.get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.master_scenario:
                return scenario
        return None

    def get_all_by_cycle(self, cycle: Cycle) -> List[Scenario]:
        """
        Returns the list of all existing scenarios that belong to the cycle given as parameter.

        Parameters:
             cycle (Cycle) : Cycle of the scenarios to return.
        """
        scenarios = []
        for scenario in self.get_all():
            if scenario.cycle == cycle:
                scenarios.append(scenario)
        return scenarios

    def get_all_masters(self) -> List[Scenario]:
        """Returns the list of all master scenarios."""
        master_scenarios = []
        for scenario in self.get_all():
            if scenario.master_scenario:
                master_scenarios.append(scenario)
        return master_scenarios

    def set_master(self, scenario: Scenario):
        """
        Promotes scenario given as parameter as master scenario of its cycle. If the cycle already had a master scenario
        it will be demoted and it will no longer be master for the cycle.

        Parameters:
            scenario (Scenario) : scenario to promote as master.
        """
        if scenario.cycle:
            master_scenario = self.get_master(scenario.cycle)
            if master_scenario:
                master_scenario.master_scenario = False
                self.set(master_scenario)
            scenario.master_scenario = True
            self.set(scenario)
        else:
            raise DoesNotBelongToACycle

    def delete(self, scenario_id: ScenarioId):
        """
        Deletes the scenario given as parameter.

        Parameters:
            scenario_id (ScenarioId) : identifier of the scenario to delete.
        Raises:
            DeletingMasterScenario : scenario_id corresponds to a master Scenario. It cannot be deleted.
            ModelNotFound : No scenario corresponds to scenario_id.
        """
        if self.get(scenario_id).master_scenario:
            raise DeletingMasterScenario
        self.repository.delete(scenario_id)

    def compare(self, *scenarios: Scenario, ds_config_name: str = None):
        """
        Compares the datasources of given scenarios with known datasource config name.

        Parameters:
            scenarios (Scenario) : list of Scenario objects to compare
            ds_config_name (Optional[str]) : config name of the DataSource to compare scenarios, if no ds_config_name is
            provided, the scenarios will be compared based on all the previously defined comparators.
        Raises:
            InsufficientScenarioToCompare: Provided only one or no scenario for comparison
            NonExistingComparator: The provided comparator does not exist
            DifferentScenarioConfig: The provided scenarios do not share the same scenario_config
            NonExistingScenarioConfig: Cannot find the shared scenario config of the provided scenarios
        """

        if len(scenarios) < 2:
            raise InsufficientScenarioToCompare

        if not all([scenarios[0].config_name == scenario.config_name for scenario in scenarios]):
            raise DifferentScenarioConfigs

        if scenario_config := Config.scenario_configs.get(scenarios[0].config_name, None):
            results = {}
            if ds_config_name:
                if ds_config_name in scenario_config.comparators.keys():
                    ds_comparators = {ds_config_name: scenario_config.comparators[ds_config_name]}
                else:
                    raise NonExistingComparator
            else:
                ds_comparators = scenario_config.comparators

            for ds_config_name, comparators in ds_comparators.items():
                datasources = [scenario.__getattr__(ds_config_name) for scenario in scenarios]
                results[ds_config_name] = {comparator.__name__: comparator(*datasources) for comparator in comparators}

            return results

        else:
            raise NonExistingScenarioConfig(scenarios[0].config_name)
