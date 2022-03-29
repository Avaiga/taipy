from datetime import datetime
from typing import Callable, Dict, List, Optional, Union

from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import CycleId, DataNodeId, JobId, PipelineId, ScenarioId, TaskId
from taipy.core.config.config import Config
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.cycle.cycle import Cycle
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.exceptions import ModelNotFound
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job
from taipy.core.pipeline._pipeline_manager import _PipelineManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task

__logger = _TaipyLogger._get_logger()


def set(entity: Union[DataNode, Task, Pipeline, Scenario, Cycle]):
    """
    Saves or updates the data node, task, job, pipeline, scenario or cycle given as parameter.

    Parameters:
        entity (Union[`DataNode^`, `Task^`, `Job^`, `Pipeline^`, `Scenario^`, `Cycle^`]): The entity to save.

    """
    if isinstance(entity, Cycle):
        return _CycleManager._set(entity)
    if isinstance(entity, Scenario):
        return _ScenarioManager._set(entity)
    if isinstance(entity, Pipeline):
        return _PipelineManager._set(entity)
    if isinstance(entity, Task):
        return _TaskManager._set(entity)
    if isinstance(entity, DataNode):
        return _DataManager._set(entity)


def submit(entity: Union[Scenario, Pipeline, Task], force: bool = False):
    """
    Submits the entity given as parameter for execution.

    All the tasks of the entity pipeline/scenario will be submitted for execution.

    Parameters:
        entity (Union[`Scenario^`, `Pipeline^`, `Task^`]): The entity to submit.
        force (bool): Force execution even if the data nodes are in cache.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManager._submit(entity, force=force)
    if isinstance(entity, Pipeline):
        return _PipelineManager._submit(entity, force=force)
    if isinstance(entity, Task):
        return _TaskManager._submit(entity, force=force)


def get(
    entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]
) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
    """
    Gets an entity given the identifier as parameter.

    Parameters:
        entity_id (Union[`TaskId^`, `DataNodeId^`, `PipelineId^`, `ScenarioId^`]): The identifier of the entity to get.
            It must match the identifier pattern of one of the entities (`Task^`, `DataNode^`, `Pipeline^`,
            `Scenario^`).
    Returns:
        Union[`Task^`, `DataNode^`, `Pipeline^`, `Scenario^`, `Job^`, `Cycle^`]: The entity matching  the corresponding
        id.None if no entity is found.
    Raises:
        `ModelNotFound^`: If _entity_id_ does not match a correct entity pattern.
    """
    if entity_id.startswith(_JobManager._ID_PREFIX):
        return _JobManager._get(JobId(entity_id))
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManager._get(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManager._get(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline._ID_PREFIX):
        return _PipelineManager._get(PipelineId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManager._get(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManager._get(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_tasks() -> List[Task]:
    """
    Returns the list of all existing tasks.

    Returns:
        List[`Task^`]: The list of tasks.
    """
    return _TaskManager._get_all()


def delete(entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]):
    """
    Deletes the entity given as parameter and the nested entities

    Deletes the entity given as parameter and propagate the deletion. The deletion is propagated to a
    nested entity if the nested entity is not shared by another entity.

    - If a `CycleId^` is provided, the nested scenarios, pipelines, data nodes, and jobs are deleted.
    - If a `ScenarioId^` is provided, the nested pipelines, tasks, data nodes, and jobs are deleted.
    - If a `PipelineId^` is provided, the nested tasks, data nodes, and jobs are deleted.
    - If a `TaskId^` is provided, the nested data nodes, and jobs are deleted.

    Parameters:
        entity_id (Union[`TaskId^`, `DataNodeId^`, `PipelineId^`, `ScenarioId^`, `JobId^`, `CycleId^`]): The id of the
            entity to delete.
    Raises:
        `ModelNotFound^`: No entity corresponds to entity_id
    """
    if entity_id.startswith(_JobManager._ID_PREFIX):
        return _JobManager._delete(_JobManager._get(JobId(entity_id)))  # type: ignore
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManager._hard_delete(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManager._hard_delete(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline._ID_PREFIX):
        return _PipelineManager._hard_delete(PipelineId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManager._hard_delete(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManager._delete(DataNodeId(entity_id))
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
        return _ScenarioManager._get_all()
    if cycle and not tag:
        return _ScenarioManager._get_all_by_cycle(cycle)
    if not cycle and tag:
        return _ScenarioManager._get_all_by_tag(tag)
    if cycle and tag:
        cycles_scenarios = _ScenarioManager._get_all_by_cycle(cycle)
        return [scenario for scenario in cycles_scenarios if scenario.has_tag(tag)]
    return []


def get_primary(cycle: Cycle) -> Optional[Scenario]:
    """
    Returns the primary scenario of the cycle given as parameter. None if the cycle has no primary scenario.

    Parameters:
         cycle (`Cycle`): The cycle of the primary scenario to return.
    Returns:
        Optional[`Scenario`]: The primary scenario of the cycle given as parameter. None if the cycle has no scenario.
    """
    return _ScenarioManager._get_primary(cycle)


def get_primary_scenarios() -> List[Scenario]:
    """
    Returns the list of all primary scenarios.

    Returns:
        List[Scenario]: The list of all primary scenarios.
    """
    return _ScenarioManager._get_primary_scenarios()


def set_primary(scenario: Scenario):
    """
    Promotes scenario `scenario` given as parameter as primary scenario of its cycle. If the cycle already had an
    primary scenario, it will be demoted, and it will no longer be primary for the cycle.

    Parameters:
        scenario (`Scenario`): The scenario to promote as primary.
    """
    return _ScenarioManager._set_primary(scenario)


def tag(scenario: Scenario, tag: str):
    """
    Adds the tag `tag` to the scenario `scenario` given as parameter. If the scenario's cycle already have
    another scenario tagged by `tag` the other scenario will be untagged.

    Parameters:
        scenario (`Scenario`): The scenario to tag.
        tag (str): The tag of the scenario to tag.
    """
    return _ScenarioManager._tag(scenario, tag)


def untag(scenario: Scenario, tag: str):
    """
    Removes tag `tag` given as parameter from the tag list of scenario `scenario` given as parameter.

    Parameters:
        scenario (`Scenario`): The scenario to untag.
        tag (str): The tag to remove from scenario.
    """
    return _ScenarioManager._untag(scenario, tag)


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
    return _ScenarioManager._compare(*scenarios, data_node_config_id=data_node_config_id)


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
    return _ScenarioManager._subscribe(callback, scenario)


def unsubscribe_scenario(callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
    """
    Unsubscribes a function that is called when the status of a Job changes.
    If scenario is not provided, the subscription is removed for all scenarios.

    Parameters:
        callback (Callable[[`Scenario`, `Job`], None]): The callable function to unsubscribe.
        scenario (Optional[`Scenario`]): The scenario to unsubscribe on. If None, the un-subscription is applied to all
            scenarios.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _ScenarioManager._unsubscribe(callback, scenario)


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
    return _PipelineManager._subscribe(callback, pipeline)


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
    return _PipelineManager._unsubscribe(callback, pipeline)


def get_pipelines() -> List[Pipeline]:
    """
    Returns all existing pipelines.

    Returns:
        List[`Pipeline`]: The list of all pipelines.
    """
    return _PipelineManager._get_all()


def get_jobs() -> List[Job]:
    """
    Returns all the existing jobs.

    Returns:
        List[`Job`]: The list of all jobs.
    """
    return _JobManager._get_all()


def delete_job(job: Job, force=False):
    """
    Deletes the job `job` given as parameter.

    Parameters:
        job (`Job`): The job to delete.
        force (bool): If `True`, forces the deletion of job `job`, even if it is not completed yet.
    Raises:
        `JobNotDeletedException`: If the job is not finished.
    """
    return _JobManager._delete(job, force)


def delete_jobs():
    """Deletes all jobs."""
    return _JobManager._delete_all()


def get_latest_job(task: Task) -> Optional[Job]:
    """
    Returns the latest job of the task `task`.

    Parameters:
        task (`Task`): The task to retrieve the latest job.
    Returns:
        Optional[`Job`]: The latest job created from task `task`. None if no job has been created from task `task`.
    """
    return _JobManager._get_latest(task)


def get_data_nodes() -> List[DataNode]:
    """
    Returns all the existing data nodes.

    Returns:
        List[`DataNode`]: The list of all data nodes.
    """
    return _DataManager._get_all()


def get_cycles() -> List[Cycle]:
    """
    Returns the list of all existing cycles.

    Returns:
        List[`Cycle`]: The list of all cycles.
    """
    return _CycleManager._get_all()


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
    return _ScenarioManager._create(config, creation_date, name)


def create_pipeline(config: PipelineConfig) -> Pipeline:
    """
    Creates and Returns a new pipeline from the pipeline configuration given as parameter.

    Parameters:
        config (`PipelineConfig`): The pipeline configuration.
    Returns:
        `Pipeline`: The new pipeline created.
    """
    return _PipelineManager._get_or_create(config)


def clean_all_entities() -> bool:
    """
    Deletes all entities from the taipy data folder. Recommended only for development purpose.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    if not Config.global_config.clean_entities_enabled:
        __logger.warning("Please set clean_entities_enabled to True to clean all entities.")
        return False

    _DataManager._delete_all()
    _TaskManager._delete_all()
    _PipelineManager._delete_all()
    _ScenarioManager._delete_all()
    _CycleManager._delete_all()
    _JobManager._delete_all()
    return True
