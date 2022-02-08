import datetime
import logging
from functools import partial
from typing import Callable, List, Optional, Union

from taipy.common.alias import ScenarioId
from taipy.config.config import Config
from taipy.config.scenario_config import ScenarioConfig
from taipy.cycle.cycle import Cycle
from taipy.cycle.manager.cycle_manager import CycleManager
from taipy.data.manager import DataManager
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
from taipy.job.job import Job
from taipy.pipeline.manager import PipelineManager
from taipy.scenario.repository import ScenarioRepository
from taipy.scenario.scenario import Scenario
from taipy.task.manager import TaskManager


class ScenarioManager:
    """
    Scenario Manager is responsible for all managing scenario related capabilities. In particular, it is exposing
    methods for creating, storing, updating, retrieving, deleting, submitting scenarios.
    """

    pipeline_manager = PipelineManager()
    cycle_manager = CycleManager
    repository = ScenarioRepository()
    task_manager = TaskManager
    data_manager = DataManager

    @classmethod
    def subscribe(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Subscribes a function to be called each time one of the provided scenario jobs changes status.
        If scenario is not passed, the subscription is added to all scenarios.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        if scenario is None:
            scenarios = cls.get_all()
            for scn in scenarios:
                cls.__add_subscriber(callback, scn)
            return

        cls.__add_subscriber(callback, scenario)

    @classmethod
    def unsubscribe(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If scenario is not passed, the subscription is removed to all scenarios.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        if scenario is None:
            scenarios = cls.get_all()
            for scn in scenarios:
                cls.__remove_subscriber(callback, scn)
            return

        cls.__remove_subscriber(callback, scenario)

    @classmethod
    def __add_subscriber(cls, callback, scenario):
        scenario.add_subscriber(callback)
        cls.set(scenario)

    @classmethod
    def __remove_subscriber(cls, callback, scenario):
        scenario.remove_subscriber(callback)
        cls.set(scenario)

    @classmethod
    def delete_all(cls):
        """Deletes all data nodes."""
        cls.repository.delete_all()

    @classmethod
    def create(
        cls,
        config: ScenarioConfig,
        creation_date: Optional[datetime.datetime] = None,
        display_name: Optional[str] = None,
    ) -> Scenario:
        """
        Creates and returns a new scenario from the scenario configuration provided as parameter.

        If the scenario belongs to a work cycle, the cycle (corresponding to the creation_date and the configuration
        frequency attribute) is created if it does not exist yet.

        Parameters:
            config (ScenarioConfig) : Scenario configuration object.
            creation_date (Optional[datetime.datetime]) : Creation date of the scenario. Current date time is used as default value.
            display_name (Optional[str]) : Display name of the scenario.
        """
        scenario_id = Scenario.new_id(config.name)
        pipelines = [cls.pipeline_manager.get_or_create(p_config, scenario_id) for p_config in config.pipelines_configs]
        cycle = CycleManager.get_or_create(config.frequency, creation_date) if config.frequency else None
        is_master_scenario = len(cls.get_all_by_cycle(cycle)) == 0 if cycle else False
        config.properties["display_name"] = display_name
        scenario = Scenario(
            config.name,
            pipelines,
            config.properties,
            scenario_id,
            creation_date,
            is_master=is_master_scenario,
            cycle=cycle,
        )

        cls.set(scenario)
        return scenario

    @classmethod
    def set(cls, scenario: Scenario):
        """
        Saves or Updates the scenario given as parameter.

        Parameters:
            scenario (Scenario) : Scenario to save or update.
        """
        cls.repository.save(scenario)

    @classmethod
    def get(cls, scenario: Union[Scenario, ScenarioId]) -> Scenario:
        """
        Returns the scenario corresponding to the scenario or the identifier given as parameter.

        Parameters:
            scenario (Union[Scenario, ScenarioId]) : scenario to get.
        Raises:
            NonExistingScenario : No scenario corresponds to scenario_id.
        """
        try:
            scenario_id = scenario.id if isinstance(scenario, Scenario) else scenario
            return cls.repository.load(scenario_id)
        except ModelNotFound:
            logging.error(f"Scenario entity: {scenario_id} does not exist.")
            raise NonExistingScenario(scenario_id)

    @classmethod
    def get_all(cls) -> List[Scenario]:
        """
        Returns the list of all existing scenarios.
        """
        return cls.repository.load_all()

    @classmethod
    def submit(cls, scenario: Union[Scenario, ScenarioId]):
        """
        Submits the scenario corresponding to the scenario of the identifier given as parameter for execution.

        All the tasks of scenario will be submitted for execution.

        Parameters:
            scenario (Union[Scenario, ScenarioId]) : the scenario or its identifier to submit.
        """
        if isinstance(scenario, Scenario):
            scenario = cls.get(scenario.id)
        else:
            scenario = cls.get(scenario)
        callbacks = cls.__get_status_notifier_callbacks(scenario)
        for pipeline in scenario.pipelines.values():
            cls.pipeline_manager.submit(pipeline, callbacks)

    @classmethod
    def __get_status_notifier_callbacks(cls, scenario: Scenario) -> List:
        return [partial(c, scenario) for c in scenario.subscribers]

    @classmethod
    def get_master(cls, cycle: Cycle) -> Optional[Scenario]:
        """
        Returns the master scenario of the cycle given as parameter. None is the cycle has no master scenario.

        Parameters:
             cycle (Cycle) : cycle of the master scenario to return.
        """
        scenarios = cls.get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.master_scenario:
                return scenario
        return None

    @classmethod
    def get_all_by_cycle(cls, cycle: Cycle) -> List[Scenario]:
        """
        Returns the list of all existing scenarios that belong to the cycle given as parameter.

        Parameters:
             cycle (Cycle) : Cycle of the scenarios to return.
        """
        scenarios = []
        for scenario in cls.get_all():
            if scenario.cycle == cycle:
                scenarios.append(scenario)
        return scenarios

    @classmethod
    def get_all_masters(cls) -> List[Scenario]:
        """Returns the list of all master scenarios."""
        master_scenarios = []
        for scenario in cls.get_all():
            if scenario.master_scenario:
                master_scenarios.append(scenario)
        return master_scenarios

    @classmethod
    def set_master(cls, scenario: Scenario):
        """
        Promotes scenario given as parameter as master scenario of its cycle. If the cycle already had a master scenario
        it will be demoted and it will no longer be master for the cycle.

        Parameters:
            scenario (Scenario) : scenario to promote as master.
        """
        if scenario.cycle:
            master_scenario = cls.get_master(scenario.cycle)
            if master_scenario:
                master_scenario.master_scenario = False
                cls.set(master_scenario)
            scenario.master_scenario = True
            cls.set(scenario)
        else:
            raise DoesNotBelongToACycle

    @classmethod
    def delete(cls, scenario_id: ScenarioId):
        """
        Deletes the scenario given as parameter.

        Parameters:
            scenario_id (ScenarioId) : identifier of the scenario to delete.
        Raises:
            DeletingMasterScenario : scenario_id corresponds to a master Scenario. It cannot be deleted.
            ModelNotFound : No scenario corresponds to scenario_id.
        """
        if cls.get(scenario_id).master_scenario:
            raise DeletingMasterScenario
        cls.repository.delete(scenario_id)

    @classmethod
    def compare(cls, *scenarios: Scenario, ds_config_name: str = None):
        """
        Compares the data nodes of given scenarios with known datanode config name.

        Parameters:
            scenarios (Scenario) : Scenario objects to compare
            ds_config_name (Optional[str]) : config name of the DataNode to compare scenarios, if no ds_config_name is
            provided, the scenarios will be compared based on all the previously defined comparators.
        Raises:
            InsufficientScenarioToCompare: Provided only one or no scenario for comparison
            NonExistingComparator: The provided comparator does not exist
            DifferentScenarioConfigs: The provided scenarios do not share the same scenario_config
            NonExistingScenarioConfig: Cannot find the shared scenario config of the provided scenarios
        """

        if len(scenarios) < 2:
            raise InsufficientScenarioToCompare

        if not all([scenarios[0].config_name == scenario.config_name for scenario in scenarios]):
            raise DifferentScenarioConfigs

        if scenario_config := Config.scenarios().get(scenarios[0].config_name, None):
            results = {}
            if ds_config_name:
                if ds_config_name in scenario_config.comparators.keys():
                    ds_comparators = {ds_config_name: scenario_config.comparators[ds_config_name]}
                else:
                    raise NonExistingComparator
            else:
                ds_comparators = scenario_config.comparators

            for ds_config_name, comparators in ds_comparators.items():
                datanodes = [scenario.__getattr__(ds_config_name).read() for scenario in scenarios]
                results[ds_config_name] = {comparator.__name__: comparator(*datanodes) for comparator in comparators}

            return results

        else:
            raise NonExistingScenarioConfig(scenarios[0].config_name)

    @classmethod
    def hard_delete(cls, scenario_id: ScenarioId):
        """
        Deletes the scenario given as parameter and the nested pipelines, tasks, data nodes, and jobs.

        Deletes the scenario given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested pipeline if the pipeline is not shared by another scenario.

        Parameters:
        scenario_id (ScenarioId) : identifier of the scenario to hard delete.

        Raises:
        ModelNotFound error if no scenario corresponds to scenario_id.
        """
        scenario = cls.get(scenario_id)
        if scenario.master_scenario:
            raise DeletingMasterScenario
        else:
            for pipeline in scenario.pipelines.values():
                if pipeline.parent_id == scenario.id or pipeline.parent_id == pipeline.id:
                    cls.pipeline_manager.hard_delete(pipeline.id, scenario.id)
            cls.repository.delete(scenario_id)
