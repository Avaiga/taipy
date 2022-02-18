"""Main module."""
import logging
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.core.common.alias import CycleId, DataNodeId, JobId, PipelineId, ScenarioId, TaskId
from taipy.core.common.frequency import Frequency
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.config import Config
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.config.task_config import TaskConfig
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_manager import CycleManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_manager import DataManager
from taipy.core.data.data_node import DataNode
from taipy.core.data.excel import ExcelDataNode
from taipy.core.data.generic import GenericDataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.data.scope import Scope
from taipy.core.data.sql import SQLDataNode
from taipy.core.exceptions import ModelNotFound
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_manager import ScenarioManager
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager


class Taipy:
    """Main Taipy class"""

    @classmethod
    def set(cls, entity: Union[DataNode, Task, Pipeline, Scenario, Cycle]):
        """
        Saves or updates a data node, a task, a job, a pipeline, a scenario or a cycle.

        Args:
            entity: The entity to save.
        """
        if isinstance(entity, Cycle):
            return CycleManager.set(entity)
        if isinstance(entity, Scenario):
            return ScenarioManager.set(entity)
        if isinstance(entity, Pipeline):
            return PipelineManager.set(entity)
        if isinstance(entity, Task):
            return TaskManager.set(entity)
        if isinstance(entity, DataNode):
            return DataManager.set(entity)

    @classmethod
    def submit(cls, entity: Union[Scenario, Pipeline]):
        """
        Submits the entity given as parameter for execution.

        All the tasks of the entity task/pipeline/scenario will be submitted for execution.

        Parameters:
            entity (Union[Scenario, Pipeline]) : the entity to submit.
        """
        if isinstance(entity, Scenario):
            return ScenarioManager.submit(entity)
        if isinstance(entity, Pipeline):
            return PipelineManager.submit(entity)

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
        if id.startswith(JobManager.ID_PREFIX):
            return JobManager.get(JobId(id))
        if id.startswith(Cycle.ID_PREFIX):
            return CycleManager.get(CycleId(id))
        if id.startswith(Scenario.ID_PREFIX):
            return ScenarioManager.get(ScenarioId(id))
        if id.startswith(Pipeline.ID_PREFIX):
            return PipelineManager.get(PipelineId(id))
        if id.startswith(Task.ID_PREFIX):
            return TaskManager.get(TaskId(id))
        if id.startswith(DataNode.ID_PREFIX):
            return DataManager.get(DataNodeId(id))
        raise ModelNotFound("NOT_DETERMINED", id)

    @classmethod
    def get_tasks(cls) -> List[Task]:
        """
        Returns the list of all existing tasks.

        Returns:
            List: The list of tasks handled by this Task Manager.
        """
        return TaskManager.get_all()

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
        return ScenarioManager.hard_delete(scenario_id)

    @classmethod
    def get_scenarios(cls, cycle: Optional[Cycle] = None) -> List[Scenario]:
        """
        Returns the list of all existing scenarios filtered by cycle if given as parameter.

        Parameters:
             cycle (Optional[Cycle]) : Cycle of the scenarios to return.
        """
        if not cycle:
            return ScenarioManager.get_all()
        return ScenarioManager.get_all_by_cycle(cycle)

    @classmethod
    def get_master(cls, cycle: Cycle) -> Optional[Scenario]:
        """
        Returns the master scenario of the cycle given as parameter. None if the cycle has no master scenario.

        Parameters:
             cycle (Cycle) : cycle of the master scenario to return.
        """
        return ScenarioManager.get_master(cycle)

    @classmethod
    def get_all_masters(cls) -> List[Scenario]:
        """Returns the list of all master scenarios."""
        return ScenarioManager.get_all_masters()

    @classmethod
    def set_master(cls, scenario: Scenario):
        """
        Promotes scenario given as parameter as master scenario of its cycle. If the cycle already had a master scenario
        it will be demoted, and it will no longer be master for the cycle.

        Parameters:
            scenario (Scenario) : scenario to promote as master.
        """
        return ScenarioManager.set_master(scenario)

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
        return ScenarioManager.compare(*scenarios, data_node_config_name=data_node_config_name)

    @classmethod
    def subscribe_scenario(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Subscribes a function to be called each time one of the provided scenario jobs changes status.
        If scenario is not passed, the subscription is added to all scenarios.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        return ScenarioManager.subscribe(callback, scenario)

    @classmethod
    def unsubscribe_scenario(cls, callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If scenario is not passed, the subscription is removed to all scenarios.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        return ScenarioManager.unsubscribe(callback, scenario)

    @classmethod
    def subscribe_pipeline(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Subscribes a function to be called when the status of a Job changes.
        If pipeline is not passed, the subscription is added to all pipelines.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        return PipelineManager.subscribe(callback, pipeline)

    @classmethod
    def unsubscribe_pipeline(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If pipeline is not passed, the subscription is removed to all pipelines.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        return PipelineManager.unsubscribe(callback, pipeline)

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
        return PipelineManager.hard_delete(pipeline_id)

    @classmethod
    def get_pipelines(cls) -> List[Pipeline]:
        """
        Returns all existing pipelines.

        Returns:
            List[Pipeline]: the list of all pipelines managed by this pipeline manager.
        """
        return PipelineManager.get_all()

    @classmethod
    def get_jobs(cls) -> List[Job]:
        """Gets all the existing jobs.

        Returns:
            List of all jobs.
        """
        return JobManager.get_all()

    @classmethod
    def delete_job(cls, job: Job, force=False):
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        return JobManager.delete(job, force)

    @classmethod
    def delete_jobs(cls):
        """Deletes all jobs."""
        return JobManager.delete_all()

    @classmethod
    def get_latest_job(cls, task: Task) -> Job:
        """Gets the latest job of a task.

        Returns:
            The latest computed job of the task.
        """
        return JobManager.get_latest(task)

    @classmethod
    def get_data_nodes(cls) -> List[DataNode]:
        """Returns the list of all existing data nodes."""
        return DataManager.get_all()

    @classmethod
    def get_cycles(cls) -> List[Cycle]:
        """Returns the list of all existing cycles."""
        return CycleManager.get_all()

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
        return ScenarioManager.create(config, creation_date, name)

    @classmethod
    def create_pipeline(cls, config: PipelineConfig) -> Pipeline:
        """
        Creates and Returns a new pipeline from the pipeline configuration given as parameter.

        Parameters:
            config (PipelineConfig): The pipeline configuration object.

        """
        return PipelineManager.get_or_create(config)

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
        clean_entities_enabled: Union[bool, str] = None,
        **properties
    ) -> GlobalAppConfig:
        """Configures fields related to global application."""
        return Config.set_global_config(
            notification, broker_endpoint, root_folder, storage_folder, clean_entities_enabled, **properties
        )

    @staticmethod
    def configure_job_executions(mode: str = None, nb_of_workers: Union[int, str] = None, **properties) -> JobConfig:
        """Configures fields related to job execution."""
        return Config.set_job_config(mode, nb_of_workers, **properties)

    @staticmethod
    def configure_data_node(
        name: str, storage_type: str = "pickle", scope: Scope = DataNodeConfig.DEFAULT_SCOPE, **properties
    ) -> DataNodeConfig:
        """Configures a new data node configuration."""
        return Config.add_data_node(name, storage_type, scope, **properties)

    @staticmethod
    def configure_default_data_node(
        storage_type: str, scope=DataNodeConfig.DEFAULT_SCOPE, **properties
    ) -> DataNodeConfig:
        """Configures the default behavior of a data node configuration."""
        return Config.add_default_data_node(storage_type, scope, **properties)

    @staticmethod
    def configure_csv_data_node(name: str, path: str, has_header=True, scope=Scope.PIPELINE, **properties):
        """Configures a new data node configuration with CSV storage type."""
        return Config.add_data_node(
            name, CSVDataNode.storage_type(), scope=scope, path=path, has_header=has_header, **properties
        )

    @staticmethod
    def configure_excel_data_node(
        name: str,
        path: str,
        has_header: bool = True,
        sheet_name: Union[List[str], str] = "Sheet1",
        scope: Scope = Scope.PIPELINE,
        **properties
    ):
        """Configures a new data node configuration with Excel storage type."""
        return Config.add_data_node(
            name,
            ExcelDataNode.storage_type(),
            scope=scope,
            path=path,
            has_header=has_header,
            sheet_name=sheet_name,
            **properties
        )

    @staticmethod
    def configure_generic_data_node(
        name: str, read_fct: Callable, write_fct: Callable, scope: Scope = Scope.PIPELINE, **properties
    ):
        """Configures a new data node configuration with Generic storage type."""
        return Config.add_data_node(
            name, GenericDataNode.storage_type(), scope=scope, read_fct=read_fct, write_fct=write_fct, **properties
        )

    @staticmethod
    def configure_in_memory_data_node(
        name: str, default_data: Optional[Any] = None, scope: Scope = Scope.PIPELINE, **properties
    ):
        """Configures a new data node configuration with In memory storage type."""
        return Config.add_data_node(
            name, InMemoryDataNode.storage_type(), scope=scope, default_data=default_data, **properties
        )

    @staticmethod
    def configure_pickle_data_node(
        name: str, default_data: Optional[Any] = None, scope: Scope = Scope.PIPELINE, **properties
    ):
        """Configures a new data node configuration with pickle storage type."""
        return Config.add_data_node(
            name, PickleDataNode.storage_type(), scope=scope, default_data=default_data, **properties
        )

    @staticmethod
    def configure_sql_data_node(
        name: str,
        db_username: str,
        db_password: str,
        db_name: str,
        db_engine: str,
        read_query: str,
        write_table: str,
        db_port: int = 143,
        scope: Scope = Scope.PIPELINE,
        **properties
    ):
        """Configures a new data node configuration with SQL storage type."""
        return Config.add_data_node(
            name,
            SQLDataNode.storage_type(),
            scope=scope,
            db_username=db_username,
            db_password=db_password,
            db_name=db_name,
            db_engine=db_engine,
            read_query=read_query,
            write_table=write_table,
            db_port=db_port,
            **properties
        )

    @staticmethod
    def configure_task(
        name: str,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties
    ) -> TaskConfig:
        """Configures a new task configuration."""
        return Config.add_task(name, function, input, output, **properties)

    @staticmethod
    def configure_default_task(
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties
    ) -> TaskConfig:
        """Configures the default behavior of a task configuration."""
        return Config.add_default_task(function, input, output, **properties)

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
    def configure_scenario_from_tasks(
        name: str,
        task_configs: List[TaskConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        pipeline_name: Optional[str] = None,
        **properties
    ) -> ScenarioConfig:
        """Configures a new scenario configuration from a list of tasks."""
        return Config.add_scenario_from_tasks(name, task_configs, frequency, comparators, pipeline_name, **properties)

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
    def clean_all_entities() -> bool:
        """
        Deletes all entities from the data folder.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        if not Config.global_config().clean_entities_enabled:
            logging.warning("Please set clean_entities_enabled to True in global app config to clean all entities.")
            return False

        data_nodes = DataManager().get_all()

        # Clean all pickle files
        for data_node in data_nodes:
            if isinstance(data_node, PickleDataNode):
                if os.path.exists(data_node.path) and data_node.is_generated_file:
                    os.remove(data_node.path)

        # Clean all entities
        DataManager.delete_all()
        TaskManager.delete_all()
        PipelineManager.delete_all()
        ScenarioManager.delete_all()
        CycleManager.delete_all()
        JobManager.delete_all()
        return True

    @staticmethod
    def check_configuration() -> IssueCollector:
        """
        Checks configuration.

        Returns:
            IssueCollector: Collector containing the info, the warning and the error messages.
        """
        return Config.check()
