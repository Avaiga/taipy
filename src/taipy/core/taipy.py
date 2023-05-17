# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pathlib
import shutil
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Union, overload

from taipy.config.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ._entity._entity import _Entity
from ._version._version_manager_factory import _VersionManagerFactory
from .common._warnings import _warn_no_core_service
from .config.pipeline_config import PipelineConfig
from .config.scenario_config import ScenarioConfig
from .cycle._cycle_manager_factory import _CycleManagerFactory
from .cycle.cycle import Cycle
from .cycle.cycle_id import CycleId
from .data._data_manager_factory import _DataManagerFactory
from .data.data_node import DataNode
from .data.data_node_id import DataNodeId
from .exceptions.exceptions import ModelNotFound, NonExistingVersion, VersionIsNotProductionVersion
from .job._job_manager_factory import _JobManagerFactory
from .job.job import Job
from .job.job_id import JobId
from .pipeline._pipeline_manager_factory import _PipelineManagerFactory
from .pipeline.pipeline import Pipeline
from .pipeline.pipeline_id import PipelineId
from .scenario._scenario_manager_factory import _ScenarioManagerFactory
from .scenario.scenario import Scenario
from .scenario.scenario_id import ScenarioId
from .task._task_manager_factory import _TaskManagerFactory
from .task.task import Task
from .task.task_id import TaskId

__logger = _TaipyLogger._get_logger()


def set(entity: Union[DataNode, Task, Pipeline, Scenario, Cycle]):
    """Save or update an entity.

    Parameters:
        entity (Union[DataNode^, Task^, Job^, Pipeline^, Scenario^, Cycle^]): The
            entity to save.
    """
    if isinstance(entity, Cycle):
        return _CycleManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Pipeline):
        return _PipelineManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._set(entity)
    if isinstance(entity, DataNode):
        return _DataManagerFactory._build_manager()._set(entity)


@_warn_no_core_service()
def submit(
    entity: Union[Scenario, Pipeline, Task],
    force: bool = False,
    wait: bool = False,
    timeout: Optional[Union[float, int]] = None,
) -> Union[Job, List[Job]]:
    """Submit an entity for execution.

    If the entity is a pipeline or a scenario, all the tasks of the entity are
    submitted for execution.

    Parameters:
        entity (Union[Scenario^, Pipeline^, Task^]): The entity to submit.
        force (bool): If True, the execution is forced even if the data nodes are in cache.
        wait (bool): Wait for the orchestrated jobs created from the submission to be finished
            in asynchronous mode.
        timeout (Union[float, int]): The optional maximum number of seconds to wait
            for the jobs to be finished before returning.
    Returns:
        The created `Job^` or a collection of the created `Job^` depends on the submitted entity.

        - If a `Scenario^` or a `Pipeline^` is provided, it will return a list of `Job^`.
        - If a `Task^` is provided, it will return the created `Job^`.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)
    if isinstance(entity, Pipeline):
        return _PipelineManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)


@overload
def get(entity_id: TaskId) -> Task:
    ...


@overload
def get(entity_id: DataNodeId) -> DataNode:
    ...


@overload
def get(entity_id: PipelineId) -> Pipeline:
    ...


@overload
def get(entity_id: ScenarioId) -> Scenario:
    ...


@overload
def get(entity_id: CycleId) -> Cycle:
    ...


@overload
def get(entity_id: JobId) -> Job:
    ...


@overload
def get(entity_id: str) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
    ...


def get(
    entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId, str]
) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
    """Get an entity from its identifier.

    Parameters:
        entity_id (Union[TaskId^, DataNodeId^, PipelineId^, ScenarioId^]): The identifier
            of the entity to get.<br/>
            It must match the identifier pattern of one of the entities (`Task^`, `DataNode^`,
            `Pipeline^` or `Scenario^`).
    Returns:
        The entity matching the corresponding identifier. None if no entity is found.
    Raises:
        ModelNotFound^: If _entity_id_ does not match a correct entity pattern.
    """
    if entity_id.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._get(JobId(entity_id))
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._get(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._get(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline._ID_PREFIX):
        return _PipelineManagerFactory._build_manager()._get(PipelineId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._get(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._get(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_tasks() -> List[Task]:
    """Return the list of all existing tasks.

    Returns:
        The list of tasks.
    """
    return _TaskManagerFactory._build_manager()._get_all()


def delete(entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]):
    """Delete an entity and its nested entities.

    The given entity is deleted. The deletion is propagated to all nested entities that are
    not shared by another entity.

    - If a `CycleId^` is provided, the nested scenarios, pipelines, data nodes, and jobs are deleted.
    - If a `ScenarioId^` is provided, the nested pipelines, tasks, data nodes, and jobs are deleted.
    - If the scenario is primary, it can only be deleted if it is the only scenario in the cycle. In that case, its
        cycle is also deleted.
    - If a `PipelineId^` is provided, the nested tasks, data nodes, and jobs are deleted.
    - If a `TaskId^` is provided, the nested data nodes, and jobs are deleted.

    Parameters:
        entity_id (Union[TaskId^, DataNodeId^, PipelineId^, ScenarioId^, JobId^, CycleId^]): The
            identifier of the entity to delete.
    Raises:
        ModelNotFound^: No entity corresponds to _entity_id_.
    """
    if entity_id.startswith(Job._ID_PREFIX):
        job_manager = _JobManagerFactory._build_manager()
        return job_manager._delete(job_manager._get(JobId(entity_id)))  # type: ignore
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._hard_delete(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._hard_delete(ScenarioId(entity_id))
    if entity_id.startswith(Pipeline._ID_PREFIX):
        return _PipelineManagerFactory._build_manager()._hard_delete(PipelineId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._hard_delete(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._delete(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_scenarios(cycle: Optional[Cycle] = None, tag: Optional[str] = None) -> List[Scenario]:
    """Return the list of all existing scenarios filtered by a cycle or a tag.

    If both _cycle_ and _tag_ are provided, the returned list contains scenarios
    that belong to _cycle_ **and** that hold the tag _tag_.

    Parameters:
         cycle (Optional[Cycle^]): Cycle of the scenarios to return.
         tag (Optional[str]): Tag of the scenarios to return.
    Returns:
        The list of scenarios filtered by cycle or tag.
    """
    if not cycle and not tag:
        return _ScenarioManagerFactory._build_manager()._get_all()
    if cycle and not tag:
        return _ScenarioManagerFactory._build_manager()._get_all_by_cycle(cycle)
    if not cycle and tag:
        return _ScenarioManagerFactory._build_manager()._get_all_by_tag(tag)
    if cycle and tag:
        cycles_scenarios = _ScenarioManagerFactory._build_manager()()._get_all_by_cycle(cycle)
        return [scenario for scenario in cycles_scenarios if scenario.has_tag(tag)]
    return []


def get_primary(cycle: Cycle) -> Optional[Scenario]:
    """Return the primary scenario of a cycle.

    Parameters:
         cycle (Cycle^): The cycle of the primary scenario to return.
    Returns:
        The primary scenario of the cycle _cycle_. If the cycle has no
            primary scenario, this method returns None.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary(cycle)


def get_primary_scenarios() -> List[Scenario]:
    """Return the list of all primary scenarios.

    Returns:
        The list of all primary scenarios.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary_scenarios()


def set_primary(scenario: Scenario):
    """Promote a scenario as the primary scenario of its cycle.

    If the cycle of _scenario_ already has a primary scenario, it is demoted and
    is no longer the primary scenario for its cycle.

    Parameters:
        scenario (Scenario^): The scenario to promote as _primary_.
    """
    return _ScenarioManagerFactory._build_manager()._set_primary(scenario)


def tag(scenario: Scenario, tag: str):
    """Add a tag to a scenario.

    If the _scenario_'s cycle already has another scenario tagged with _tag_, then this other
    scenario is untagged.

    Parameters:
        scenario (Scenario^): The scenario to tag.
        tag (str): The tag to apply to the scenario.
    """
    return _ScenarioManagerFactory._build_manager()._tag(scenario, tag)


def untag(scenario: Scenario, tag: str):
    """Remove a tag from a scenario.

    Parameters:
        scenario (Scenario^): The scenario to remove the tag from.
        tag (str): The _tag_ to remove from _scenario_.
    """
    return _ScenarioManagerFactory._build_manager()._untag(scenario, tag)


def compare_scenarios(*scenarios: Scenario, data_node_config_id: Optional[str] = None) -> Dict[str, Any]:
    """Compare the data nodes of several scenarios.

    You can specify which data node config identifier should the comparison be performed
    on.

    Parameters:
        *scenarios (*Scenario^): The list of the scenarios to compare.
        data_node_config_id (Optional[str]): Config identifier of the DataNode to compare
            scenarios.<br/>
            if _datanode_config_id_ is None, the scenarios are compared based on all the defined
            comparators.
    Returns:
        The comparison results. The key is the data node config identifier that is compared.
    Raises:
        InsufficientScenarioToCompare^: Only one or no scenario for comparison is provided.
        NonExistingComparator^: The scenario comparator does not exist.
        DifferentScenarioConfigs^: _scenarios_ do not share the same scenario config.
        NonExistingScenarioConfig^: The scenario config of the provided scenarios could not
            be found.
    """
    return _ScenarioManagerFactory._build_manager()._compare(*scenarios, data_node_config_id=data_node_config_id)


def subscribe_scenario(
    callback: Callable[[Scenario, Job], None],
    params: Optional[List[Any]] = None,
    scenario: Optional[Scenario] = None,
):
    """Subscribe a function to be called on job status change.

    The subscription is applied to all jobs created for the execution of _scenario_.
    If no scenario is provided, the subscription applies to all scenarios.

    Parameters:
        callback (Callable[[Scenario^, Job^], None]): The function to be called on
            status change.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        scenario (Optional[Scenario^]): The scenario that subscribes to _callback_.
            If None, the subscription is registered for all scenarios.
    Note:
        Notifications are applied only for jobs created **after** this subscription.
    """
    params = [] if params is None else params
    return _ScenarioManagerFactory._build_manager()._subscribe(callback, params, scenario)


def unsubscribe_scenario(
    callback: Callable[[Scenario, Job], None], params: Optional[List[Any]] = None, scenario: Optional[Scenario] = None
):
    """Unsubscribe a function that is called when the status of a `Job^` changes.

    If _scenario_ is not provided, the subscription is removed for all scenarios.

    Parameters:
        callback (Callable[[Scenario^, Job^], None]): The function to unsubscribe to.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        scenario (Optional[Scenario^]): The scenario to unsubscribe to. If None, all scenarios
            unsubscribe to _callback_.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _ScenarioManagerFactory._build_manager()._unsubscribe(callback, params, scenario)


def subscribe_pipeline(
    callback: Callable[[Pipeline, Job], None], params: Optional[List[Any]] = None, pipeline: Optional[Pipeline] = None
):
    """Subscribe a function to be called on job status change.

    The subscription is applied to all jobs created for the execution of _pipeline_.

    Parameters:
        callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
            status change.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        pipeline (Optional[Pipeline^]): The pipeline to subscribe on. If None, the subscription
            is actived for all pipelines.
    Note:
        Notifications are applied only for jobs created **after** this subscription.
    """
    return _PipelineManagerFactory._build_manager()._subscribe(callback, params, pipeline)


def unsubscribe_pipeline(
    callback: Callable[[Pipeline, Job], None], params: Optional[List[Any]] = None, pipeline: Optional[Pipeline] = None
):
    """Unsubscribe a function that is called when the status of a Job changes.

    Parameters:
        callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
            status change.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        pipeline (Optional[Pipeline^]): The pipeline to unsubscribe to. If None, all pipelines
            unsubscribe to _callback_.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _PipelineManagerFactory._build_manager()._unsubscribe(callback, params, pipeline)


def get_pipelines() -> List[Pipeline]:
    """Return all existing pipelines.

    Returns:
        The list of all pipelines.
    """
    return _PipelineManagerFactory._build_manager()._get_all()


def get_jobs() -> List[Job]:
    """Return all the existing jobs.

    Returns:
        The list of all jobs.
    """
    return _JobManagerFactory._build_manager()._get_all()


def delete_job(job: Job, force=False):
    """Delete a job.

    Parameters:
        job (Job^): The job to delete.
        force (Optional[bool]): If True, forces the deletion of _job_, even if it is not
            completed yet.
    Raises:
        JobNotDeletedException^: If the job is not finished.
    """
    return _JobManagerFactory._build_manager()._delete(job, force)


def delete_jobs():
    """Delete all jobs."""
    return _JobManagerFactory._build_manager()._delete_all()


def cancel_job(job: Union[str, Job]):
    """Cancel a job and set the status of the subsequent jobs to ABANDONED.

    Parameters:
        job (Job^): The job to cancel.
    """
    _JobManagerFactory._build_manager()._cancel(job)


def get_latest_job(task: Task) -> Optional[Job]:
    """Return the latest job of a task.

    Parameters:
        task (Task^): The task to retrieve the latest job from.
    Returns:
        The latest job created from _task_. This is None if no job has been created from _task_.
    """
    return _JobManagerFactory._build_manager()._get_latest(task)


def get_data_nodes() -> List[DataNode]:
    """Return all the existing data nodes.

    Returns:
        The list of all data nodes.
    """
    return _DataManagerFactory._build_manager()._get_all()


def get_cycles() -> List[Cycle]:
    """Return the list of all existing cycles.

    Returns:
        The list of all cycles.
    """
    return _CycleManagerFactory._build_manager()._get_all()


def create_scenario(
    config: ScenarioConfig,
    creation_date: Optional[datetime] = None,
    name: Optional[str] = None,
) -> Scenario:
    """Create and return a new scenario from a scenario configuration.

    If the scenario belongs to a work cycle, a cycle (corresponding to the _creation_date_
    and the configuration frequency attribute) is created if it does not exist yet.

    Parameters:
        config (ScenarioConfig^): The scenario configuration.
        creation_date (Optional[datetime.datetime]): The creation date of the scenario.
            If None, the current date time is used.
        name (Optional[str]): The displayable name of the scenario.
    Returns:
        The new scenario.
    """
    return _ScenarioManagerFactory._build_manager()._create(config, creation_date, name)


def create_pipeline(config: PipelineConfig) -> Pipeline:
    """Create and return a new pipeline from a pipeline configuration.

    Parameters:
        config (PipelineConfig^): The pipeline configuration.
    Returns:
        The new pipeline.
    """
    return _PipelineManagerFactory._build_manager()._get_or_create(config)


def clean_all_entities() -> bool:
    """Delete all entities from the Taipy data folder.

    !!! important
        Invoking this function is only recommended for development purposes.

    Returns:
        True if the operation succeeded, False otherwise.
    """
    if not Config.global_config.clean_entities_enabled:
        __logger.warning("Please set 'clean_entities_enabled' to True to clean all entities.")
        return False

    _DataManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _ScenarioManagerFactory._build_manager()._delete_all()
    _CycleManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()
    _VersionManagerFactory._build_manager()._delete_all()
    return True


def clean_all_entities_by_version(version_number) -> bool:
    """Delete all entities belongs to a version from the Taipy data folder.

    Returns:
        True if the operation succeeded, False otherwise.
    """
    version_manager = _VersionManagerFactory._build_manager()
    try:
        version_number = version_manager._replace_version_number(version_number)
    except NonExistingVersion as e:
        __logger.warning(f"{e.message} Abort cleaning the entities of version '{version_number}'.")
        return False

    _JobManagerFactory._build_manager()._delete_by_version(version_number)
    _ScenarioManagerFactory._build_manager()._delete_by_version(version_number)
    _PipelineManagerFactory._build_manager()._delete_by_version(version_number)
    _TaskManagerFactory._build_manager()._delete_by_version(version_number)
    _DataManagerFactory._build_manager()._delete_by_version(version_number)

    version_manager._delete(version_number)
    try:
        version_manager._delete_production_version(version_number)
    except VersionIsNotProductionVersion:
        pass

    return True


def export_scenario(
    scenario_id: ScenarioId,
    folder_path: Union[str, pathlib.Path],
):
    """Export all related entities of a scenario to a folder.

    Parameters:
        scenario_id (ScenarioId): The id of the scenario to export.
        folder_path (Union[str, pathlib.Path]): The folder path to export the scenario to.
    """

    manager = _ScenarioManagerFactory._build_manager()
    scenario = manager._get(scenario_id)
    entity_ids = manager._get_children_entity_ids(scenario)  # type: ignore
    entity_ids.scenario_ids = {scenario_id}
    entity_ids.cycle_ids = {scenario.cycle.id}

    shutil.rmtree(folder_path, ignore_errors=True)

    for data_node_id in entity_ids.data_node_ids:
        _DataManagerFactory._build_manager()._export(data_node_id, folder_path)
    for task_id in entity_ids.task_ids:
        _TaskManagerFactory._build_manager()._export(task_id, folder_path)
    for pipeline_id in entity_ids.pipeline_ids:
        _PipelineManagerFactory._build_manager()._export(pipeline_id, folder_path)
    for cycle_id in entity_ids.cycle_ids:
        _CycleManagerFactory._build_manager()._export(cycle_id, folder_path)
    for scenario_id in entity_ids.scenario_ids:
        _ScenarioManagerFactory._build_manager()._export(scenario_id, folder_path)
    for job_id in entity_ids.job_ids:
        _JobManagerFactory._build_manager()._export(job_id, folder_path)


def get_parents(
    entity: Union[TaskId, DataNodeId, PipelineId, Task, DataNode, Pipeline], parent_dict=None
) -> Dict[str, Set[_Entity]]:
    """Get the parents of an entity from itself or its identifier.

    Parameters:
        entity (Union[TaskId^, DataNodeId^, PipelineId^, Task, DataNode, Pipeline]): The entity or its
            identifier to get the parents.<br/>
    Returns:
        The dictionary of all parent entities.
            They are grouped by their type (Scenario^, Pipelines^, or tasks^) so each key corresponds
            to a level of the parents and the value is a set of the parent entities.
            An empty dictionary is returned if the entity does not have parents.<br/>
            Example: The following instruction returns all the pipelines that include the
            datanode identified by "my_datanode_id".
            `taipy.get_parents("id_of_my_datanode")["pipelines"]`
    Raises:
        ModelNotFound^: If _entity_ does not match a correct entity pattern.
    """

    def update_parent_dict(parents_set, parent_dict, key):
        if key in parent_dict.keys():
            parent_dict[key].update(parents_set)
        else:
            parent_dict[key] = parents_set

    if isinstance(entity, str):
        entity = get(entity)  # type: ignore

    parent_dict = parent_dict or dict()

    if isinstance(entity, (Scenario, Cycle)):
        return parent_dict

    parents = {get(parent) for parent in entity.parent_ids}  # type: ignore

    if isinstance(entity, Pipeline):
        parent_entity_key = "scenarios"
        update_parent_dict(parents, parent_dict, parent_entity_key)

    if isinstance(entity, Task):
        parent_entity_key = "pipelines"
        update_parent_dict(parents, parent_dict, parent_entity_key)
        for parent in parent_dict[parent_entity_key]:
            get_parents(parent, parent_dict)

    if isinstance(entity, DataNode):
        parent_entity_key = "tasks"
        update_parent_dict(parents, parent_dict, parent_entity_key)
        for parent in parent_dict[parent_entity_key]:
            get_parents(parent, parent_dict)

    return parent_dict


def get_cycles_scenarios() -> Dict[Optional[Cycle], List[Scenario]]:
    """Get the scenarios grouped by cycles.

    Returns:
        The dictionary of all cycles and their corresponding scenarios.
    """

    cycles_scenarios: Dict[Optional[Cycle], List[Scenario]] = {}
    for scenario in get_scenarios():
        if scenario.cycle in cycles_scenarios.keys():
            cycles_scenarios[scenario.cycle].append(scenario)
        else:
            cycles_scenarios[scenario.cycle] = [scenario]
    return cycles_scenarios


def get_entities_by_config_id(
    config_id: str,
) -> Union[List, List[Task], List[DataNode], List[Pipeline], List[Scenario]]:
    """Get the entities by its cofig id.

    Parameters:
        config_id (str): The config id of the entities
    Returns:
        The list of all entities by the config id.
    """

    entities: List = []

    if entities := _ScenarioManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    if entities := _PipelineManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    if entities := _TaskManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    if entities := _DataManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    return entities
