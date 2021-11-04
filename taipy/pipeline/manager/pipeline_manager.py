"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related to pipelines.
"""
from functools import partial
from typing import Callable, Iterable, List, Optional, Set

from taipy.common.alias import PipelineId
from taipy.config import PipelineConfig
from taipy.exceptions import ModelNotFound
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.repository import PipelineRepository
from taipy.task import Job
from taipy.task.manager.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = TaskScheduler()

    def __init__(self):
        self.repository = PipelineRepository(model=PipelineModel, dir_name="pipelines")

    __status_notifier: Set[Callable] = set()

    def subscribe(self, callback: Callable[[Pipeline, Job], None]):
        """
        Subscribe a function to be called when the status of a Job changes

        Note:
            - Notification will be available only for Jobs created after this subscription
        """
        self.__status_notifier.add(callback)

    def unsubscribe(self, callback: Callable[[Pipeline, Job], None]):
        """
        Unsubscribe a function called when the status of a Job changes

        Note:
            - The function will continue to be called for ongoing Jobs
        """
        self.__status_notifier.remove(callback)

    def delete_all(self):
        self.repository.delete_all()

    def create(self, config: PipelineConfig, scenario_id: Optional[str] = None) -> Pipeline:
        pipeline_id = Pipeline.new_id(config.name)
        tasks = [self.task_manager.create(t_config, scenario_id, pipeline_id) for t_config in config.tasks_configs]
        pipeline = Pipeline(config.name, config.properties, tasks, pipeline_id)
        self.set(pipeline)
        return pipeline

    def set(self, pipeline: Pipeline):
        self.repository.save(pipeline)

    def get(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            return self.repository.load(pipeline_id)
        except ModelNotFound:
            raise NonExistingPipeline(pipeline_id)

    def get_all(self) -> Iterable[Pipeline]:
        return self.repository.load_all()

    def submit(self, pipeline_id: PipelineId, callbacks: Optional[List[Callable]] = None):
        callbacks = callbacks or []
        pipeline_to_submit = self.get(pipeline_id)
        pipeline_subscription_callback = self.__get_status_notifier_callbacks(pipeline_to_submit) + callbacks
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task, pipeline_subscription_callback)

    def __get_status_notifier_callbacks(self, pipeline: Pipeline) -> List:
        return [partial(c, pipeline) for c in self.__status_notifier]
