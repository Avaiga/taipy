"""Main module."""
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.core.common._taipy_logger import _TaipyLogger
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
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_manager import ScenarioManager
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager

__logger = _TaipyLogger._get_logger()


def set(entity: Union[DataNode, Task, Pipeline, Scenario, Cycle]):
    """
    Saves or updates the data node, task, job, pipeline, scenario or cycle given as parameter.

    Parameters:
        entity (Union[`DataNode`, `Task`, `Pipeline`, `Scenario`, `Cycle`]): The entity to save.

    """
    if isinstance(entity, Cycle):
        return CycleManager._set(entity)
    if isinstance(entity, Scenario):
        return ScenarioManager._set(entity)
    if isinstance(entity, Pipeline):
        return PipelineManager._set(entity)
    if isinstance(entity, Task):
        return TaskManager._set(entity)
    if isinstance(entity, DataNode):
        return DataManager._set(entity)


def submit(entity: Union[Scenario, Pipeline], force: bool = False):
    """
    Submits the entity given as parameter for execution.

    All the tasks of the entity pipeline/scenario will be submitted for execution.

    Parameters:
        entity (Union[`Scenario`, `Pipeline`]): The entity to submit.
        force (bool): Force execution even if the data nodes are in cache.
    """
    if isinstance(entity, Scenario):
        return ScenarioManager.submit(entity, force=force)
    if isinstance(entity, Pipeline):
        return PipelineManager.submit(entity, force=force)


def get(
    entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]
) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
    """
    Gets an entity given the identifier as parameter.

    Parameters:
        entity_id (Union[`TaskId`, `DataNodeId`, `PipelineId`, `ScenarioId`]): The identifier of the entity to get.
            It must match the identifier pattern of one of the entities (task, data node, pipeline, scenario).
    Returns:
        Union[`Task`, `DataNode`, `Pipeline`, `Scenario`, `Job`, `Cycle`]: The entity matching  the corresponding id.
        None if no entity is found.
    Raises:
        `ModelNotFound`: If `entity_id` does not match a correct entity id pattern.
    """
    if entity_id.startswith(JobManager.ID_PREFIX):
        return JobManager._get(JobId(entity_id))
    if entity_id.startswith(Cycle.ID_PREFIX):
        return CycleManager._get(CycleId(entity_id))
    if entity_id.startswith(Scenario.ID_PREFIX):
        return ScenarioManager._get(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline.ID_PREFIX):
        return PipelineManager._get(PipelineId(entity_id))
    if entity_id.startswith(Task.ID_PREFIX):
        return TaskManager._get(TaskId(entity_id))
    if entity_id.startswith(DataNode.ID_PREFIX):
        return DataManager._get(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_tasks() -> List[Task]:
    """
    Returns the list of all existing tasks.

    Returns:
        List[`Task`]: The list of tasks.
    """
    return TaskManager._get_all()


def delete(entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]):
    """
    Deletes the entity given as parameter and the nested entities

    Deletes the entity given as parameter and propagate the deletion. The deletion is propagated to a
    nested entity if the nested entity is not shared by another entity.

    - If a `CycleId` is provided, the nested scenarios, pipelines, data nodes, and jobs are deleted.
    - If a `ScenarioId` is provided, the nested pipelines, tasks, data nodes, and jobs are deleted.
    - If a `PipelineId` is provided, the nested tasks, data nodes, and jobs are deleted.
    - If a `TaskId` is provided, the nested data nodes, and jobs are deleted.

    Parameters:
        entity_id (Union[`TaskId`, `DataNodeId`, `PipelineId`, `ScenarioId`, `JobId`, `CycleId`]): The id of the entity
            to delete.
    Raises:
        `ModelNotFound`: No entity corresponds to entity_id
    """
    if entity_id.startswith(JobManager.ID_PREFIX):
        return JobManager._delete(JobManager._get(JobId(entity_id)))  # type: ignore
    if entity_id.startswith(Cycle.ID_PREFIX):
        return CycleManager._delete(CycleId(entity_id))
    if entity_id.startswith(Scenario.ID_PREFIX):
        return ScenarioManager.hard_delete(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline.ID_PREFIX):
        return PipelineManager.hard_delete(PipelineId(entity_id))
    if entity_id.startswith(Task.ID_PREFIX):
        return TaskManager.hard_delete(TaskId(entity_id))
    if entity_id.startswith(DataNode.ID_PREFIX):
        return DataManager._delete(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_scenarios(cycle: Optional[Cycle] = None, tag: Optional[str] = None) -> List[Scenario]:
    """
    Returns the list of all existing scenarios filtered by cycle and/or tag if given as parameter.

    Parameters:
         cycle (Optional[`Cycle`]): Cycle of the scenarios to return.
         tag (Optional[str]): Tag of the scenarios to return.
    Returns:
        List[`Scenario`]: The list of scenarios filtered by cycle or tag if given as parameter.
    """
    if not cycle and not tag:
        return ScenarioManager._get_all()
    if cycle and not tag:
        return ScenarioManager.get_all_by_cycle(cycle)
    if not cycle and tag:
        return ScenarioManager.get_all_by_tag(tag)
    if cycle and tag:
        cycles_scenarios = ScenarioManager.get_all_by_cycle(cycle)
        return [scenario for scenario in cycles_scenarios if scenario.has_tag(tag)]
    return []


def get_master(cycle: Cycle) -> Optional[Scenario]:
    """
    Returns the master scenario of the cycle given as parameter. None if the cycle has no master scenario.

    Parameters:
         cycle (`Cycle`): The cycle of the master scenario to return.
    Returns:
        Optional[`Scenario`]: The master scenario of the cycle given as parameter. None if the cycle has no scenario.
    """
    return ScenarioManager.get_master(cycle)


def get_all_masters() -> List[Scenario]:
    """
    Returns the list of all master scenarios.

    Returns:
        List[Scenario]: The list of all master scenarios.
    """
    return ScenarioManager.get_all_masters()


def set_master(scenario: Scenario):
    """
    Promotes scenario `scenario` given as parameter as master scenario of its cycle. If the cycle already had a
    master scenario, it will be demoted, and it will no longer be master for the cycle.

    Parameters:
        scenario (`Scenario`): The scenario to promote as master.
    """
    return ScenarioManager.set_master(scenario)


def tag(scenario: Scenario, tag: str):
    """
    Adds the tag `tag` to the scenario `scenario` given as parameter. If the scenario's cycle already have
    another scenario tagged by `tag` the other scenario will be untagged.

    Parameters:
        scenario (`Scenario`): The scenario to tag.
        tag (str): The tag of the scenario to tag.
    """
    return ScenarioManager.tag(scenario, tag)


def untag(scenario: Scenario, tag: str):
    """
    Removes tag `tag` given as parameter from the tag list of scenario `scenario` given as parameter.

    Parameters:
        scenario (`Scenario`): The scenario to untag.
        tag (str): The tag to remove from scenario.
    """
    return ScenarioManager.untag(scenario, tag)


def compare_scenarios(*scenarios: Scenario, data_node_config_id: Optional[str] = None):
    """
    Compares the data nodes of given scenarios 'scenarios' with known datanode config id.

    Parameters:
        scenarios (*`Scenario`): A variable length argument list. List of scenarios to compare.
        data_node_config_id (Optional[str]): Config id of the DataNode to compare scenarios, if no
            datanode_config_id is provided, the scenarios will be compared based on all the defined
            comparators.
    Returns:
        Dict[str, Any]: The dictionary of comparison results. The key corresponds to the data node config id compared.
    Raises:
        `InsufficientScenarioToCompare`: Provided only one or no scenario for comparison.
        `NonExistingComparator`: The scenario comparator does not exist.
        `DifferentScenarioConfigs`: The provided scenarios do not share the same scenario_config.
        `NonExistingScenarioConfig`: Cannot find the shared scenario config of the provided scenarios.
    """
    return ScenarioManager.compare(*scenarios, data_node_config_id=data_node_config_id)


def subscribe_scenario(callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
    """
    Subscribes a function to be called on job status change. The subscription is applied to all jobs
    created from the execution `scenario`. If no scenario is provided, the subscription concerns
    all scenarios.

    Parameters:
        callback (Callable[[`Scenario`, `Job`], None]): The callable function to be called on status change.
        scenario (Optional[`Scenario`]): The scenario to subscribe on. If None, the subscription is active for all
            scenarios.
    Note:
        Notification will be available only for jobs created after this subscription.
    """
    return ScenarioManager.subscribe(callback, scenario)


def unsubscribe_scenario(callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
    """
    Unsubscribes a function that is called when the status of a Job changes.
    If scenario is not passed, the subscription is removed for all scenarios.

    Parameters:
        callback (Callable[[`Scenario`, `Job`], None]): The callable function to unsubscribe.
        scenario (Optional[`Scenario`]): The scenario to unsubscribe on. If None, the un-subscription is applied to all
            scenarios.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return ScenarioManager.unsubscribe(callback, scenario)


def subscribe_pipeline(callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
    """
    Subscribes a function to be called on job status change. The subscription is applied to all jobs
    created from the execution of `pipeline`. If no pipeline is provided, the subscription concerns
    all pipelines. If pipeline is not passed, the subscription concerns all pipelines.

    Parameters:
        callback (Callable[[`Pipeline`, `Job`], None]): The callable function to be called on status change.
        pipeline (Optional[`Pipeline`]): The pipeline to subscribe on. If None, the subscription is active for all
            pipelines.
    Note:
        Notification will be available only for jobs created after this subscription.
    """
    return PipelineManager.subscribe(callback, pipeline)


def unsubscribe_pipeline(callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
    """
    Unsubscribes a function that is called when the status of a Job changes.
    If pipeline is not passed, the subscription is removed to all pipelines.

    Parameters:
        callback (Callable[[`Pipeline`, `Job`], None]): The callable function to be called on status change.
        pipeline (Optional[`Pipeline`]): The pipeline to unsubscribe on. If None, the un-subscription is applied to all
            pipelines.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return PipelineManager.unsubscribe(callback, pipeline)


def get_pipelines() -> List[Pipeline]:
    """
    Returns all existing pipelines.

    Returns:
        List[`Pipeline`]: The list of all pipelines.
    """
    return PipelineManager._get_all()


def get_jobs() -> List[Job]:
    """
    Returns all the existing jobs.

    Returns:
        List[`Job`]: The list of all jobs.
    """
    return JobManager._get_all()


def delete_job(job: Job, force=False):
    """
    Deletes the job `job` given as parameter.

    Parameters:
        job (`Job`): The job to delete.
        force (bool): If `True`, forces the deletion of job `job`, even if it is not completed yet.
    Raises:
        `JobNotDeletedException`: If the job is not finished.
    """
    return JobManager._delete(job, force)


def delete_jobs():
    """Deletes all jobs."""
    return JobManager._delete_all()


def get_latest_job(task: Task) -> Optional[Job]:
    """
    Returns the latest job of the task `task`.

    Parameters:
        task (`Task`): The task to retrieve the latest job.
    Returns:
        Optional[`Job`]: The latest job created from task `task`. None if no job has been created from task `task`.
    """
    return JobManager.get_latest(task)


def get_data_nodes() -> List[DataNode]:
    """
    Returns all the existing data nodes.

    Returns:
        List[`DataNode`]: The list of all data nodes.
    """
    return DataManager._get_all()


def get_cycles() -> List[Cycle]:
    """
    Returns the list of all existing cycles.

    Returns:
        List[`Cycle`]: The list of all cycles.
    """
    return CycleManager._get_all()


def create_scenario(
    config: ScenarioConfig, creation_date: Optional[datetime] = None, name: Optional[str] = None
) -> Scenario:
    """
    Creates and returns a new scenario from the scenario configuration `config` provided as parameter.

    If the scenario belongs to a work cycle, the cycle (corresponding to the creation_date and the configuration
    frequency attribute) is created if it does not exist yet.

    Parameters:
        config (`ScenarioConfig`): Scenario configuration object.
        creation_date (Optional[datetime.datetime]): The creation date of the scenario.
            Current date time used as default value.
        name (Optional[str]): The displayable name of the scenario.
    Returns:
        `Scenario`: The new scenario created.
    """
    return ScenarioManager.create(config, creation_date, name)


def create_pipeline(config: PipelineConfig) -> Pipeline:
    """
    Creates and Returns a new pipeline from the pipeline configuration given as parameter.

    Parameters:
        config (`PipelineConfig`): The pipeline configuration.
    Returns:
        `Pipeline`: The new pipeline created.
    """
    return PipelineManager.get_or_create(config)


def load_configuration(filename):
    """
    Loads a toml file configuration located at the `filename` path given as parameter.

    Parameters:
        filename (str or Path): The path of the toml configuration file to load.
    """
    __logger.info(f"Loading configuration. Filename: '{filename}'")
    cfg = Config._load(filename)
    __logger.info(f"Configuration '{filename}' successfully loaded.")
    return cfg


def export_configuration(filename):
    """
    Exports the configuration to a toml file.

    The configuration exported is a compilation from the three possible methods to configure the application:
    The python code configuration, the file configuration and the environment
    configuration.

    Parameters:
        filename (str or Path): The path of the file to export.
    Note:
        It overwrites the file if it already exists.
    """
    return Config._export(filename)


def configure_global_app(
    root_folder: str = None,
    storage_folder: str = None,
    clean_entities_enabled: Union[bool, str] = None,
    **properties,
) -> GlobalAppConfig:
    """
    Configures global application.

    Parameters:
        root_folder (Optional[str]): The path of the base folder for the taipy application.
        storage_folder (Optional[str]): The folder name used to store Taipy data.
            It is used in conjunction with the root_folder field. That means the storage path is
            "<root_folder><storage_folder>".
        clean_entities_enabled (Optional[str]): The field to activate/deactivate the clean entities feature.
            The default value is false.
    Returns:
        `GlobalAppConfig`: The global application configuration.
    """
    return Config._set_global_config(root_folder, storage_folder, clean_entities_enabled, **properties)


def configure_job_executions(mode: str = None, nb_of_workers: Union[int, str] = None, **properties) -> JobConfig:
    """
    Configures job execution.

    Parameters:
        mode (Optional[str]): The job execution mode.
            Possible values are: `standalone` (default value), or `airflow` (Enterprise version only).
        nb_of_workers (Optional[int, str]): The maximum number of jobs able to run in parallel. Default value: 1.
            A string can be provided as parameter to dynamically set the value using an environment variable.
            The string must follow the pattern: `ENV[<env_var>]` where `<env_var>` is an environment variable name.
    Returns:
        `JobConfig`: The job execution configuration.
    """
    return Config._set_job_config(mode, nb_of_workers, **properties)


def configure_data_node(
    id: str, storage_type: str = "pickle", scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
) -> DataNodeConfig:
    """
    Configures a new data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        storage_type (str): The data node configuration storage type. The possible values are "pickle"
            (default value), "csv", "excel", "sql". "in_memory", "generic".
        scope (`Scope`): The scope of the data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new data node configuration.
    """
    return Config._add_data_node(id, storage_type, scope, **properties)


def configure_default_data_node(
    storage_type: str = "pickle", scope=DataNodeConfig._DEFAULT_SCOPE, **properties
) -> DataNodeConfig:
    """
    Configures the default values of the data node configurations.

    Parameters:
        storage_type (str): The default storage type of the data node configurations. The possible values are "pickle"
            (default value), "csv", "excel", "sql". "in_memory", "generic".
        scope (`Scope`): The default scope of the data node configurations. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The default data node configuration.
    """
    return Config._add_default_data_node(storage_type, scope, **properties)


def configure_csv_data_node(id: str, path: str, has_header=True, scope=DataNodeConfig._DEFAULT_SCOPE, **properties):
    """
    Configures a new CSV data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        path (str): The path of the CSV file.
        has_header (bool): The parameter to define if the CSV file has a header or not.
        scope (`Scope`): The scope of the CSV data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new CSV data node configuration.
    """
    return Config._add_data_node(
        id, CSVDataNode.storage_type(), scope=scope, path=path, has_header=has_header, **properties
    )


def configure_excel_data_node(
    id: str,
    path: str,
    has_header: bool = True,
    sheet_name: Union[List[str], str] = "Sheet1",
    scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
    **properties,
):
    """
    Configures a new Excel data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        path (str): The path of the Excel file.
        has_header (bool): The parameter to define if the Excel file has a header or not.
        sheet_name (str): The sheet names.
        scope (`Scope`): The scope of the Excel data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new CSV data node configuration.
    """
    return Config._add_data_node(
        id,
        ExcelDataNode.storage_type(),
        scope=scope,
        path=path,
        has_header=has_header,
        sheet_name=sheet_name,
        **properties,
    )


def configure_generic_data_node(
    id: str,
    read_fct: Callable = None,
    write_fct: Callable = None,
    scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
    **properties,
):
    """
    Configures a new Generic data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        read_fct (Callable): The python function called by Taipy to read the data.
        write_fct (Callable): The python function called by Taipy to write the data.
        scope (`Scope`): The scope of the Generic data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new Generic data node configuration.
    """
    return Config._add_data_node(
        id, GenericDataNode.storage_type(), scope=scope, read_fct=read_fct, write_fct=write_fct, **properties
    )


def configure_in_memory_data_node(
    id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
):
    """
    Configures a new in_memory data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        default_data (Optional[Any]): The default data of the data nodes instantiated from the in_memory data node
            configuration.
        scope (`Scope`): The scope of the in_memory data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new in_memory data node configuration.
    """
    return Config._add_data_node(
        id, InMemoryDataNode.storage_type(), scope=scope, default_data=default_data, **properties
    )


def configure_pickle_data_node(
    id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
):
    """
    Configures a new pickle data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        default_data (Optional[Any]): The default data of the data nodes instantiated from the pickle data node
            configuration.
        scope (`Scope`): The scope of the pickle data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new pickle data node configuration.
    """
    return Config._add_data_node(
        id, PickleDataNode.storage_type(), scope=scope, default_data=default_data, **properties
    )


def configure_sql_data_node(
    id: str,
    db_username: str,
    db_password: str,
    db_name: str,
    db_engine: str,
    read_query: str,
    write_table: str,
    db_port: int = 143,
    scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
    **properties,
):
    """
    Configures a new SQL data node configuration.

    Parameters:
        id (str): The unique identifier of the data node configuration.
        db_username (str): The database username.
        db_password (str): The database password.
        db_name (str): The database name.
        db_engine (str): The database engine. Possible values are 'sqlite' or 'mssql'.
        read_query (str): The SQL query called by Taipy to read the data from the database.
        write_table (str): The name of the table in the database to write the data to.
        db_port (int): The database port. The default value is 143.
        scope (`Scope`): The scope of the SQL data node configuration. The default value is Scope.SCENARIO.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `DataNodeConfig`: The new SQL data node configuration.
    """
    return Config._add_data_node(
        id,
        SQLDataNode.storage_type(),
        scope=scope,
        db_username=db_username,
        db_password=db_password,
        db_name=db_name,
        db_engine=db_engine,
        read_query=read_query,
        write_table=write_table,
        db_port=db_port,
        **properties,
    )


def configure_task(
    id: str,
    function,
    input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
    output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
    **properties,
) -> TaskConfig:
    """
    Configures a new task configuration.

    Parameters:
        id (str): The unique identifier of the task configuration.
        function (Callable): The python function called by Taipy to run the task.
        input (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function inputs as data node
            configurations.
        output (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function outputs as data node
            configurations.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `TaskConfig`: The new task configuration.
    """
    return Config._add_task(id, function, input, output, **properties)


def configure_default_task(
    function,
    input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
    output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
    **properties,
) -> TaskConfig:
    """
    Configures the default values of the task configurations.

    Parameters:
        function (Callable): The python function called by Taipy to run the task.
        input (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function inputs as data node
            configurations.
        output (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function outputs as data node
            configurations.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `TaskConfig`: The default task configuration.
    """
    return Config._add_default_task(function, input, output, **properties)


def configure_pipeline(id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties) -> PipelineConfig:
    """
    Configures a new pipeline configuration.

    Parameters:
        id (str): The unique identifier of the pipeline configuration.
        task_configs (Callable): The list of the task configurations.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `PipelineConfig`: The new pipeline configuration.
    """
    return Config._add_pipeline(id, task_configs, **properties)


def configure_default_pipeline(task_configs: Union[TaskConfig, List[TaskConfig]], **properties) -> PipelineConfig:
    """
    Configures the default values of the pipeline configurations.

    Parameters:
        task_configs (Callable): The list of the task configurations.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `PipelineConfig`: The default pipeline configuration.
    """
    return Config._add_default_pipeline(task_configs, **properties)


def configure_scenario(
    id: str,
    pipeline_configs: List[PipelineConfig],
    frequency: Optional[Frequency] = None,
    comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
    **properties,
) -> ScenarioConfig:
    """
    Configures a new scenario configuration.

    Parameters:
        id (str): The unique identifier of the scenario configuration.
        pipeline_configs (Callable): The list of the pipeline configurations.
        frequency (Optional[`Frequency`]): The scenario frequency.
            It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
            frequency each scenario will be attached to the right cycle.
        comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
            scenarios. A comparator function is attached to a scenario's data node configuration. The key of
            the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
            each comparator is applied to all the data nodes instantiated from the data node configuration attached
            to the comparator.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `ScenarioConfig`: The new scenario configuration.
    """
    return Config._add_scenario(id, pipeline_configs, frequency, comparators, **properties)


def configure_scenario_from_tasks(
    id: str,
    task_configs: List[TaskConfig],
    frequency: Optional[Frequency] = None,
    comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
    pipeline_id: Optional[str] = None,
    **properties,
) -> ScenarioConfig:
    """
    Configures a new scenario configuration made of a single new pipeline configuration. A new pipeline configuration is
    created as well. If no pipeline_id is provided, it will be the scenario configuration id post-fixed by '_pipeline'.

    Parameters:
        id (str): The unique identifier of the scenario configuration.
        task_configs (Callable): The list of the task configurations.
        frequency (Optional[`Frequency`]): The scenario frequency.
            It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
            frequency each scenario will be attached to the right cycle.
        comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
            scenarios. A comparator function is attached to a scenario's data node configuration. The key of
            the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
            each comparator is applied to all the data nodes instantiated from the data node configuration attached
            to the comparator.
        pipeline_id (str): The id of the pipeline configuration to be configured.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `ScenarioConfig`: The new scenario configuration.
    """
    return Config._add_scenario_from_tasks(id, task_configs, frequency, comparators, pipeline_id, **properties)


def configure_default_scenario(
    pipeline_configs: List[PipelineConfig],
    frequency: Optional[Frequency] = None,
    comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
    **properties,
) -> ScenarioConfig:
    """
    Configures the default values of the scenario configurations.

    Parameters:
        pipeline_configs (Callable): The list of the pipeline configurations.
        frequency (Optional[`Frequency`]): The scenario frequency.
            It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
            frequency each scenario will be attached to the right cycle.
        comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
            scenarios. A comparator function is attached to a scenario's data node configuration. The key of
            the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
            each comparator is applied to all the data nodes instantiated from the data node configuration attached
            to the comparator.
        **properties (Dict[str, Any]): The variable length keyword arguments.
    Returns:
        `ScenarioConfig`: The default scenario configuration.
    """
    return Config._add_default_scenario(pipeline_configs, frequency, comparators, **properties)


def clean_all_entities() -> bool:
    """
    Deletes all entities from the taipy data folder. Recommended only for development purpose.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    if not Config.global_config.clean_entities_enabled:
        __logger.warning("Please set clean_entities_enabled to True in global app config to clean all entities.")
        return False

    data_nodes = DataManager._get_all()

    # Clean all pickle files
    for data_node in data_nodes:
        if isinstance(data_node, PickleDataNode):
            if os.path.exists(data_node.path) and data_node.is_generated_file:
                os.remove(data_node.path)

    # Clean all entities
    DataManager._delete_all()
    TaskManager._delete_all()
    PipelineManager._delete_all()
    ScenarioManager._delete_all()
    CycleManager._delete_all()
    JobManager._delete_all()
    return True


def check_configuration() -> IssueCollector:
    """
    Checks configuration, logs issue messages and returns an issue collector.

    Returns:
        `IssueCollector`: Collector containing the info, the warning and the error issues.
    """
    return Config._check()
