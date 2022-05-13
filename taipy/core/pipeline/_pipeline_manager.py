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

from functools import partial
from typing import Callable, List, Optional, Union

from taipy.core._manager._manager import _Manager
from taipy.core.common._entity_ids import _EntityIds
from taipy.core.common.alias import PipelineId, ScenarioId
from taipy.core.common.scope import Scope
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.exceptions.exceptions import NonExistingPipeline
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job
from taipy.core.pipeline._pipeline_repository import _PipelineRepository
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task._task_manager import _TaskManager


class _PipelineManager(_Manager[Pipeline]):
    _repository = _PipelineRepository()
    _ENTITY_NAME = Pipeline.__name__

    @classmethod
    def _subscribe(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        if pipeline is None:
            pipelines = cls._get_all()
            for pln in pipelines:
                cls.__add_subscriber(callback, pln)
            return

        cls.__add_subscriber(callback, pipeline)

    @classmethod
    def _unsubscribe(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):

        if pipeline is None:
            pipelines = cls._get_all()
            for pln in pipelines:
                cls.__remove_subscriber(callback, pln)
            return

        cls.__remove_subscriber(callback, pipeline)

    @classmethod
    def __add_subscriber(cls, callback, pipeline):
        pipeline._add_subscriber(callback)
        cls._set(pipeline)

    @classmethod
    def __remove_subscriber(cls, callback, pipeline):
        pipeline._remove_subscriber(callback)
        cls._set(pipeline)

    @classmethod
    def _get_or_create(cls, pipeline_config: PipelineConfig, scenario_id: Optional[ScenarioId] = None) -> Pipeline:
        pipeline_id = Pipeline._new_id(pipeline_config.id)
        tasks = [
            _TaskManager._get_or_create(t_config, scenario_id, pipeline_id) for t_config in pipeline_config.task_configs
        ]
        scope = min(task.scope for task in tasks) if len(tasks) != 0 else Scope.GLOBAL
        parent_id = scenario_id if scope == Scope.SCENARIO else pipeline_id if scope == Scope.PIPELINE else None

        if pipelines_from_parent := cls._repository._get_by_config_and_parent_ids(pipeline_config.id, parent_id):
            return pipelines_from_parent

        pipeline = Pipeline(pipeline_config.id, dict(**pipeline_config.properties), tasks, pipeline_id, parent_id)
        cls._set(pipeline)
        return pipeline

    @classmethod
    def _submit(
        cls, pipeline: Union[PipelineId, Pipeline], callbacks: Optional[List[Callable]] = None, force: bool = False
    ):
        callbacks = callbacks or []
        pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
        pipeline = cls._get(pipeline_id)
        if pipeline is None:
            raise NonExistingPipeline(pipeline_id)
        pipeline_subscription_callback = cls.__get_status_notifier_callbacks(pipeline) + callbacks
        _TaskManager._scheduler().submit(pipeline, callbacks=pipeline_subscription_callback, force=force)

    @staticmethod
    def __get_status_notifier_callbacks(pipeline: Pipeline) -> List:
        return [partial(c, pipeline) for c in pipeline.subscribers]

    @classmethod
    def _hard_delete(cls, pipeline_id: PipelineId):
        pipeline = cls._get(pipeline_id)
        entity_ids_to_delete = cls._get_owned_entity_ids(pipeline)
        entity_ids_to_delete.pipeline_ids.add(pipeline.id)
        cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _get_owned_entity_ids(cls, pipeline: Pipeline) -> _EntityIds:
        entity_ids = _EntityIds()
        for task in pipeline._tasks.values():
            if task.parent_id == pipeline.id:
                entity_ids.task_ids.add(task.id)
            for data_node in task.data_nodes.values():
                if data_node.parent_id == pipeline.id:
                    entity_ids.data_node_ids.add(data_node.id)
        jobs = _JobManager._get_all()
        for job in jobs:
            if job.task.id in entity_ids.task_ids:
                entity_ids.job_ids.add(job.id)
        return entity_ids
