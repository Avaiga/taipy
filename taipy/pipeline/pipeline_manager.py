"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating, deleting, duplicating, executing) related
 to pipelines.
"""
import logging
from typing import Dict, List

from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.pipeline import NonExistingPipeline, NonExistingPipelineEntity
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_entity import Dag, PipelineEntity
from taipy.pipeline.pipeline_model import PipelineId, PipelineModel
from taipy.pipeline.pipeline_schema import PipelineSchema
from taipy.task.scheduler.task_scheduler import TaskScheduler
from taipy.task.task_manager import TaskManager


class PipelineManager:
    task_manager = TaskManager()
    task_scheduler = TaskScheduler()

    __PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}

    __PIPELINES: Dict[str, Pipeline] = {}

    def delete_all(self):
        self.__PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}
        self.__PIPELINES: Dict[str, Pipeline] = {}

    def register_pipeline(self, pipeline: Pipeline):
        self.__PIPELINES[pipeline.name] = pipeline

    def get_pipeline(self, name: str) -> Pipeline:
        try:
            return self.__PIPELINES[name]
        except KeyError:
            logging.error(f"Pipeline : {name} does not exist.")
            raise NonExistingPipeline(name)

    def get_pipelines(self) -> List[Pipeline]:
        return [self.get_pipeline(pipeline.name) for pipeline in list(self.__PIPELINES.values())]

    def create_pipeline_entity(self, pipeline: Pipeline) -> PipelineEntity:
        task_entities = list(map(self.task_manager.create_task_entity, pipeline.tasks))
        pipeline_entity = PipelineEntity(pipeline.name, pipeline.properties, task_entities)
        self.save_pipeline_entity(pipeline_entity)
        return pipeline_entity

    def save_pipeline_entity(self, pipeline_entity: PipelineEntity):
        for task in pipeline_entity.task_entities:
            self.task_manager.save_task_entity(task)
        self.__PIPELINE_MODEL_DB[pipeline_entity.id] = pipeline_entity.to_model()

    def get_pipeline_entity(self, pipeline_id: PipelineId) -> PipelineEntity:
        try:
            model = self.__PIPELINE_MODEL_DB[pipeline_id]
            task_entities = list(map(self.task_manager.get_task_entity, model.task_source_edges.keys()))
            return PipelineEntity(model.name, model.properties, task_entities, model.id)
        except NonExistingTaskEntity as err:
            logging.error(
                f"Task : {err.task_id} from pipeline {pipeline_id} does not exist."
            )
            raise err
        except KeyError:
            logging.error(f"Pipeline : {pipeline_id} does not exist.")
            raise NonExistingPipeline(pipeline_id)

    def get_pipeline_entities(self) -> List[PipelineEntity]:
        return [
            self.get_pipeline_entity(model.id) for model in list(self.__PIPELINE_MODEL_DB.values())
        ]

    def get_pipeline_schema(self, pipeline_id: PipelineId) -> PipelineSchema:
        try:
            model = self.__PIPELINE_MODEL_DB[pipeline_id]
            return PipelineSchema(
                model.id,
                model.name,
                model.properties,
                Dag({**model.source_task_edges, **model.task_source_edges}),
            )
        except KeyError:
            logging.error(f"Pipeline entity : {pipeline_id} does not exist.")
            raise NonExistingPipelineEntity(pipeline_id)

    def get_pipeline_schemas(self) -> List[PipelineSchema]:
        return [
            self.get_pipeline_schema(model.id) for model in list(self.__PIPELINE_MODEL_DB.values())
        ]

    def submit(self, pipeline_id: PipelineId):
        pipeline_entity_to_submit = self.get_pipeline_entity(pipeline_id)
        for tasks in pipeline_entity_to_submit.get_sorted_task_entities():
            for task in tasks:
                self.task_scheduler.submit(task)
