"""Main module."""
from datetime import datetime
from typing import Callable, Dict, List, Optional, Union

from taipy.common.alias import CycleId, DataNodeId, JobId, PipelineId, ScenarioId, TaskId
from taipy.common.frequency import Frequency
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config
from taipy.config.data_node_config import DataNodeConfig
from taipy.config.global_app_config import GlobalAppConfig
from taipy.config.job_config import JobConfig
from taipy.config.pipeline_config import PipelineConfig
from taipy.config.scenario_config import ScenarioConfig
from taipy.config.task_config import TaskConfig
from taipy.cycle.cycle import Cycle
from taipy.data.data_node import DataNode
from taipy.data.scope import Scope
from taipy.exceptions import ModelNotFound
from taipy.job.job import Job
from taipy.pipeline.pipeline import Pipeline
from taipy.scenario.scenario import Scenario
from taipy.scenario.scenario_manager import ScenarioManager
from taipy.task.task import Task


class Taipy:
    """Main Taipy class"""

    scenario_manager = ScenarioManager()
    cycle_manager = scenario_manager.cycle_manager
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    job_manager = pipeline_manager.scheduler.job_manager

    @classmethod
    def set(cls, entity: Union[DataNode, Task, Pipeline, Scenario, Cycle]):
        """
        Saves or updates a data node, a task, a job, a pipeline, a scenario or a cycle.

        Args:
            entity: The entity to save.
        """
        if isinstance(entity, Cycle):
            return cls.cycle_manager.set(entity)
        if isinstance(entity, Scenario):
            return cls.scenario_manager.set(entity)
        if isinstance(entity, Pipeline):
            return cls.pipeline_manager.set(entity)
        if isinstance(entity, Task):
            return cls.task_manager.set(entity)
        if isinstance(entity, DataNode):
            return cls.data_manager.set(entity)

    @classmethod
    def submit(cls, entity: Union[Scenario, Pipeline]):
        """
        Submits the entity given as parameter for execution.

        All the tasks of the entity task/pipeline/scenario will be submitted for execution.

        Parameters:
            entity (Union[Scenario, ScenarioId]) : the entity or its identifier to submit.
        """
        if isinstance(entity, Scenario):
            return cls.scenario_manager.submit(entity)
        if isinstance(entity, Pipeline):
            return cls.pipeline_manager.submit(entity)

    @classmethod
    def get(
        cls, id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]
    ) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
        """
        Gets an entity given the identifier as parameter.

        Args:
            entity (Union[TaskId, DataNodeId, PipelineId, ScenarioId]): The identifier of the entity to get.

        Returns:
            The entity corresponding to the provided identifier.

        Raises:
            ModelNotFound: if no entity corresponds to `entity_id`.
        """
        if id.startswith(cls.job_manager.ID_PREFIX):
            return cls.job_manager.get(JobId(id))
        if id.startswith(Cycle.ID_PREFIX):
            return cls.cycle_manager.get(CycleId(id))
        if id.startswith(Scenario.ID_PREFIX):
            return cls.scenario_manager.get(ScenarioId(id))
        if id.startswith(Pipeline.ID_PREFIX):
            return cls.pipeline_manager.get(PipelineId(id))
        if id.startswith(Task.ID_PREFIX):
            return cls.task_manager.get(TaskId(id))
        if id.startswith(DataNode.ID_PREFIX):
            return cls.data_manager.get(DataNodeId(id))
        raise ModelNotFound("NOT_DETERMINED", id)

    @classmethod
    def get_tasks(cls) -> List[Task]:
        """
        Returns the list of all existing tasks.

        Returns:
            List: The list of tasks handled by this Task Manager.
        """
        return cls.task_manager.get_all()

    @classmethod
    def delete_scenario(cls, scenario_id: ScenarioId):
        """
        Deletes the scenario given as parameter and the nested pipelines, tasks, data nodes, and jobs.

        Deletes the scenario given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested pipeline if the pipeline is not shared by another scenario.

        Parameters:
        scenario_id (ScenarioId) : identifier of the scenario to hard delete.

        Raises:
        ModelNotFound error if no scenario corresponds to scenario_id.
        """
        return cls.scenario_manager.hard_delete(scenario_id)

    @classmethod
    def get_scenarios(cls, cycle: Optional[Cycle] = None) -> List[Scenario]:
        """
        Returns the list of all existing scenarios filtered by cycle if given as parameter.

        Parameters:
             cycle (Optional[Cycle]) : Cycle of the scenarios to return.
        """
        if not cycle:
            return cls.scenario_manager.get_all()
        return cls.scenario_manager.get_all_by_cycle(cycle)

    @classmethod
    def get_master(cls, cycle: Cycle) -> Optional[Scenario]:
        """
        Returns the master scenario of the cycle given as parameter. None if the cycle has no master scenario.

        Parameters:
             cycle (Cycle) : cycle of the master scenario to return.
        """
        return cls.scenario_manager.get_master(cycle)

    @classmethod
    def get_all_masters(cls) -> List[Scenario]:
        """Returns the list of all master scenarios."""
        return cls.scenario_manager.get_all_masters()

    @classmethod
    def set_master(cls, scenario: Scenario):
        """
        Promotes scenario given as parameter as master scenario of its cycle. If the cycle already had a master scenario
        it will be demoted, and it will no longer be master for the cycle.

        Parameters:
            scenario (Scenario) : scenario to promote as master.
        """
        return cls.scenario_manager.set_master(scenario)

    @classmethod
    def compare_scenarios(cls, *scenarios: Scenario, data_node_config_name: str = None):
        """
        Compares the data nodes of given scenarios with known datanode config name.

        Parameters:
            scenarios (Scenario) : Scenario objects to compare
            data_node_config_name (Optional[str]) : config name of the DataNode to compare scenarios, if no
                datanode_config_name is provided, the scenarios will be compared based on all the previously defined
                comparators.
        Raises:
            InsufficientScenarioToCompare: Provided only one or no scenario for comparison
            NonExistingComparator: The provided comparator does not exist
            DifferentScenarioConfigs: The provided scenarios do not share the same scenario_config
            NonExistingScenarioConfig: Cannot find the shared scenario config of the provided scenarios
        """
        cls.scenario_manager.compare(*scenarios, data_node_config_name=data_node_config_name)

    @classmethod
    def subscribe_scenario(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Subscribes a function to be called each time one of the provided scenario jobs changes status.
        If scenario is not passed, the subscription is added to all scenarios.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        return cls.scenario_manager.subscribe(callback, scenario)

    @classmethod
    def unsubscribe_scenario(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If scenario is not passed, the subscription is removed to all scenarios.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        return cls.scenario_manager.unsubscribe(callback, scenario)

    @classmethod
    def subscribe_pipeline(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Subscribes a function to be called when the status of a Job changes.
        If pipeline is not passed, the subscription is added to all pipelines.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        return cls.pipeline_manager.subscribe(callback, pipeline)

    @classmethod
    def unsubscribe_pipeline(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If pipeline is not passed, the subscription is removed to all pipelines.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        return cls.pipeline_manager.unsubscribe(callback, pipeline)

    @classmethod
    def delete_pipeline(cls, pipeline_id: PipelineId):
        """
        Deletes the pipeline given as parameter and the nested tasks, data nodes, and jobs.

        Deletes the pipeline given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested task if the task is not shared by another pipeline.

        Parameters:
        pipeline_id (PipelineId) : identifier of the pipeline to hard delete.

        Raises:
        ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        return cls.pipeline_manager.hard_delete(pipeline_id)

    @classmethod
    def get_pipelines(cls) -> List[Pipeline]:
        """
        Returns all existing pipelines.

        Returns:
            List[Pipeline]: the list of all pipelines managed by this pipeline manager.
        """
        return cls.pipeline_manager.get_all()

    @classmethod
    def get_jobs(cls) -> List[Job]:
        """Gets all the existing jobs.

        Returns:
            List of all jobs.
        """
        return cls.job_manager.get_all()

    @classmethod
    def delete_job(cls, job: Job, force=False):
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        return cls.job_manager.delete(job, force)

    @classmethod
    def delete_jobs(cls):
        """Deletes all jobs."""
        cls.job_manager.delete_all()

    @classmethod
    def get_latest_job(cls, task: Task) -> Job:
        """Gets the latest job of a task.

        Returns:
            The latest computed job of the task.
        """
        return cls.job_manager.get_latest(task)

    @classmethod
    def get_data_nodes(cls) -> List[DataNode]:
        """Returns the list of all existing data nodes."""
        return cls.data_manager.get_all()

    @classmethod
    def create_scenario(cls, config: ScenarioConfig, creation_date: datetime = None, name: str = None) -> Scenario:
        """
        Creates and returns a new scenario from the scenario configuration provided as parameter.

        If the scenario belongs to a work cycle, the cycle (corresponding to the creation_date and the configuration
        frequency attribute) is created if it does not exist yet.

        Parameters:
            config (ScenarioConfig) : Scenario configuration object.
            creation_date (Optional[datetime.datetime]) : Creation date. Current date time used as default value.
            name (Optional[str]) : Display name of the scenario.
        """
        return cls.scenario_manager.create(config, creation_date, name)

    @classmethod
    def create_pipeline(cls, config: PipelineConfig) -> Pipeline:
        """
        Creates and Returns a new pipeline from the pipeline configuration given as parameter.

        Parameters:
            config (PipelineConfig): The pipeline configuration object.

        """
        return cls.pipeline_manager.get_or_create(config)

    @staticmethod
    def load_configuration(filename):
        """
        Loads configuration from file located at the filename given as parameter.

        Parameters:
            filename (str or Path): File to load.
        """
        return Config.load(filename)

    @staticmethod
    def export_configuration(filename):
        """
        Exports the configuration to a toml file.

        The configuration exported is the configuration applied. It is compiled from the three possible methods to
        configure the application: The python code configuration, the file configuration and the environment
        configuration.

        Parameters:
            filename (str or Path): File to export.
        Note:
            Overwrite the file if it already exists.
        """
        return Config.export(filename)

    @staticmethod
    def configure_global_app(
        notification: Union[bool, str] = None,
        broker_endpoint: str = None,
        root_folder: str = None,
        storage_folder: str = None,
        **properties
    ) -> GlobalAppConfig:
        """Configures fields related to global application."""
        return Config.set_global_config(notification, broker_endpoint, root_folder, storage_folder, **properties)

    @staticmethod
    def configure_job_executions(
        mode: str = None,
        nb_of_workers: Union[int, str] = None,
        hostname: str = None,
        airflow_dags_folder: str = None,
        airflow_folder: str = None,
        start_airflow: Union[bool, str] = None,
        airflow_api_retry: Union[int, str] = None,
        airflow_user: str = None,
        airflow_password: str = None,
        **properties
    ) -> JobConfig:
        """Configures fields related to job execution."""
        return Config.set_job_config(
            mode,
            nb_of_workers,
            hostname,
            airflow_dags_folder,
            airflow_folder,
            start_airflow,
            airflow_api_retry,
            airflow_user,
            airflow_password,
            **properties
        )

    @staticmethod
    def configure_data_node(
        name: str, storage_type: str = "pickle", scope: Scope = Scope.PIPELINE, **properties
    ) -> DataNodeConfig:
        """Configures a new data node configuration."""
        return Config.add_data_node(name, storage_type, scope, **properties)

    @staticmethod
    def configure_default_data_node(storage_type: str, scope=Scope.PIPELINE, **properties) -> DataNodeConfig:
        """Configures the default behavior of a data node configuration."""
        return Config.add_default_data_node(storage_type, scope, **properties)

    @staticmethod
    def configure_task(
        name: str,
        input: Union[DataNodeConfig, List[DataNodeConfig]],
        function,
        output: Union[DataNodeConfig, List[DataNodeConfig]],
        **properties
    ) -> TaskConfig:
        """Configures a new task configuration."""
        return Config.add_task(name, input, function, output, **properties)

    @staticmethod
    def configure_default_task(
        input: Union[DataNodeConfig, List[DataNodeConfig]],
        function,
        output: Union[DataNodeConfig, List[DataNodeConfig]],
        **properties
    ) -> TaskConfig:
        """Configures the default behavior of a task configuration."""
        return Config.add_default_task(input, function, output, **properties)

    @staticmethod
    def configure_pipeline(
        name: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties
    ) -> PipelineConfig:
        """Configures a new pipeline configuration."""
        return Config.add_pipeline(name, task_configs, **properties)

    @staticmethod
    def configure_default_pipeline(task_configs: Union[TaskConfig, List[TaskConfig]], **properties) -> PipelineConfig:
        """Configures the default behavior of a pipeline configuration."""
        return Config.add_default_pipeline(task_configs, **properties)

    @staticmethod
    def configure_scenario(
        name: str,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties
    ) -> ScenarioConfig:
        """Configures a new scenario configuration."""
        return Config.add_scenario(name, pipeline_configs, frequency, comparators, **properties)

    @staticmethod
    def configure_default_scenario(
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties
    ) -> ScenarioConfig:
        """Configures the default behavior of a scenario configuration."""
        return Config.add_default_scenario(pipeline_configs, frequency, comparators, **properties)

    @staticmethod
    def check_configuration() -> IssueCollector:
        return Config.check()
