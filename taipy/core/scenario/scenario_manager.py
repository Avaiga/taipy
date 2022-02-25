import datetime
from functools import partial
from typing import Callable, List, Optional, Union

from taipy.core.common.alias import ScenarioId
from taipy.core.common.logger import TaipyLogger
from taipy.core.config.config import Config
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_manager import CycleManager
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.exceptions.scenario import (
    DeletingMasterScenario,
    DifferentScenarioConfigs,
    DoesNotBelongToACycle,
    InsufficientScenarioToCompare,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
    UnauthorizedTagError,
)
from taipy.core.job.job import Job
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_repository import ScenarioRepository


class ScenarioManager:
    """
    Scenario Manager is responsible for all managing scenario related capabilities. In particular, it is exposing
    methods for creating, storing, updating, retrieving, deleting, submitting scenarios.
    """

    AUTHORIZED_TAGS_KEY = "authorized_tags"
    repository = ScenarioRepository()
    __logger = TaipyLogger.get_logger()

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
        """Deletes all scenarios."""
        cls.repository.delete_all()

    @classmethod
    def create(
        cls,
        config: ScenarioConfig,
        creation_date: datetime.datetime = None,
        display_name: str = None,
    ) -> Scenario:
        """
        Creates and returns a new scenario from the scenario configuration provided as parameter.

        If the scenario belongs to a work cycle, the cycle (corresponding to the creation_date and the configuration
        frequency attribute) is created if it does not exist yet.

        Parameters:
            config (ScenarioConfig) : Scenario configuration object.
            creation_date (Optional[datetime.datetime]) : Creation date of the scenario. Current date time is used as
                default value.
            display_name (Optional[str]) : Display name of the scenario.
        """
        scenario_id = Scenario.new_id(config.name)
        pipelines = [PipelineManager.get_or_create(p_config, scenario_id) for p_config in config.pipelines_configs]
        cycle = CycleManager.get_or_create(config.frequency, creation_date) if config.frequency else None
        is_master_scenario = len(cls.get_all_by_cycle(cycle)) == 0 if cycle else False
        props = config.properties.copy()
        if display_name:
            props["display_name"] = display_name
        scenario = Scenario(
            config.name,
            pipelines,
            props,
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
    def get(cls, scenario: Union[Scenario, ScenarioId], default=None) -> Scenario:
        """
        Returns the scenario corresponding to the scenario or the identifier given as parameter.

        Parameters:
            scenario (Union[Scenario, ScenarioId]) : scenario to get.
            default: Default value to return if scenario is not found. None is returned if no default value is provided.
        """
        scenario_id = scenario.id if isinstance(scenario, Scenario) else scenario
        try:
            return cls.repository.load(scenario_id)
        except ModelNotFound:
            cls.__logger.warning(f"Scenario entity: {scenario_id} does not exist.")
            return default

    @classmethod
    def get_all(cls) -> List[Scenario]:
        """
        Returns the list of all existing scenarios.
        """
        return cls.repository.load_all()

    @classmethod
    def submit(cls, scenario: Union[Scenario, ScenarioId], force: bool = False):
        """
        Submits the scenario corresponding to the scenario of the identifier given as parameter for execution.

        All the tasks of scenario will be submitted for execution.

        Parameters:
            scenario (Union[Scenario, ScenarioId]) : the scenario or its identifier to submit.
            force: Boolean to enforce re execution of the tasks whatever the cache data nodes.

        Raises:
            NonExistingScenario : No scenario is found with the given identifier.
        """
        scenario_id = scenario.id if isinstance(scenario, Scenario) else scenario
        scenario = cls.get(scenario_id)
        if scenario is None:
            raise NonExistingScenario(scenario_id)
        callbacks = cls.__get_status_notifier_callbacks(scenario)
        for pipeline in scenario.pipelines.values():
            PipelineManager.submit(pipeline, callbacks=callbacks, force=force)

    @classmethod
    def __get_status_notifier_callbacks(cls, scenario: Scenario) -> List:
        return [partial(c, scenario) for c in scenario.subscribers]

    @classmethod
    def get_master(cls, cycle: Cycle) -> Optional[Scenario]:
        """
        Returns the master scenario of the cycle given as parameter. None if the cycle has no master scenario.

        Parameters:
             cycle (Cycle) : cycle of the master scenario to return.
        """
        scenarios = cls.get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.is_master:
                return scenario
        return None

    @classmethod
    def get_by_tag(cls, cycle: Cycle, tag: str) -> Optional[Scenario]:
        """
        Returns the scenario of the `cycle` given as parameter that is tagged by `tag` given as parameter.
        None if the cycle has no scenario tagged by `tag`.

        Parameters:
             cycle (Cycle) : cycle of the scenario to return.
             tag (str) : tag of the scenario to return.
        """
        scenarios = cls.get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.has_tag(tag):
                return scenario
        return None

    @classmethod
    def get_all_by_tag(cls, tag: str) -> List[Scenario]:
        """
        Returns the list of all existing scenarios tagged by `tag` given as parameter.

        Parameters:
             tag (str) : Tag of the scenarios to return.
        """
        scenarios = []
        for scenario in cls.get_all():
            if scenario.has_tag(tag):
                scenarios.append(scenario)
        return scenarios

    @classmethod
    def get_all_by_cycle(cls, cycle: Cycle) -> List[Scenario]:
        """
        Returns the list of all existing scenarios that belong to the cycle given as parameter.

        Parameters:
             cycle (Cycle) : Cycle of the scenarios to return.
        """
        scenarios = []
        for scenario in cls.get_all():
            if scenario.cycle and scenario.cycle == cycle:
                scenarios.append(scenario)
        return scenarios

    @classmethod
    def get_all_masters(cls) -> List[Scenario]:
        """Returns the list of all master scenarios."""
        master_scenarios = []
        for scenario in cls.get_all():
            if scenario.is_master:
                master_scenarios.append(scenario)
        return master_scenarios

    @classmethod
    def set_master(cls, scenario: Scenario):
        """
        Promotes scenario given as parameter as master scenario of its cycle. If the cycle already had a master scenario
        it will be demoted, and it will no longer be master for the cycle.

        Parameters:
            scenario (Scenario) : scenario to promote as master.
        """
        if scenario.cycle:
            master_scenario = cls.get_master(scenario.cycle)
            if master_scenario:
                master_scenario._master_scenario = False
                cls.set(master_scenario)
            scenario._master_scenario = True
            cls.set(scenario)
        else:
            raise DoesNotBelongToACycle

    @classmethod
    def tag(cls, scenario: Scenario, tag: str):
        """
        Adds `tag` given as parameter to `scenario` given as parameter. If the scenario's cycle already have
        another scenario tagged by `tag` the other scenario will be untagged.

        Parameters:
            scenario (Scenario) : scenario to tag.
            tag (str) : Tag of the scenario to tag.
        """
        tags = scenario.properties.get(cls.AUTHORIZED_TAGS_KEY, set())
        if len(tags) > 0 and tag not in tags:
            raise UnauthorizedTagError(f"Tag `{tag}` not authorized by scenario configuration `{scenario.config_name}`")
        if scenario.cycle:
            old_tagged_scenario = cls.get_by_tag(scenario.cycle, tag)
            if old_tagged_scenario:
                old_tagged_scenario.remove_tag(tag)
                cls.set(old_tagged_scenario)
        scenario.add_tag(tag)
        cls.set(scenario)

    @classmethod
    def untag(cls, scenario: Scenario, tag: str):
        """
        Removes `tag` given as parameter from `scenario` given as parameter.

        Parameters:
            scenario (Scenario) : scenario to untag.
            tag (str) : Tag to remove from scenario.
        """
        scenario.remove_tag(tag)
        cls.set(scenario)

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
        if cls.get(scenario_id).is_master:
            raise DeletingMasterScenario
        cls.repository.delete(scenario_id)

    @classmethod
    def compare(cls, *scenarios: Scenario, data_node_config_name: str = None):
        """
        Compares the data nodes of given scenarios with known datanode config name.

        Parameters:
            scenarios (Scenario) : Scenario objects to compare
            data_node_config_name (Optional[str]) : config name of the DataNode to compare scenarios, if no
                data_node_config_name is provided, the scenarios will be compared based on all the previously
                defined comparators.
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

        if scenario_config := ScenarioManager.__get_config(scenarios[0]):
            results = {}
            if data_node_config_name:
                if data_node_config_name in scenario_config.comparators.keys():
                    dn_comparators = {data_node_config_name: scenario_config.comparators[data_node_config_name]}
                else:
                    raise NonExistingComparator
            else:
                dn_comparators = scenario_config.comparators

            for data_node_config_name, comparators in dn_comparators.items():
                data_nodes = [scenario.__getattr__(data_node_config_name).read() for scenario in scenarios]
                results[data_node_config_name] = {
                    comparator.__name__: comparator(*data_nodes) for comparator in comparators
                }

            return results

        else:
            raise NonExistingScenarioConfig(scenarios[0].config_name)

    @staticmethod
    def __get_config(scenario: Scenario):
        return Config.scenarios.get(scenario.config_name, None)

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
        if scenario.is_master:
            raise DeletingMasterScenario
        else:
            for pipeline in scenario.pipelines.values():
                if pipeline.parent_id == scenario.id or pipeline.parent_id == pipeline.id:
                    PipelineManager.hard_delete(pipeline.id, scenario.id)
            cls.repository.delete(scenario_id)
