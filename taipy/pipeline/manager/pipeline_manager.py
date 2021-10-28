"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related to pipelines.
"""
import logging
from typing import Callable, Dict, Iterable, List, Optional

from taipy.common.alias import PipelineId, TaskId
from taipy.config import PipelineConfig
from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.task.manager.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = TaskScheduler()

    __PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}

    def delete_all(self):
        self.__PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}

    def create(self, config: PipelineConfig, scenario_id: Optional[str] = None) -> Pipeline:
        pipeline_id = Pipeline.new_id(config.name)
        tasks = [self.task_manager.create(t_config, scenario_id, pipeline_id) for t_config in config.tasks_configs]
        pipeline = Pipeline(config.name, config.properties, tasks, pipeline_id)
        self.save(pipeline)
        return pipeline

    def save(self, pipeline: Pipeline):
        self.__PIPELINE_MODEL_DB[pipeline.id] = pipeline.to_model()

    def get_pipeline(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            model = self.__PIPELINE_MODEL_DB[pipeline_id]
            tasks = [self.task_manager.get(TaskId(task_id)) for task_id in model.task_source_edges.keys()]
            return Pipeline(model.name, model.properties, tasks, model.id)
        except NonExistingTask as err:
            logging.error(err.message)
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(pipeline_id)
            logging.error(pipeline_err.message)
            raise pipeline_err

    def get_pipelines(self) -> Iterable[Pipeline]:
        return [self.get_pipeline(model.id) for model in self.__PIPELINE_MODEL_DB.values()]

    def submit(self, pipeline_id: PipelineId, callbacks: Optional[List[Callable]] = None):
        pipeline_to_submit = self.get_pipeline(pipeline_id)
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task, callbacks)
