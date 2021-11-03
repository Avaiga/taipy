"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related to pipelines.
"""
from typing import Callable, Iterable, List, Optional

from taipy.common.alias import PipelineId
from taipy.config import PipelineConfig
from taipy.exceptions import ModelNotFound
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.repository import PipelineRepository
from taipy.task.manager.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = TaskScheduler()

    def __init__(self):
        self.repository = PipelineRepository(model=PipelineModel, dir_name="pipelines")

    def delete_all(self):
        self.repository.delete_all()

    def create(self, config: PipelineConfig, scenario_id: Optional[str] = None) -> Pipeline:
        pipeline_id = Pipeline.new_id(config.name)
        tasks = [self.task_manager.create(t_config, scenario_id, pipeline_id) for t_config in config.tasks_configs]
        pipeline = Pipeline(config.name, config.properties, tasks, pipeline_id)
        self.save(pipeline)
        return pipeline

    def save(self, pipeline: Pipeline):
        self.repository.save(pipeline)

    def get_pipeline(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            return self.repository.load(pipeline_id)
        except ModelNotFound:
            raise NonExistingPipeline(pipeline_id)

    def get_pipelines(self) -> Iterable[Pipeline]:
        return self.repository.load_all()

    def submit(self, pipeline_id: PipelineId, callbacks: Optional[List[Callable]] = None):
        pipeline_to_submit = self.get_pipeline(pipeline_id)
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task, callbacks)
