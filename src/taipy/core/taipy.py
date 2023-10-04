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

from taipy.config.common.scope import Scope
from taipy.logger._taipy_logger import _TaipyLogger

from ._entity._entity import _Entity
from ._version._version_manager_factory import _VersionManagerFactory
from .common._warnings import _warn_no_core_service
from .config.data_node_config import DataNodeConfig
from .config.scenario_config import ScenarioConfig
from .cycle._cycle_manager_factory import _CycleManagerFactory
from .cycle.cycle import Cycle
from .cycle.cycle_id import CycleId
from .data._data_manager_factory import _DataManagerFactory
from .data.data_node import DataNode
from .data.data_node_id import DataNodeId
from .exceptions.exceptions import (
    DataNodeConfigIsNotGlobal,
    ModelNotFound,
    NonExistingVersion,
    VersionIsNotProductionVersion,
)
from .job._job_manager_factory import _JobManagerFactory
from .job.job import Job
from .job.job_id import JobId
from .scenario._scenario_manager_factory import _ScenarioManagerFactory
from .scenario.scenario import Scenario
from .scenario.scenario_id import ScenarioId
from .sequence._sequence_manager_factory import _SequenceManagerFactory
from .sequence.sequence import Sequence
from .sequence.sequence_id import SequenceId
from .task._task_manager_factory import _TaskManagerFactory
from .task.task import Task
from .task.task_id import TaskId

__logger = _TaipyLogger._get_logger()


def set(entity: Union[DataNode, Task, Sequence, Scenario, Cycle]):
    """Save or update an entity.

    This function allows you to save or update an entity in Taipy.

    Parameters:
        entity (Union[DataNode^, Task^, Sequence^, Scenario^, Cycle^]): The
            entity to save or update.
    """
    if isinstance(entity, Cycle):
        return _CycleManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._set(entity)
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._set(entity)
    if isinstance(entity, DataNode):
        return _DataManagerFactory._build_manager()._set(entity)


def is_submittable(entity: Union[Scenario, ScenarioId, Sequence, SequenceId, Task, TaskId]) -> bool:
    """Indicate if an entity can be submitted.

    This function checks if the given entity can be submitted for execution.

    Returns:
        True if the given entity can be submitted. False otherwise.
    """
    if isinstance(entity, Scenario) or (isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX)):
        return _ScenarioManagerFactory._build_manager()._is_submittable(entity)  # type: ignore
    if isinstance(entity, Sequence) or (isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX)):
        return _SequenceManagerFactory._build_manager()._is_submittable(entity)  # type: ignore
    if isinstance(entity, Task) or (isinstance(entity, str) and entity.startswith(Task._ID_PREFIX)):
        return _TaskManagerFactory._build_manager()._is_submittable(entity)  # type: ignore
    return False


def is_editable(
    entity: Union[
        DataNode, Task, Job, Sequence, Scenario, Cycle, DataNodeId, TaskId, JobId, SequenceId, ScenarioId, CycleId
    ]
) -> bool:

    """Indicate if an entity can be edited.

    This function checks if the given entity can be edited.

    Returns:
        True if the given entity can be edited. False otherwise.
    """
    if isinstance(entity, Cycle) or (isinstance(entity, str) and entity.startswith(Cycle._ID_PREFIX)):
        return _CycleManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    if isinstance(entity, Scenario) or (isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX)):
        return _ScenarioManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    if isinstance(entity, Sequence) or (isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX)):
        return _SequenceManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    if isinstance(entity, Task) or (isinstance(entity, str) and entity.startswith(Task._ID_PREFIX)):
        return _TaskManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    if isinstance(entity, Job) or (isinstance(entity, str) and entity.startswith(Job._ID_PREFIX)):
        return _JobManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    if isinstance(entity, DataNode) or (isinstance(entity, str) and entity.startswith(DataNode._ID_PREFIX)):
        return _DataManagerFactory._build_manager()._is_editable(entity)  # type: ignore
    return False


def is_readable(
    entity: Union[
        DataNode, Task, Job, Sequence, Scenario, Cycle, DataNodeId, TaskId, JobId, SequenceId, ScenarioId, CycleId
    ]
) -> bool:

    """Indicate if an entity can be read.

    This function checks if the given entity can be read.

    Returns:
        True if the given entity can be read. False otherwise.
    """
    if isinstance(entity, Cycle) or (isinstance(entity, str) and entity.startswith(Cycle._ID_PREFIX)):
        return _CycleManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    if isinstance(entity, Scenario) or (isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX)):
        return _ScenarioManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    if isinstance(entity, Sequence) or (isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX)):
        return _SequenceManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    if isinstance(entity, Task) or (isinstance(entity, str) and entity.startswith(Task._ID_PREFIX)):
        return _TaskManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    if isinstance(entity, Job) or (isinstance(entity, str) and entity.startswith(Job._ID_PREFIX)):
        return _JobManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    if isinstance(entity, DataNode) or (isinstance(entity, str) and entity.startswith(DataNode._ID_PREFIX)):
        return _DataManagerFactory._build_manager()._is_readable(entity)  # type: ignore
    return False


@_warn_no_core_service()
def submit(
    entity: Union[Scenario, Sequence, Task],
    force: bool = False,
    wait: bool = False,
    timeout: Optional[Union[float, int]] = None,
) -> Union[Job, List[Job]]:
    """Submit a scenario, sequence or task entity for execution.

    This function submits the given entity for execution and returns the created job(s).

    If the entity is a sequence or a scenario, all the tasks of the entity are
    submitted for execution.

    Parameters:
        entity (Union[Scenario^, Sequence^, Task^]): The scenario, sequence or task to submit.
        force (bool): If True, the execution is forced even if for skippable tasks.
        wait (bool): Wait for the orchestrated jobs created from the submission to be finished
            in asynchronous mode.
        timeout (Union[float, int]): The optional maximum number of seconds to wait
            for the jobs to be finished before returning.

    Returns:
        The created `Job^` or a collection of the created `Job^` depends on the submitted entity.

            - If a `Scenario^` or a `Sequence^` is provided, it will return a list of `Job^`.
            - If a `Task^` is provided, it will return the created `Job^`.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._submit(entity, force=force, wait=wait, timeout=timeout)


@overload
def exists(entity_id: TaskId) -> bool:
    ...


@overload
def exists(entity_id: DataNodeId) -> bool:
    ...


@overload
def exists(entity_id: SequenceId) -> bool:
    ...


@overload
def exists(entity_id: ScenarioId) -> bool:
    ...


@overload
def exists(entity_id: CycleId) -> bool:
    ...


@overload
def exists(entity_id: JobId) -> bool:
    ...


@overload
def exists(entity_id: str) -> bool:
    ...


def exists(entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, str]) -> bool:
    """Check if an entity with the specified identifier exists.

    This function checks if an entity with the given identifier exists.
    It supports various types of entity identifiers, including `TaskId^`,
    `DataNodeId^`, `SequenceId^`, `ScenarioId^`, `JobId^`, `CycleId^`, and string
    representations.

    Parameters:
        entity_id (Union[DataNodeId^, TaskId^, SequenceId^, ScenarioId^, JobId^, CycleId^]): The
            identifier of the entity to check for existence.

    Returns:
        True if the given entity exists. False otherwise.

    Raises:
        ModelNotFound: If the entity's type cannot be determined.

    Note:
        The function performs checks for various entity types
        (`Job^`, `Cycle^`, `Scenario^`, `Sequence^`, `Task^`, `DataNode^`)
        based on their respective identifier prefixes.
    """
    if entity_id.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._exists(JobId(entity_id))
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._exists(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._exists(ScenarioId(entity_id))
    if entity_id.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._exists(SequenceId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._exists(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._exists(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


@overload
def get(entity_id: TaskId) -> Task:
    ...


@overload
def get(entity_id: DataNodeId) -> DataNode:
    ...


@overload
def get(entity_id: SequenceId) -> Sequence:
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
def get(entity_id: str) -> Union[Task, DataNode, Sequence, Scenario, Job, Cycle]:
    ...


def get(
    entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, str]
) -> Union[Task, DataNode, Sequence, Scenario, Job, Cycle]:
    """Retrieve an entity by its unique identifier.

    This function allows you to retrieve an entity by specifying its identifier.
    The identifier must match the pattern of one of the supported entity types:
    Task^, DataNode^, Sequence^, Job^, Cycle^, or Scenario^.


    Parameters:
        entity_id (Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, str]):
            The identifier of the entity to retrieve.<br/>
            It should conform to the identifier pattern of one of the entities (`Task^`, `DataNode^`,
            `Sequence^`, `Job^`, `Cycle^` or `Scenario^`).

    Returns:
        The entity that corresponds to the provided identifier. Returns None if no matching entity is found.

    Raises:
        ModelNotFound^: If the provided *entity_id* does not match any known entity pattern.
    """
    if entity_id.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._get(JobId(entity_id))
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._get(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._get(ScenarioId(entity_id))
    if entity_id.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._get(SequenceId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._get(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._get(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_tasks() -> List[Task]:
    """Retrieve a list of all existing tasks.

    This function returns a list of all tasks that currently exist.

    Returns:
        A list containing all the tasks.
    """
    return _TaskManagerFactory._build_manager()._get_all()


def is_deletable(entity: Union[Scenario, Job, ScenarioId, JobId]) -> bool:
    """Check if a `Scenario^` or a `Job^` can be deleted.

    This function determines whether a scenario or a job can be safely
    deleted without causing conflicts or issues.

    Parameters:
        entity (Union[Scenario, Job, ScenarioId, JobId]): The scenario or job to check.

    Returns:
        True if the given scenario or job can be deleted. False otherwise.
    """
    if isinstance(entity, str) and entity.startswith(Job._ID_PREFIX) or isinstance(entity, Job):
        return _JobManagerFactory._build_manager()._is_deletable(entity)  # type: ignore
    if isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX) or isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._is_deletable(entity)  # type: ignore
    return True


def delete(entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId]):
    """Delete an entity and its nested entities.

    This function deletes the specified entity and recursively deletes all its nested entities.
    The behavior varies depending on the type of entity provided:

    - If a `CycleId` is provided, the nested scenarios, tasks, data nodes, and jobs are deleted.
    - If a `ScenarioId` is provided, the nested tasks, data nodes, and jobs are deleted.
      If the scenario is primary, it can only be deleted if it is the only scenario in the cycle.
      In that case, its cycle is also deleted. Use the `is_deletable()^` function to check if
      the scenario can be deleted.
    - If a `SequenceId` is provided, the related jobs are deleted.
    - If a `TaskId` is provided, the related data nodes, and jobs are deleted.

    Parameters:
        entity_id (Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId]):
            The identifier of the entity to delete.

    Raises:
        ModelNotFound: No entity corresponds to the specified *entity_id*.
    """
    if entity_id.startswith(Job._ID_PREFIX):
        job_manager = _JobManagerFactory._build_manager()
        return job_manager._delete(job_manager._get(JobId(entity_id)))  # type: ignore
    if entity_id.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._hard_delete(CycleId(entity_id))
    if entity_id.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._hard_delete(ScenarioId(entity_id))
    if entity_id.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._hard_delete(SequenceId(entity_id))
    if entity_id.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._hard_delete(TaskId(entity_id))
    if entity_id.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._delete(DataNodeId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_scenarios(cycle: Optional[Cycle] = None, tag: Optional[str] = None) -> List[Scenario]:
    """Retrieve a list of existing scenarios filtered by cycle or tag.

    This function allows you to retrieve a list of scenarios based on optional
    filtering criteria. If both a _cycle_ and a _tag_ are provided, the returned
    list contains scenarios that belong to the specified _cycle_ **and** also
    have the specified _tag_.

    Parameters:
         cycle (Optional[Cycle^]): The optional `Cycle^` to filter scenarios by.
         tag (Optional[str]): The optional tag to filter scenarios by.

    Returns:
        The list of scenarios filtered by cycle or tag. If no filtering criteria
            are provided, this method returns all existing scenarios.
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
    """Retrieve the primary scenario associated with a cycle.

    Parameters:
        cycle (Cycle^): The cycle for which to retrieve the primary scenario.

    Returns:
        The primary scenario of the given _cycle_. If the cycle has no
            primary scenario, this method returns None.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary(cycle)


def get_primary_scenarios() -> List[Scenario]:
    """Retrieve a list of all primary scenarios.

    Returns:
        A list containing all primary scenarios.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary_scenarios()


def is_promotable(scenario: Union[Scenario, ScenarioId]) -> bool:
    """Determine if a scenario can be promoted to become a primary scenario.

    This function checks whether the given scenario is eligible to be promoted
    as a primary scenario.

    Parameters:
        scenario (Union[Scenario, ScenarioId]): The scenario to be evaluated for promotability.

    Returns:
        True if the given scenario can be promoted to be a primary scenario. False otherwise.
    """
    return _ScenarioManagerFactory._build_manager()._is_promotable_to_primary(scenario)


def set_primary(scenario: Scenario):
    """Promote a scenario as the primary scenario of its cycle.

    This function promotes the given scenario as the primary scenario of its associated cycle.
    If the cycle already has a primary scenario, that scenario is demoted and is
    no longer considered the primary scenario for its cycle.

    Parameters:
        scenario (Scenario^): The scenario to promote as the new _primary_ scenario.
    """
    return _ScenarioManagerFactory._build_manager()._set_primary(scenario)


def tag(scenario: Scenario, tag: str):
    """Add a tag to a scenario.

    This function adds a user-defined tag to the specified scenario. If another scenario
    within the same cycle already has the same tag applied, the previous scenario is untagged.

    Parameters:
        scenario (Scenario^): The scenario to which the tag will be added.
        tag (str): The tag to apply to the scenario.
    """
    return _ScenarioManagerFactory._build_manager()._tag(scenario, tag)


def untag(scenario: Scenario, tag: str):
    """Remove a tag from a scenario.

    This function removes a specified tag from the given scenario. If the scenario does
    not have the specified tag, it has no effect.

    Parameters:
        scenario (Scenario^): The scenario from which the tag will be removed.
        tag (str): The tag to remove from the scenario.
    """
    return _ScenarioManagerFactory._build_manager()._untag(scenario, tag)


def compare_scenarios(*scenarios: Scenario, data_node_config_id: Optional[str] = None) -> Dict[str, Any]:
    """Compare the data nodes of several scenarios.

    You can specify which data node config identifier should the comparison be performed
    on.

    Parameters:
        *scenarios (*Scenario^): The list of the scenarios to compare.
        data_node_config_id (Optional[str]): The config identifier of the DataNode to perform
            the comparison on. <br/>

            If _data_node_config_id_ is not provided, the scenarios are
            compared on all defined comparators.<br/>

    Returns:
        The comparison results. The key is the data node config identifier used for
        comparison.

    Raises:
        InsufficientScenarioToCompare^: Raised when only one or no scenario for comparison
            is provided.
        NonExistingComparator^: Raised when the scenario comparator does not exist.
        DifferentScenarioConfigs^: Raised when the provided scenarios do not share the
            same scenario config.
        NonExistingScenarioConfig^: Raised when the scenario config of the provided
            scenarios could not be found.
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
        scenario (Optional[Scenario^]): The scenario to which the callback is applied.
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

    If no scenario is provided, the subscription is removed for all scenarios.

    Parameters:
        callback (Callable[[Scenario^, Job^], None]): The function to unsubscribe from.
        params (Optional[List[Any]]): The parameters to be passed to the callback.
        scenario (Optional[Scenario]): The scenario to unsubscribe from. If None, it
            applies to all scenarios.

    Note:
        The callback function will continue to be called for ongoing jobs.
    """
    return _ScenarioManagerFactory._build_manager()._unsubscribe(callback, params, scenario)


def subscribe_sequence(
    callback: Callable[[Sequence, Job], None], params: Optional[List[Any]] = None, sequence: Optional[Sequence] = None
):
    """Subscribe a function to be called on job status change.

    The subscription is applied to all jobs created for the execution of _sequence_.

    Parameters:
        callback (Callable[[Sequence^, Job^], None]): The callable function to be called on
            status change.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        sequence (Optional[Sequence^]): The sequence to subscribe on. If None, the subscription
            is applied to all sequences.

    Note:
        Notifications are applied only for jobs created **after** this subscription.
    """
    return _SequenceManagerFactory._build_manager()._subscribe(callback, params, sequence)


def unsubscribe_sequence(
    callback: Callable[[Sequence, Job], None], params: Optional[List[Any]] = None, sequence: Optional[Sequence] = None
):
    """Unsubscribe a function that is called when the status of a Job changes.

    Parameters:
        callback (Callable[[Sequence^, Job^], None]): The callable function to be called on
            status change.
        params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        sequence (Optional[Sequence^]): The sequence to unsubscribe to. If None, it applies
            to all sequences.

    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _SequenceManagerFactory._build_manager()._unsubscribe(callback, params, sequence)


def get_sequences() -> List[Sequence]:
    """Return all existing sequences.

    Returns:
        The list of all sequences.
    """
    return _SequenceManagerFactory._build_manager()._get_all()


def get_jobs() -> List[Job]:
    """Return all the existing jobs.

    Returns:
        The list of all jobs.
    """
    return _JobManagerFactory._build_manager()._get_all()


def delete_job(job: Job, force=False):
    """Delete a job.

    This function deletes the specified job. If the job is not completed and
    *force* is not set to True, a `JobNotDeletedException^` may be raised.

    Parameters:
        job (Job^): The job to delete.
        force (Optional[bool]): If True, forces the deletion of _job_, even
            if it is not completed yet.
    Raises:
        JobNotDeletedException^: If the job is not finished.
    """
    return _JobManagerFactory._build_manager()._delete(job, force)


def delete_jobs():
    """Delete all jobs."""
    return _JobManagerFactory._build_manager()._delete_all()


def cancel_job(job: Union[str, Job]):
    """Cancel a job and set the status of the subsequent jobs to ABANDONED.

    This function cancels the specified job and sets the status of any subsequent jobs to ABANDONED.

    Parameters:
        job (Job^): The job to cancel.
    """
    _JobManagerFactory._build_manager()._cancel(job)


def get_latest_job(task: Task) -> Optional[Job]:
    """Return the latest job of a task.

    This function retrieves the latest job associated with a task.

    Parameters:
        task (Task^): The task to retrieve the latest job from.
    Returns:
        The latest job created from _task_, or None if no job has been created from _task_.
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
    """Create and return a new scenario based on a scenario configuration.

    If the scenario belongs to a cycle, a cycle (corresponding to the _creation_date_
    and the configuration frequency attribute) is created if it does not exist yet.

    Parameters:
        config (ScenarioConfig^): The scenario configuration used to create a new scenario.
        creation_date (Optional[datetime.datetime]): The creation date of the scenario.
            If None, the current date time is used.
        name (Optional[str]): The displayable name of the scenario.
    Returns:
        The new scenario.
    """
    return _ScenarioManagerFactory._build_manager()._create(config, creation_date, name)


def create_global_data_node(config: DataNodeConfig) -> DataNode:
    """Create and return a new GLOBAL data node from a data node configuration.

    Parameters:
        config (DataNodeConfig^): The data node configuration. It must have a `GLOBAL` scope.

    Returns:
        The new global data node.

    Raises:
        DataNodeConfigIsNotGlobal^: If the data node configuration does not have GLOBAL scope.
    """
    # Check if the data node config has GLOBAL scope
    if config.scope is not Scope.GLOBAL:
        raise DataNodeConfigIsNotGlobal(config.id)  # type: ignore

    if dns := _DataManagerFactory._build_manager()._get_by_config_id(config.id):  # type: ignore
        return dns[0]
    return _DataManagerFactory._build_manager()._create_and_set(config, None, None)


def clean_all_entities_by_version(version_number=None) -> bool:
    """Delete all entities of a specific version.

    This function deletes all entities associated with the specified version.

    Parameters:
        version_number (optional[str]): The version number of the entities to be deleted.
            If None, the default behavior may apply.

    Returns:
        True if the operation succeeded, False otherwise.

    Notes:
        - If the specified version does not exist, the operation will be aborted, and False will be returned.
        - This function cleans all entities, including jobs, scenarios, sequences, tasks, and data nodes.
        - The production version of the specified version is also deleted if it exists.
    """
    version_manager = _VersionManagerFactory._build_manager()
    try:
        version_number = version_manager._replace_version_number(version_number)
    except NonExistingVersion as e:
        __logger.warning(f"{e.message} Abort cleaning the entities of version '{version_number}'.")
        return False

    _JobManagerFactory._build_manager()._delete_by_version(version_number)
    _ScenarioManagerFactory._build_manager()._delete_by_version(version_number)
    _SequenceManagerFactory._build_manager()._delete_by_version(version_number)
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

    This function exports all related entities of the specified scenario to the
    specified folder.

    Parameters:
        scenario_id (ScenarioId): The ID of the scenario to export.
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
    for sequence_id in entity_ids.sequence_ids:
        _SequenceManagerFactory._build_manager()._export(sequence_id, folder_path)
    for cycle_id in entity_ids.cycle_ids:
        _CycleManagerFactory._build_manager()._export(cycle_id, folder_path)
    for scenario_id in entity_ids.scenario_ids:
        _ScenarioManagerFactory._build_manager()._export(scenario_id, folder_path)
    for job_id in entity_ids.job_ids:
        _JobManagerFactory._build_manager()._export(job_id, folder_path)


def get_parents(
    entity: Union[TaskId, DataNodeId, SequenceId, Task, DataNode, Sequence], parent_dict=None
) -> Dict[str, Set[_Entity]]:
    """Get the parents of an entity from itself or its identifier.

    Parameters:
        entity (Union[TaskId, DataNodeId, SequenceId, Task, DataNode, Sequence]): The entity or its
            identifier to get the parents.

    Returns:
        The dictionary of all parent entities.
            They are grouped by their type (Scenario^, Sequences^, or tasks^) so each key corresponds
            to a level of the parents and the value is a set of the parent entities.
            An empty dictionary is returned if the entity does not have parents.<br/>
            Example: The following instruction returns all the scenarios that include the
            datanode identified by "my_datanode_id".
            `taipy.get_parents("id_of_my_datanode")["scenario"]`

    Raises:
        ModelNotFound^: If _entity_ does not match a correct entity pattern.
    """

    def update_parent_dict(parents_set, parent_dict):
        for k, value in parents_set.items():
            if k in parent_dict.keys():
                parent_dict[k].update(value)
            else:
                parent_dict[k] = value

    if isinstance(entity, str):
        entity = get(entity)  # type: ignore

    parent_dict = parent_dict or dict()

    if isinstance(entity, (Scenario, Cycle)):
        return parent_dict

    current_parent_dict: Dict[str, Set] = {}
    for parent in entity.parent_ids:
        parent_entity = get(parent)
        if parent_entity._MANAGER_NAME in current_parent_dict.keys():
            current_parent_dict[parent_entity._MANAGER_NAME].add(parent_entity)
        else:
            current_parent_dict[parent_entity._MANAGER_NAME] = {parent_entity}

    if isinstance(entity, Sequence):
        update_parent_dict(current_parent_dict, parent_dict)

    if isinstance(entity, Task):
        parent_entity_key_to_search_next = "scenario"
        update_parent_dict(current_parent_dict, parent_dict)
        for parent in parent_dict.get(parent_entity_key_to_search_next, []):
            get_parents(parent, parent_dict)

    if isinstance(entity, DataNode):
        parent_entity_key_to_search_next = "task"
        update_parent_dict(current_parent_dict, parent_dict)
        for parent in parent_dict.get(parent_entity_key_to_search_next, []):
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
) -> Union[List, List[Task], List[DataNode], List[Sequence], List[Scenario]]:
    """Get the entities by its config id.

    Parameters:
        config_id (str): The config id of the entities

    Returns:
        The list of all entities by the config id.
    """

    entities: List = []

    if entities := _ScenarioManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    if entities := _TaskManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    if entities := _DataManagerFactory._build_manager()._get_by_config_id(config_id):
        return entities
    return entities
