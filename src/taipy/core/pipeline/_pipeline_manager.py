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
from typing import Any, Callable, List, Optional, Union

from taipy.config import Config
from taipy.config.common.scope import Scope

from .._manager._manager import _Manager
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._entity_ids import _EntityIds
from ..common.alias import CycleId, PipelineId, ScenarioId
from ..config.pipeline_config import PipelineConfig
from ..exceptions.exceptions import NonExistingPipeline
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..task._task_manager_factory import _TaskManagerFactory
from ..task.task import Task
from ._pipeline_repository_factory import _PipelineRepositoryFactory
from .pipeline import Pipeline


class _PipelineManager(_Manager[Pipeline]):
    _repository = _PipelineRepositoryFactory._build_repository()  # type: ignore
    _ENTITY_NAME = Pipeline.__name__

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
        cls._set(pipeline)

    @classmethod
    def __remove_subscriber(cls, callback, params, pipeline):
        pipeline._remove_subscriber(callback, params)
        cls._set(pipeline)

    @classmethod
    def _get_or_create(
        cls,
        pipeline_config: PipelineConfig,
        cycle_id: Optional[CycleId] = None,
        scenario_id: Optional[ScenarioId] = None,
    ) -> Pipeline:
        pipeline_id = Pipeline._new_id(str(pipeline_config.id))  # type: ignore

        task_manager = _TaskManagerFactory._build_manager()
        tasks = task_manager._bulk_get_or_create(pipeline_config.task_configs, cycle_id, scenario_id, pipeline_id)

        scope = min(task.scope for task in tasks) if len(tasks) != 0 else Scope.GLOBAL
        owner_id: Union[Optional[PipelineId], Optional[ScenarioId], Optional[CycleId]]
        if scope == Scope.PIPELINE:
            owner_id = pipeline_id
        elif scope == Scope.SCENARIO:
            owner_id = scenario_id
        elif scope == Scope.CYCLE:
            owner_id = cycle_id
        else:
            owner_id = None

        if pipelines_from_owner := cls._repository._get_by_config_and_owner_id(str(pipeline_config.id), owner_id):
            return pipelines_from_owner

        version = _VersionManagerFactory._build_manager()._get_latest_version()
        pipeline = Pipeline(
            str(pipeline_config.id),  # type: ignore
            dict(**pipeline_config._properties),
            tasks,
            pipeline_id,
            owner_id,
            {scenario_id} if scenario_id else None,
            version=version,
        )
        for task in tasks:
            task._parent_ids.update([pipeline_id])
        cls.__save_tasks(tasks)
        cls._set(pipeline)
        return pipeline

    @classmethod
    def __save_tasks(cls, tasks):
        task_manager = _TaskManagerFactory._build_manager()
        for i in tasks:
            task_manager._set(i)

    @classmethod
    def _submit(
        cls,
        pipeline: Union[PipelineId, Pipeline],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ):
        callbacks = callbacks or []
        pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
        pipeline = cls._get(pipeline_id)
        if pipeline is None:
            raise NonExistingPipeline(pipeline_id)
        pipeline_subscription_callback = cls.__get_status_notifier_callbacks(pipeline) + callbacks
        return (
            _TaskManagerFactory._build_manager()
            ._scheduler()
            .submit(pipeline, callbacks=pipeline_subscription_callback, force=force, wait=wait, timeout=timeout)
        )

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
