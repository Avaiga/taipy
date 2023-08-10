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

from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._version._version_mixin import _VersionMixin
from ..common._utils import _Subscriber
from ..common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from ..exceptions.exceptions import InvalidPipelineId, ModelNotFound, NonExistingPipeline, NonExistingTask
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..notification import EventEntityType, EventOperation, _publish_event
from ..scenario.scenario_id import ScenarioId
from ..task._task_manager_factory import _TaskManagerFactory
from ..task.task import Task, TaskId
from .pipeline import Pipeline
from .pipeline_id import PipelineId


class _PipelineManager(_Manager[Pipeline], _VersionMixin):

    _ENTITY_NAME = Pipeline.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.PIPELINE

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Pipeline]:
        """
        Returns all entities.
        """
        pipelines = set()

        from ..scenario._scenario_manager_factory import _ScenarioManagerFactory

        scenarios = _ScenarioManagerFactory._build_manager()._get_all(version_number)
        for scenario in scenarios:
            pipelines.update(scenario.pipelines.values())

        return list(pipelines)

    @classmethod
    def _subscribe(
        cls,
        callback: Callable[[Pipeline, Job], None],
        params: Optional[List[Any]] = None,
        pipeline: Optional[Pipeline] = None,
    ):
        if pipeline is None:
            pipelines = cls._get_all()
            for pln in pipelines:
                cls.__add_subscriber(callback, params, pln)
            return

        cls.__add_subscriber(callback, params, pipeline)

    @classmethod
    def _unsubscribe(
        cls,
        callback: Callable[[Pipeline, Job], None],
        params: Optional[List[Any]] = None,
        pipeline: Optional[Pipeline] = None,
    ):
        if pipeline is None:
            pipelines = cls._get_all()
            for pln in pipelines:
                cls.__remove_subscriber(callback, params, pln)
            return

        cls.__remove_subscriber(callback, params, pipeline)

    @classmethod
    def __add_subscriber(cls, callback, params, pipeline):
        pipeline._add_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, pipeline.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def __remove_subscriber(cls, callback, params, pipeline):
        pipeline._remove_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, pipeline.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def _create(
        cls,
        pipeline_name: str,
        tasks: Union[List[Task], List[TaskId]],
        subscribers: Optional[List[_Subscriber]] = None,
        properties: Optional[Dict] = None,
        scenario_id: Optional[ScenarioId] = None,
    ) -> Pipeline:
        pipeline_id = Pipeline._new_id(pipeline_name, scenario_id)

        task_manager = _TaskManagerFactory._build_manager()
        _tasks = []
        for task in tasks:
            if not isinstance(task, Task):
                if _task := task_manager._get(task):
                    _tasks.append(_task)
                else:
                    raise NonExistingTask(task)
            else:
                _tasks.append(task)

        properties = properties if properties else {}
        properties["name"] = pipeline_name
        version = cls._get_latest_version()
        pipeline = Pipeline(
            properties=properties,
            tasks=_tasks,
            pipeline_id=pipeline_id,
            owner_id=scenario_id,
            parent_ids={scenario_id} if scenario_id else None,
            subscribers=subscribers,
            version=version,
        )
        for task in _tasks:
            task._parent_ids.update([pipeline_id])
        cls.__save_tasks(_tasks)
        _publish_event(cls._EVENT_ENTITY_TYPE, pipeline.id, EventOperation.CREATION, None)
        return pipeline

    @classmethod
    def _get(cls, pipeline: Union[str, Pipeline], default=None) -> Pipeline:
        """
        Returns a pipeline by id or reference.
        """
        try:
            pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
            pipeline_name, scenario_id = cls._breakdown_pipeline_id(pipeline_id)

            from ..scenario._scenario_manager_factory import _ScenarioManagerFactory

            scenario_manager = _ScenarioManagerFactory._build_manager()

            if scenario := scenario_manager._get(scenario_id):
                if pipeline_entity := scenario.pipelines.get(pipeline_name, None):
                    return pipeline_entity
            return default

        except (ModelNotFound, InvalidPipelineId):
            cls._logger.error(f"{cls._ENTITY_NAME} not found: {pipeline_id}")
            return default

    @classmethod
    def _set(cls, pipeline: Pipeline):
        """
        Save or update a pipeline.
        """
        try:
            pipeline_name, scenario_id = cls._breakdown_pipeline_id(pipeline.id)

            from ..scenario._scenario_manager_factory import _ScenarioManagerFactory
            from ..scenario.scenario import Scenario

            scenario_manager = _ScenarioManagerFactory._build_manager()

            if scenario := scenario_manager._get(scenario_id):
                pipeline_data = {
                    Scenario._PIPELINE_TASKS_KEY: pipeline._tasks,
                    Scenario._PIPELINE_SUBSCRIBERS_KEY: pipeline._subscribers,
                    Scenario._PIPELINE_PROPERTIES_KEY: pipeline._properties.data,
                }
                scenario._pipelines[pipeline_name] = pipeline_data  # type: ignore
                scenario_manager._set(scenario)
            else:
                # TODO: raise error and add test cases
                pass

        except (ModelNotFound, InvalidPipelineId):
            # cls._logger.error(f"{cls._ENTITY_NAME} not found: {pipeline_id}")
            pass

    @classmethod
    def _breakdown_pipeline_id(cls, pipeline_id: str) -> Tuple[str, str]:
        from ..scenario.scenario import Scenario

        try:
            pipeline_name, scenario_id = pipeline_id.split(Scenario._ID_PREFIX)
            scenario_id = f"{Scenario._ID_PREFIX}{scenario_id}"
            pipeline_name = pipeline_name.split(Pipeline._ID_PREFIX)[1].strip("_")
            return pipeline_name, scenario_id
        except ValueError:
            raise InvalidPipelineId(pipeline_id)

    @classmethod
    def __save_tasks(cls, tasks):
        task_manager = _TaskManagerFactory._build_manager()
        for i in tasks:
            task_manager._set(i)

    @classmethod
    def _is_submittable(cls, pipeline: Union[Pipeline, PipelineId]) -> bool:
        if isinstance(pipeline, str):
            pipeline = cls._get(pipeline)
        return isinstance(pipeline, Pipeline)

    @classmethod
    def _submit(
        cls,
        pipeline: Union[PipelineId, Pipeline],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        check_inputs_are_ready: bool = True,
    ) -> List[Job]:
        pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
        pipeline = cls._get(pipeline_id)
        if pipeline is None:
            raise NonExistingPipeline(pipeline_id)
        callbacks = callbacks or []
        pipeline_subscription_callback = cls.__get_status_notifier_callbacks(pipeline) + callbacks
        if check_inputs_are_ready:
            _warn_if_inputs_not_ready(pipeline.get_inputs())

        jobs = (
            _TaskManagerFactory._build_manager()
            ._orchestrator()
            .submit(pipeline, callbacks=pipeline_subscription_callback, force=force, wait=wait, timeout=timeout)
        )
        _publish_event(cls._EVENT_ENTITY_TYPE, pipeline.id, EventOperation.SUBMISSION, None)
        return jobs

    @staticmethod
    def __get_status_notifier_callbacks(pipeline: Pipeline) -> List:
        return [partial(c.callback, *c.params, pipeline) for c in pipeline.subscribers]

    @classmethod
    def _hard_delete(cls, pipeline_id: PipelineId):
        pipeline = cls._get(pipeline_id)
        entity_ids_to_delete = cls._get_children_entity_ids(pipeline)
        entity_ids_to_delete.pipeline_ids.add(pipeline.id)
        cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _get_children_entity_ids(cls, pipeline: Pipeline) -> _EntityIds:
        entity_ids = _EntityIds()
        for task in pipeline.tasks.values():
            if not isinstance(task, Task):
                task = _TaskManagerFactory._build_manager()._get(task)
            if task.owner_id == pipeline.id:
                entity_ids.task_ids.add(task.id)
            for data_node in task.data_nodes.values():
                if data_node.owner_id == pipeline.id:
                    entity_ids.data_node_ids.add(data_node.id)
        jobs = _JobManagerFactory._build_manager()._get_all()
        for job in jobs:
            if job.task.id in entity_ids.task_ids:
                entity_ids.job_ids.add(job.id)
        return entity_ids
