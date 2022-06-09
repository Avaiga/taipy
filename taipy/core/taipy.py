# Copyright 2022 Avaiga Private Limited
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
from typing import Callable, Dict, List, Optional, Union

from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import CycleId, DataNodeId, JobId, PipelineId, ScenarioId, TaskId
from taipy.core.config.config import Config
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.cycle.cycle import Cycle
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.exceptions import ModelNotFound
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task

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


def submit(entity: Union[Scenario, Pipeline, Task], force: bool = False):
    """Submit an entity for execution.

    If the entity is a pipeline or a scenario, all the tasks of the entity are
    submitted for execution.

    Parameters:
        entity (Union[Scenario^, Pipeline^, Task^]): The entity to submit.
        force (bool): If True, the execution is forced even if the data nodes are in cache.
    """
    if isinstance(entity, Scenario):
        return _ScenarioManagerFactory._build_manager()._submit(entity, force=force)
    if isinstance(entity, Pipeline):
        return _PipelineManagerFactory._build_manager()._submit(entity, force=force)
    if isinstance(entity, Task):
        return _TaskManagerFactory._build_manager()._submit(entity, force=force)


def get(
    entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]
) -> Union[Task, DataNode, Pipeline, Scenario, Job, Cycle]:
    """Get an entity from its identifier.

    Parameters:
        entity_id (Union[TaskId^, DataNodeId^, PipelineId^, ScenarioId^]): The identifier
            of the entity to get.<br/>
            It must match the identifier pattern of one of the entities (`Task^`, `DataNode^`,
            `Pipeline^` or `Scenario^`).
    Returns:
        Union[Task^, DataNode^, Pipeline^, Scenario^, Job^, Cycle^]: The entity
        matching the corresponding identifier. None if no entity is found.
    Raises:
        ModelNotFound^: If _entity_id_ does not match a correct entity pattern.
    """
    if entity_id.startswith(_JobManagerFactory._build_manager()._ID_PREFIX):
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
        List[Task^]: The list of tasks.
    """
    return _TaskManagerFactory._build_manager()._get_all()


def delete(entity_id: Union[TaskId, DataNodeId, PipelineId, ScenarioId, JobId, CycleId]):
    """Delete an entity and its nested entities.

    The given entity is deleted. The deletion is propagated to all nested entities that are
    not shared by another entity.

    - If a `CycleId^` is provided, the nested scenarios, pipelines, data nodes, and jobs are deleted.
    - If a `ScenarioId^` is provided, the nested pipelines, tasks, data nodes, and jobs are deleted.
    - If a `PipelineId^` is provided, the nested tasks, data nodes, and jobs are deleted.
    - If a `TaskId^` is provided, the nested data nodes, and jobs are deleted.

    Parameters:
        entity_id (Union[TaskId^, DataNodeId^, PipelineId^, ScenarioId^, JobId^, CycleId^]): The
            identifier of the entity to delete.
    Raises:
        ModelNotFound^: No entity corresponds to _entity_id_.
    """
    if entity_id.startswith(_JobManagerFactory._build_manager()._ID_PREFIX):
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
        List[Scenario^]: The list of scenarios filtered by cycle or tag.
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
        Optional[Scenario^]: The primary scenario of the cycle _cycle_.
            If the cycle has no primary scenario, this method returns None.
    """
    return _ScenarioManagerFactory._build_manager()._get_primary(cycle)


def get_primary_scenarios() -> List[Scenario]:
    """Return the list of all primary scenarios.

    Returns:
        List[Scenario^]: The list of all primary scenarios.
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


def compare_scenarios(*scenarios: Scenario, data_node_config_id: Optional[str] = None):
    """Compare the data nodes of several scenarios.

    You can specify which data node config identifier should the comparison be performed
    on.

    Parameters:
        scenarios (*Scenario^): The list of the scenarios to compare.
        data_node_config_id (Optional[str]): Config identifier of the DataNode to compare
            scenarios.<br/>
            if _datanode_config_id_ is None, the scenarios are compared based on all the defined
            comparators.
    Returns:
        Dict[str, Any]: The comparison results. The key is the data node config identifier
            that is compared.
    Raises:
        InsufficientScenarioToCompare^: Only one or no scenario for comparison is provided.
        NonExistingComparator^: The scenario comparator does not exist.
        DifferentScenarioConfigs^: _scenarios_ do not share the same scenario config.
        NonExistingScenarioConfig^: The scenario config of the provided scenarios could not
            be found.
    """
    return _ScenarioManagerFactory._build_manager()._compare(*scenarios, data_node_config_id=data_node_config_id)


def subscribe_scenario(callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
    """Subscribe a function to be called on job status change.

    The subscription is applied to all jobs created for the execution of _scenario_.
    If no scenario is provided, the subscription applies to all scenarios.

    Parameters:
        callback (Callable[[Scenario^, Job^], None]): The function to be called on
            status change.
        scenario (Optional[Scenario^]): The scenario that subscribes to _callback_.
            If None, the subscription is registered for all scenarios.
    Note:
        Notifications are applied only for jobs created **after** this subscription.
    """
    return _ScenarioManagerFactory._build_manager()._subscribe(callback, scenario)


def unsubscribe_scenario(callback: Callable[[Scenario, Job], None], scenario: Optional[Scenario] = None):
    """Unsubscribe a function that is called when the status of a `Job^` changes.

    If _scenario_ is not provided, the subscription is removed for all scenarios.

    Parameters:
        callback (Callable[[Scenario^, Job^], None]): The function to unsubscribe to.
        scenario (Optional[Scenario^]): The scenario to unsubscribe to. If None, all scenarios
            unsubscribe to _callback_.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _ScenarioManagerFactory._build_manager()._unsubscribe(callback, scenario)


def subscribe_pipeline(callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
    """Subscribe a function to be called on job status change.

    The subscription is applied to all jobs created for the execution of _pipeline_.

    Parameters:
        callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
            status change.
        pipeline (Optional[Pipeline^]): The pipeline to subscribe on. If None, the subscription
            is actived for all pipelines.
    Note:
        Notifications are applied only for jobs created **after** this subscription.
    """
    return _PipelineManagerFactory._build_manager()._subscribe(callback, pipeline)


def unsubscribe_pipeline(callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
    """Unsubscribe a function that is called when the status of a Job changes.

    Parameters:
        callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
            status change.
        pipeline (Optional[Pipeline^]): The pipeline to unsubscribe to. If None, all pipelines
            unsubscribe to _callback_.
    Note:
        The function will continue to be called for ongoing jobs.
    """
    return _PipelineManagerFactory._build_manager()._unsubscribe(callback, pipeline)


def get_pipelines() -> List[Pipeline]:
    """Return all existing pipelines.

    Returns:
        List[Pipeline^]: The list of all pipelines.
    """
    return _PipelineManagerFactory._build_manager()._get_all()


def get_jobs() -> List[Job]:
    """Return all the existing jobs.

    Returns:
        List[Job^]: The list of all jobs.
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


def get_latest_job(task: Task) -> Optional[Job]:
    """Return the latest job of a task.

    Parameters:
        task (Task^): The task to retrieve the latest job from.
    Returns:
        Optional[Job^]: The latest job created from _task_. This is None if no job has been
            created from _task_.
    """
    return _JobManagerFactory._build_manager()._get_latest(task)


def get_data_nodes() -> List[DataNode]:
    """Return all the existing data nodes.

    Returns:
        List[DataNode^]: The list of all data nodes.
    """
    return _DataManagerFactory._build_manager()._get_all()


def get_cycles() -> List[Cycle]:
    """Return the list of all existing cycles.

    Returns:
        List[Cycle^]: The list of all cycles.
    """
    return _CycleManagerFactory._build_manager()._get_all()


def create_scenario(
    config: ScenarioConfig, creation_date: Optional[datetime] = None, name: Optional[str] = None
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
        Scenario^: The new scenario.
    """
    return _ScenarioManagerFactory._build_manager()._create(config, creation_date, name)


def create_pipeline(config: PipelineConfig) -> Pipeline:
    """Create and return a new pipeline from a pipeline configuration.

    Parameters:
        config (PipelineConfig^): The pipeline configuration.
    Returns:
        Pipeline^: The new pipeline.
    """
    return _PipelineManagerFactory._build_manager()._get_or_create(config)


def clean_all_entities() -> bool:
    """Delete all entities from the Taipy data folder.

    !!! important
        Invoking this function is only recommended for development purposes.

    Returns:
        bool: True if the operation succeeded, False otherwise.
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
    return True
