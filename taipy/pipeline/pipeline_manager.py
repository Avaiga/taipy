"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating, deleting, duplicating, executing) related
 to pipelines.
"""
import logging
from typing import Dict, List

from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.pipeline.pipeline import Pipeline, Dag
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.pipeline_schema import PipelineSchema
from taipy.pipeline import PipelineId
from taipy.task.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    task_scheduler = TaskScheduler()

    __PIPELINE_DB: Dict[PipelineId, PipelineModel] = {}

    def delete_all(self):
        self.__PIPELINE_DB: Dict[(PipelineId, PipelineModel)] = {}

    def save_pipeline(self, pipeline: Pipeline):
        for task in pipeline.tasks:
            self.task_manager.save_task(task)
        self.__PIPELINE_DB[pipeline.id] = pipeline.to_model()

    def get_pipeline_schema(self, pipeline_id: PipelineId) -> PipelineSchema:
        try:
            model = self.__PIPELINE_DB[pipeline_id]
            return PipelineSchema(
                model.id,
                model.name,
                model.properties,
                Dag({**model.source_task_edges, **model.task_source_edges}),
            )
        except KeyError:
            logging.error(f"Pipeline : {pipeline_id} does not exist.")
            raise NonExistingPipeline(pipeline_id)

    def get_pipeline(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            model = self.__PIPELINE_DB[pipeline_id]
            tasks = list(
                map(self.task_manager.get_task, model.task_source_edges.keys())
            )
            return Pipeline(model.id, model.name, model.properties, tasks)
        except NonExistingTask as err:
            logging.error(
                f"Task : {err.task_id} from pipeline {pipeline_id} does not exist."
            )
            raise err
        except KeyError:
            logging.error(f"Pipeline : {pipeline_id} does not exist.")
            raise NonExistingPipeline(pipeline_id)

    def get_pipelines(self) -> List[Pipeline]:
        return [
            self.get_pipeline(model.id) for model in list(self.__PIPELINE_DB.values())
        ]

    def submit(self, pipeline_id: PipelineId):
        pipeline_to_submit = self.get_pipeline(pipeline_id)
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task)
