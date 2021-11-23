"""
The Pipeline Manager is responsible for managing the pipelines.

This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related to pipelines.
"""

import logging
from functools import partial
from typing import Callable, Iterable, List, Optional, Set

from taipy.common.alias import PipelineId
from taipy.config import PipelineConfig
from taipy.data import Scope
from taipy.exceptions import ModelNotFound
from taipy.exceptions.pipeline import MultiplePipelineFromSameConfigWithSameParent, NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.repository import PipelineRepository
from taipy.task import Job
from taipy.task.manager.task_manager import TaskManager


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = task_manager.task_scheduler

    def __init__(self):
        self.repository = PipelineRepository(model=PipelineModel, dir_name="pipelines")

    __status_notifier: Set[Callable] = set()

    def subscribe(self, callback: Callable[[Pipeline, Job], None], pipeline: Pipeline):
        """
        Subscribes a function to be called when the status of a Job changes.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        pipeline.add_subscriber(callback)
        self.set(pipeline)

    def unsubscribe(self, callback: Callable[[Pipeline, Job], None], pipeline: Pipeline):
        """
        Unsubscribes a function that is called when the status of a Job changes.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        pipeline.remove_subscriber(callback)
        self.set(pipeline)

    def delete_all(self):
        self.repository.delete_all()

    def get_or_create(self, config: PipelineConfig, scenario_id: Optional[str] = None) -> Pipeline:
        pipeline_id = Pipeline.new_id(config.name)
        tasks = [
            self.task_manager.get_or_create(t_config, scenario_id, pipeline_id) for t_config in config.tasks_configs
        ]
        scope = min(task.scope for task in tasks) if len(tasks) != 0 else Scope.GLOBAL
        parent_id = scenario_id if scope == Scope.SCENARIO else pipeline_id if scope == Scope.PIPELINE else None
        pipelines_from_config_name = self._get_all_by_config_name(config.name)
        pipelines_from_parent = [pipeline for pipeline in pipelines_from_config_name if pipeline.parent_id == parent_id]
        if len(pipelines_from_parent) == 1:
            return pipelines_from_parent[0]
        elif len(pipelines_from_parent) > 1:
            logging.error("Multiple pipelines from same config exist with the same parent_id.")
            raise MultiplePipelineFromSameConfigWithSameParent
        else:
            pipeline = Pipeline(config.name, config.properties, tasks, pipeline_id, parent_id)
            self.set(pipeline)
            return pipeline

    def set(self, pipeline: Pipeline):
        self.repository.save(pipeline)

    def get(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            return self.repository.load(pipeline_id)
        except ModelNotFound:
            raise NonExistingPipeline(pipeline_id)

    def get_all(self) -> List[Pipeline]:
        return self.repository.load_all()

    def submit(self, pipeline_id: PipelineId, callbacks: Optional[List[Callable]] = None):
        callbacks = callbacks or []
        pipeline_to_submit = self.get(pipeline_id)
        pipeline_subscription_callback = list(pipeline_to_submit.subscribers) + callbacks
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task, pipeline_subscription_callback)

    def __get_status_notifier_callbacks(self, pipeline: Pipeline) -> List:
        return [partial(c, pipeline) for c in self.__status_notifier]

    def _get_all_by_config_name(self, config_name: str) -> List[Pipeline]:
        return self.repository.search_all("config_name", config_name)
