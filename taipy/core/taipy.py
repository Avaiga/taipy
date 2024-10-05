# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Union, overload

from taipy.common.config import Scope
from taipy.common.logger._taipy_logger import _TaipyLogger

from ._entity._entity import _Entity
from ._version._version_manager_factory import _VersionManagerFactory
from .common._check_instance import (
    _is_cycle,
    _is_data_node,
    _is_job,
    _is_scenario,
    _is_sequence,
    _is_submission,
    _is_task,
)
from .common._warnings import _warn_no_orchestrator_service
from .config.data_node_config import DataNodeConfig
from .config.scenario_config import ScenarioConfig
from .cycle._cycle_manager_factory import _CycleManagerFactory
from .cycle.cycle import Cycle
from .cycle.cycle_id import CycleId
from .data._data_manager_factory import _DataManagerFactory
from .data.data_node import DataNode
from .data.data_node_id import DataNodeId
from .exceptions.exceptions import DataNodeConfigIsNotGlobal, ModelNotFound, NonExistingVersion
from .job._job_manager_factory import _JobManagerFactory
from .job.job import Job
from .job.job_id import JobId
from .orchestrator import Orchestrator
from .reason import EntityDoesNotExist, EntityIsNotSubmittableEntity, ReasonCollection
from .scenario._scenario_manager_factory import _ScenarioManagerFactory
from .scenario.scenario import Scenario
from .scenario.scenario_id import ScenarioId
from .sequence._sequence_manager_factory import _SequenceManagerFactory
from .sequence.sequence import Sequence
from .sequence.sequence_id import SequenceId
from .submission._submission_manager_factory import _SubmissionManagerFactory
from .submission.submission import Submission, SubmissionId
from .task._task_manager_factory import _TaskManagerFactory
from .task.task import Task
from .task.task_id import TaskId

__logger = _TaipyLogger._get_logger()


def set(entity: Union[DataNode, Task, Sequence, Scenario, Cycle, Submission]):
    """Save or update an entity.

    This function allows you to save or update an entity in Taipy.

    Parameters:
        entity (Union[DataNode^, Task^, Sequence^, Scenario^, Cycle^, Submission^]): The
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
    if isinstance(entity, Submission):
        return _SubmissionManagerFactory._build_manager()._set(entity)


def is_submittable(entity: Union[Scenario, ScenarioId, Sequence, SequenceId, Task, TaskId, str]) -> ReasonCollection:
    """Indicate if an entity can be submitted.

    This function checks if the given entity can be submitted for execution.

    Returns:
        True if the given entity can be submitted. False otherwise.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._is_submittable(entity)
    if isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._is_submittable(ScenarioId(entity))
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._is_submittable(entity)
    if isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._is_submittable(SequenceId(entity))
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._is_submittable(entity)
    if isinstance(entity, str) and entity.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._is_submittable(TaskId(entity))
    return ReasonCollection()._add_reason(str(entity), EntityIsNotSubmittableEntity(str(entity)))


def is_editable(
    entity: Union[
        DataNode,
        Task,
        Job,
        Sequence,
        Scenario,
        Cycle,
        Submission,
        DataNodeId,
        TaskId,
        JobId,
        SequenceId,
        ScenarioId,
        CycleId,
        SubmissionId,
    ],
) -> ReasonCollection:
    """Indicate if an entity can be edited.

    This function checks if the given entity can be edited.

    Returns:
        A ReasonCollection object that can function as a Boolean value,
        which is True if the given entity can be edited. False otherwise.
    """
    if isinstance(entity, Cycle):
        return _CycleManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._is_editable(CycleId(entity))
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._is_editable(ScenarioId(entity))
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._is_editable(SequenceId(entity))
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._is_editable(TaskId(entity))
    if isinstance(entity, Job):
        return _JobManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._is_editable(JobId(entity))
    if isinstance(entity, DataNode):
        return _DataManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._is_editable(DataNodeId(entity))
    if isinstance(entity, Submission):
        return _SubmissionManagerFactory._build_manager()._is_editable(entity)
    if isinstance(entity, str) and entity.startswith(Submission._ID_PREFIX):
        return _SubmissionManagerFactory._build_manager()._is_editable(SequenceId(entity))
    return ReasonCollection()._add_reason(str(entity), EntityDoesNotExist(str(entity)))


def is_readable(
    entity: Union[
        DataNode,
        Task,
        Job,
        Sequence,
        Scenario,
        Cycle,
        Submission,
        DataNodeId,
        TaskId,
        JobId,
        SequenceId,
        ScenarioId,
        CycleId,
        SubmissionId,
    ],
) -> ReasonCollection:
    """Indicate if an entity can be read.

    This function checks if the given entity can be read.

    Returns:
        A ReasonCollection object that can function as a Boolean value,
        which is True if the given entity can be read. False otherwise.
    """
    if isinstance(entity, Cycle):
        return _CycleManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Cycle._ID_PREFIX):
        return _CycleManagerFactory._build_manager()._is_readable(CycleId(entity))
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._is_readable(ScenarioId(entity))
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX):
        return _SequenceManagerFactory._build_manager()._is_readable(SequenceId(entity))
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Task._ID_PREFIX):
        return _TaskManagerFactory._build_manager()._is_readable(TaskId(entity))
    if isinstance(entity, Job):
        return _JobManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._is_readable(JobId(entity))
    if isinstance(entity, DataNode):
        return _DataManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(DataNode._ID_PREFIX):
        return _DataManagerFactory._build_manager()._is_readable(DataNodeId(entity))
    if isinstance(entity, Submission):
        return _SubmissionManagerFactory._build_manager()._is_readable(entity)
    if isinstance(entity, str) and entity.startswith(Submission._ID_PREFIX):
        return _SubmissionManagerFactory._build_manager()._is_readable(SequenceId(entity))
    return ReasonCollection()._add_reason(str(entity), EntityDoesNotExist(str(entity)))


@_warn_no_orchestrator_service("The submitted entity will not be executed until the Orchestrator service is running.")
def submit(
    entity: Union[Scenario, Sequence, Task],
    force: bool = False,
    wait: bool = False,
    timeout: Optional[Union[float, int]] = None,
    **properties,
) -> Submission:
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
            for the jobs to be finished before returning.<br/>
            If not provided and *wait* is True, the function waits indefinitely.
        **properties (dict[str, any]): A key-worded variable length list of user additional arguments
            that will be stored within the `Submission^`. It can be accessed via `Submission.properties^`.

    Returns:
        The created `Submission^` containing the information about the submission.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._submit(
            entity, force=force, wait=wait, timeout=timeout, **properties
        )
    if isinstance(entity, Sequence):
        return _SequenceManagerFactory._build_manager()._submit(
            entity, force=force, wait=wait, timeout=timeout, **properties
        )
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._submit(
            entity, force=force, wait=wait, timeout=timeout, **properties
        )
    return None


@overload
def exists(entity_id: TaskId) -> ReasonCollection: ...


@overload
def exists(entity_id: DataNodeId) -> ReasonCollection: ...


@overload
def exists(entity_id: SequenceId) -> ReasonCollection: ...


@overload
def exists(entity_id: ScenarioId) -> ReasonCollection: ...


@overload
def exists(entity_id: CycleId) -> ReasonCollection: ...


@overload
def exists(entity_id: JobId) -> ReasonCollection: ...


@overload
def exists(entity_id: SubmissionId) -> ReasonCollection: ...


@overload
def exists(entity_id: str) -> ReasonCollection: ...


def exists(
    entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, SubmissionId, str],
) -> ReasonCollection:
    """Check if an entity with the specified identifier exists.

    This function checks if an entity with the given identifier exists.
    It supports various types of entity identifiers, including `TaskId`,
    `DataNodeId`, `SequenceId`, `ScenarioId`, `JobId`, `CycleId`, `SubmissionId`, and string
    representations.

    Parameters:
        entity_id (Union[DataNodeId, TaskId, SequenceId, ScenarioId, JobId, CycleId, SubmissionId, str]): The
            identifier of the entity to check for existence.

    Returns:
        A ReasonCollection object that can function as a Boolean value,
        which is True if the given entity exists. False otherwise.

    Raises:
        ModelNotFound: If the entity's type cannot be determined.

    Note:
        The function performs checks for various entity types
        (`Job^`, `Cycle^`, `Scenario^`, `Sequence^`, `Task^`, `DataNode^`, `Submission^`)
        based on their respective identifier prefixes.
    """
    if _is_job(entity_id):
        return _JobManagerFactory._build_manager()._exists(JobId(entity_id))
    if _is_cycle(entity_id):
        return _CycleManagerFactory._build_manager()._exists(CycleId(entity_id))
    if _is_scenario(entity_id):
        return _ScenarioManagerFactory._build_manager()._exists(ScenarioId(entity_id))
    if _is_sequence(entity_id):
        return _SequenceManagerFactory._build_manager()._exists(SequenceId(entity_id))
    if _is_task(entity_id):
        return _TaskManagerFactory._build_manager()._exists(TaskId(entity_id))
    if _is_data_node(entity_id):
        return _DataManagerFactory._build_manager()._exists(DataNodeId(entity_id))
    if _is_submission(entity_id):
        return _SubmissionManagerFactory._build_manager()._exists(SubmissionId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


@overload
def get(entity_id: TaskId) -> Task: ...


@overload
def get(entity_id: DataNodeId) -> DataNode: ...


@overload
def get(entity_id: SequenceId) -> Sequence: ...


@overload
def get(entity_id: ScenarioId) -> Scenario: ...


@overload
def get(entity_id: CycleId) -> Cycle: ...


@overload
def get(entity_id: JobId) -> Job: ...


@overload
def get(entity_id: SubmissionId) -> Submission: ...


@overload
def get(entity_id: str) -> Union[Task, DataNode, Sequence, Scenario, Job, Cycle, Submission]: ...


def get(
    entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, SubmissionId, str],
) -> Union[Task, DataNode, Sequence, Scenario, Job, Cycle, Submission]:
    """Retrieve an entity by its unique identifier.

    This function allows you to retrieve an entity by specifying its identifier.
    The identifier must match the pattern of one of the supported entity types:
    `Task^`, `DataNode^`, `Sequence^`, `Job^`, `Cycle^`, `Submission^`, or `Scenario^`.


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
    if _is_job(entity_id):
        return _JobManagerFactory._build_manager()._get(JobId(entity_id))
    if _is_cycle(entity_id):
        return _CycleManagerFactory._build_manager()._get(CycleId(entity_id))
    if _is_scenario(entity_id):
        return _ScenarioManagerFactory._build_manager()._get(ScenarioId(entity_id))
    if _is_sequence(entity_id):
        return _SequenceManagerFactory._build_manager()._get(SequenceId(entity_id))
    if _is_task(entity_id):
        return _TaskManagerFactory._build_manager()._get(TaskId(entity_id))
    if _is_data_node(entity_id):
        return _DataManagerFactory._build_manager()._get(DataNodeId(entity_id))
    if _is_submission(entity_id):
        return _SubmissionManagerFactory._build_manager()._get(SubmissionId(entity_id))

    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_tasks() -> List[Task]:
    """Retrieve a list of all existing tasks.

    This function returns a list of all tasks that currently exist.

    Returns:
        A list containing all the tasks.
    """
    return _TaskManagerFactory._build_manager()._get_all()


def is_deletable(entity: Union[Scenario, Job, Submission, ScenarioId, JobId, SubmissionId]) -> ReasonCollection:
    """Check if a `Scenario^`, a `Job^` or a `Submission^` can be deleted.

    This function determines whether a scenario or a job can be safely
    deleted without causing conflicts or issues.

    Parameters:
        entity (Union[Scenario, Job, Submission, ScenarioId, JobId, SubmissionId]): The scenario,
            job or submission to check.

    Returns:
        A ReasonCollection object that can function as a Boolean value, which is True
            if the given scenario, job or submission can be deleted. False otherwise.
    """
    if isinstance(entity, Job):
        return _JobManagerFactory._build_manager()._is_deletable(entity)
    if isinstance(entity, str) and entity.startswith(Job._ID_PREFIX):
        return _JobManagerFactory._build_manager()._is_deletable(JobId(entity))
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._is_deletable(entity)
    if isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX):
        return _ScenarioManagerFactory._build_manager()._is_deletable(ScenarioId(entity))
    if isinstance(entity, Submission):
        return _SubmissionManagerFactory._build_manager()._is_deletable(entity)
    if isinstance(entity, str) and entity.startswith(Submission._ID_PREFIX):
        return _SubmissionManagerFactory._build_manager()._is_deletable(SubmissionId(entity))
    return ReasonCollection()._add_reason(str(entity), EntityDoesNotExist(str(entity)))


def delete(entity_id: Union[TaskId, DataNodeId, SequenceId, ScenarioId, JobId, CycleId, SubmissionId]):
    """Delete an entity and its nested entities.

    This function deletes the specified entity and recursively deletes all its nested entities.
    The behavior varies depending on the type of entity provided:

    - If a `CycleId` is provided, the nested scenarios, tasks, data nodes, and jobs are deleted.
    - If a `ScenarioId` is provided, the nested sequences, tasks, data nodes, submissions and jobs are deleted.
      If the scenario is primary, it can only be deleted if it is the only scenario in the cycle.
      In that case, its cycle is also deleted. Use the `is_deletable()^` function to check if
      the scenario can be deleted.
    - If a `SequenceId` is provided, the related jobs are deleted.
    - If a `TaskId` is provided, the related data nodes, and jobs are deleted.
    - If a `DataNodeId` is provided, the data node is deleted.
    - If a `SubmissionId` is provided, the related jobs are deleted.
      The submission can only be deleted if the execution has been finished.
    - If a `JobId` is provided, the job entity can only be deleted if the execution has been finished.

    Parameters:
        entity_id (Union[TaskId, DataNodeId, SequenceId, ScenarioId, SubmissionId, JobId, CycleId]):
            The identifier of the entity to delete.

    Raises:
        ModelNotFound^: No entity corresponds to the specified *entity_id*.
    """
    if _is_job(entity_id):
        job_manager = _JobManagerFactory._build_manager()
        return job_manager._delete(job_manager._get(JobId(entity_id)))
    if _is_cycle(entity_id):
        return _CycleManagerFactory._build_manager()._hard_delete(CycleId(entity_id))
    if _is_scenario(entity_id):
        return _ScenarioManagerFactory._build_manager()._hard_delete(ScenarioId(entity_id))
    if _is_sequence(entity_id):
        return _SequenceManagerFactory._build_manager()._hard_delete(SequenceId(entity_id))
    if _is_task(entity_id):
        return _TaskManagerFactory._build_manager()._hard_delete(TaskId(entity_id))
    if _is_data_node(entity_id):
        return _DataManagerFactory._build_manager()._delete(DataNodeId(entity_id))
    if _is_submission(entity_id):
        return _SubmissionManagerFactory._build_manager()._hard_delete(SubmissionId(entity_id))
    raise ModelNotFound("NOT_DETERMINED", entity_id)


def get_scenarios(
    cycle: Optional[Cycle] = None,
    tag: Optional[str] = None,
    is_sorted: bool = False,
    descending: bool = False,
    created_start_time: Optional[datetime] = None,
    created_end_time: Optional[datetime] = None,
    sort_key: Literal["name", "id", "config_id", "creation_date", "tags"] = "name",
) -> List[Scenario]:
    """Retrieve a list of existing scenarios filtered by cycle or tag.

    This function allows you to retrieve a list of scenarios based on optional
    filtering criteria. If both a *cycle* and a *tag* are provided, the returned
    list contains scenarios that belong to the specified *cycle* and also
    have the specified *tag*.

    Parameters:
        cycle (Optional[Cycle^]): The optional `Cycle^` to filter scenarios by.
        tag (Optional[str]): The optional tag to filter scenarios by.
        is_sorted (bool): If True, sort the output list of scenarios using the sorting key.
            The default value is False.
        descending (bool): If True, sort the output list of scenarios in descending order.
            The default value is False.
        created_start_time (Optional[datetime]): The optional inclusive start date to filter scenarios by creation date.
        created_end_time (Optional[datetime]): The optional exclusive end date to filter scenarios by creation date.
        sort_key (Literal["name", "id", "creation_date", "tags"]): The optional sort_key to
            decide upon what key scenarios are sorted. The sorting is in increasing order for
            dates, in alphabetical order for name and id, and in lexicographical order for tags.
            The default value is "name".<br/>
            If an incorrect sorting key is provided, the scenarios are sorted by name.

    Returns:
        The list of scenarios filtered by cycle or tag.
    """
    scenario_manager = _ScenarioManagerFactory._build_manager()
    if not cycle and not tag:
        scenarios = scenario_manager._get_all()
    elif cycle and not tag:
        scenarios = scenario_manager._get_all_by_cycle(cycle)
    elif not cycle and tag:
        scenarios = scenario_manager._get_all_by_tag(tag)
    elif cycle and tag:
        scenarios = scenario_manager._get_all_by_cycle_tag(cycle, tag)
    else:
        scenarios = []

    if created_start_time or created_end_time:
        scenarios = scenario_manager._filter_by_creation_time(scenarios, created_start_time, created_end_time)
    if is_sorted:
        scenario_manager._sort_scenarios(scenarios, descending, sort_key)
    return scenarios


def get_primary(cycle: Cycle) -> Optional[Scenario]:
    """Retrieve the primary scenario associated with a cycle.

    Parameters:
        cycle (Cycle^): The cycle for which to retrieve the primary scenario.

    Returns:
        The primary scenario of the given _cycle_. If the cycle has no
            primary scenario, this method returns None.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary(cycle)


def get_primary_scenarios(
    is_sorted: bool = False,
    descending: bool = False,
    created_start_time: Optional[datetime] = None,
    created_end_time: Optional[datetime] = None,
    sort_key: Literal["name", "id", "config_id", "creation_date", "tags"] = "name",
) -> List[Scenario]:
    """Retrieve a list of all primary scenarios.

    Parameters:
        is_sorted (bool): If True, sort the output list of scenarios using the sorting key.
            The default value is False.
        descending (bool): If True, sort the output list of scenarios in descending order.
            The default value is False.
        created_start_time (Optional[datetime]): The optional inclusive start date to filter scenarios by creation date.
        created_end_time (Optional[datetime]): The optional exclusive end date to filter scenarios by creation date.
        sort_key (Literal["name", "id", "creation_date", "tags"]): The optional sort_key to
            decide upon what key scenarios are sorted. The sorting is in increasing order for
            dates, in alphabetical order for name and id, and in lexicographical order for tags.
            The default value is "name".<br/>
            If an incorrect sorting key is provided, the scenarios are sorted by name.

    Returns:
        A list contains all primary scenarios.
    """
    scenario_manager = _ScenarioManagerFactory._build_manager()
    scenarios = scenario_manager._get_primary_scenarios()

    if created_start_time or created_end_time:
        scenarios = scenario_manager._filter_by_creation_time(scenarios, created_start_time, created_end_time)
    if is_sorted:
        scenario_manager._sort_scenarios(scenarios, descending, sort_key)
    return scenarios


def is_promotable(scenario: Union[Scenario, ScenarioId]) -> ReasonCollection:
    """Determine if a scenario can be promoted to become a primary scenario.

    This function checks whether the given scenario is eligible to be promoted
    as a primary scenario.

    Parameters:
        scenario (Union[Scenario, ScenarioId]): The scenario to be evaluated for promotion.

    Returns:
        A ReasonCollection object that can function as a Boolean value,
        which is True if the given scenario can be promoted to be a primary scenario. False otherwise.
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

    This function adds a user-defined tag to the specified scenario.

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
) -> None:
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


def get_submissions() -> List[Submission]:
    """Return all the existing submissions.

    Returns:
        The list of all submissions.
    """
    return _SubmissionManagerFactory._build_manager()._get_all()


def delete_job(job: Job, force: Optional[bool] = False):
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


def get_latest_submission(entity: Union[Scenario, Sequence, Task]) -> Optional[Submission]:
    """Return the latest submission of a scenario, sequence or task.

    This function retrieves the latest submission associated with a scenario, sequence or task.

    Parameters:
        entity (Union[Scenario^, Sequence^, Task^]): The scenario, sequence or task to
            retrieve the latest submission from.

    Returns:
        The latest submission created from _scenario_, _sequence_ and _task_, or None
        if no submission has been created from _scenario_, _sequence_ and _task_.
    """
    return _SubmissionManagerFactory._build_manager()._get_latest(entity)


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


def can_create(config: Optional[Union[ScenarioConfig, DataNodeConfig]] = None) -> ReasonCollection:
    """Indicate if a config can be created. The config should be a scenario or data node config.

    If no config is provided, the function indicates if any scenario or data node config can be created.

    Returns:
        True if the given config can be created. False otherwise.
    """
    if isinstance(config, DataNodeConfig):
        return _DataManagerFactory._build_manager()._can_create(config)

    return _ScenarioManagerFactory._build_manager()._can_create(config)


def create_scenario(
    config: ScenarioConfig,
    creation_date: Optional[datetime] = None,
    name: Optional[str] = None,
) -> Scenario:
    """Create and return a new scenario based on a scenario configuration.

    This function checks and locks the configuration, manages application's version,
    and creates a new scenario from the scenario configuration provided.

    If the scenario belongs to a cycle, the cycle (corresponding to the _creation_date_
    and the configuration frequency attribute) is created if it does not exist yet.

    Parameters:
        config (ScenarioConfig^): The scenario configuration used to create a new scenario.
        creation_date (Optional[datetime.datetime]): The creation date of the scenario.
            If None, the current date time is used.
        name (Optional[str]): The displayable name of the scenario.

    Returns:
        The new scenario.

    Raises:
        SystemExit: If the configuration check returns some errors.

    """
    Orchestrator._manage_version_and_block_config()

    return _ScenarioManagerFactory._build_manager()._create(config, creation_date, name)


def create_global_data_node(config: DataNodeConfig) -> DataNode:
    """Create and return a new GLOBAL data node from a data node configuration.

    This function checks and locks the configuration, manages application's version,
    and creates the new data node from the data node configuration provided.

    Parameters:
        config (DataNodeConfig^): The data node configuration. It must have a `GLOBAL` scope.

    Returns:
        The new global data node.

    Raises:
        DataNodeConfigIsNotGlobal^: If the data node configuration does not have GLOBAL scope.
        SystemExit: If the configuration check returns some errors.
    """
    # Check if the data node config has GLOBAL scope
    if config.scope is not Scope.GLOBAL:
        raise DataNodeConfigIsNotGlobal(config.id)

    Orchestrator._manage_version_and_block_config()

    if dns := _DataManagerFactory._build_manager()._get_by_config_id(config.id):
        return dns[0]
    return _DataManagerFactory._build_manager()._create_and_set(config, None, None)


def clean_all_entities(version_number: str) -> bool:
    """Deletes all entities associated with the specified version.
    This function cleans all entities, including jobs, submissions, scenarios, cycles, sequences, tasks, and data nodes.

    Parameters:
        version_number (str): The version number of the entities to be deleted.<br/>
            - If the specified version does not exist, the operation will be aborted, and False will be returned.

    Returns:
        True if the operation succeeded, False otherwise.
    """
    version_manager = _VersionManagerFactory._build_manager()
    try:
        version_number = version_manager._replace_version_number(version_number)
    except NonExistingVersion as e:
        __logger.warning(f"{e.message} Abort cleaning the entities of version '{version_number}'.")
        return False

    if not version_manager._is_deletable(version_number):
        reason_collection = version_manager._is_deletable(version_number)
        __logger.warning(f"Abort cleaning the entities of version '{version_number}'. {reason_collection.reasons}.")
        return False

    _JobManagerFactory._build_manager()._delete_by_version(version_number)
    _SubmissionManagerFactory._build_manager()._delete_by_version(version_number)
    _ScenarioManagerFactory._build_manager()._delete_by_version(version_number)
    _SequenceManagerFactory._build_manager()._delete_by_version(version_number)
    _TaskManagerFactory._build_manager()._delete_by_version(version_number)
    _DataManagerFactory._build_manager()._delete_by_version(version_number)
    version_manager._delete(version_number)

    return True


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
        entity = get(entity)

    parent_dict = parent_dict or {}

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
