"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related
 to pipelines.
"""
import logging
from typing import Dict, List, Set

from taipy.data import DataSourceEntity
from taipy.data.data_source import DataSource
from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.pipeline import (
    NonExistingDataSourceEntity,
    NonExistingPipeline,
    NonExistingPipelineEntity,
)
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_entity import PipelineEntity
from taipy.pipeline.pipeline_model import PipelineId, PipelineModel
from taipy.task import TaskId
from taipy.task.manager.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = TaskScheduler()

    __PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}

    __PIPELINES: Dict[str, Pipeline] = {}

    def delete_all(self):
        self.__PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}
        self.__PIPELINES: Dict[str, Pipeline] = {}

    def register_pipeline(self, pipeline: Pipeline):
        [self.task_manager.register_task(task) for task in pipeline.tasks]
        self.__PIPELINES[pipeline.name] = pipeline

    def get_pipeline(self, name: str) -> Pipeline:
        try:
            return self.__PIPELINES[name]
        except KeyError:
            err = NonExistingPipeline(name)
            logging.error(err.message)
            raise err

    def get_pipelines(self) -> List[Pipeline]:
        return [
            self.get_pipeline(pipeline.name) for pipeline in self.__PIPELINES.values()
        ]

    def create_pipeline_entity(
        self,
        pipeline: Pipeline,
        data_source_entities: Dict[DataSource, DataSourceEntity] = None,
    ) -> PipelineEntity:
        if data_source_entities is None:
            all_ds: Set[DataSource] = set()
            for task in pipeline.tasks:
                for ds in task.input:
                    all_ds.add(ds)
                for ds in task.output:
                    all_ds.add(ds)
            data_source_entities = {
                ds: self.data_manager.create_data_source_entity(ds) for ds in all_ds
            }
        task_entities = [
            self.task_manager.create_task_entity(task, data_source_entities)
            for task in pipeline.tasks
        ]
        pipeline_entity = PipelineEntity(
            pipeline.name, pipeline.properties, task_entities
        )
        self.save_pipeline_entity(pipeline_entity)
        return pipeline_entity

    def save_pipeline_entity(self, pipeline_entity: PipelineEntity):
        self.__PIPELINE_MODEL_DB[pipeline_entity.id] = pipeline_entity.to_model()

    def get_pipeline_entity(self, pipeline_id: PipelineId) -> PipelineEntity:
        try:
            model = self.__PIPELINE_MODEL_DB[pipeline_id]
            task_entities = [
                self.task_manager.get_task_entity(TaskId(task_id))
                for task_id in model.task_source_edges.keys()
            ]
            return PipelineEntity(model.name, model.properties, task_entities, model.id)
        except NonExistingTaskEntity as err:
            logging.error(err.message)
            raise err
        except KeyError:
            pipeline_err = NonExistingPipelineEntity(pipeline_id)
            logging.error(pipeline_err.message)
            raise pipeline_err

    def get_pipeline_entities(self) -> List[PipelineEntity]:
        return [
            self.get_pipeline_entity(model.id)
            for model in self.__PIPELINE_MODEL_DB.values()
        ]

    def submit(self, pipeline_id: PipelineId):
        pipeline_entity_to_submit = self.get_pipeline_entity(pipeline_id)
        for tasks in pipeline_entity_to_submit.get_sorted_task_entities():
            for task in tasks:
                self.task_scheduler.submit(task)

    def get_data(self, data_source_name: str, pipeline_id: PipelineId):
        pipeline_entity = self.get_pipeline_entity(pipeline_id)
        for task in pipeline_entity.task_entities:
            for ds_entity in task.input.values():
                if ds_entity.name == data_source_name:
                    return ds_entity.get()
            for ds_entity in task.output.values():
                if ds_entity.name == data_source_name:
                    return ds_entity.get()
        raise NonExistingDataSourceEntity(pipeline_id, data_source_name)

    def set_data(self, data_source_name: str, pipeline_id: PipelineId, data):
        pipeline_entity = self.get_pipeline_entity(pipeline_id)
        for task in pipeline_entity.task_entities:
            for ds_entity in task.input.values():
                if ds_entity.name == data_source_name:
                    return ds_entity.write(data)
            for ds_entity in task.output.values():
                if ds_entity.name == data_source_name:
                    return ds_entity.write(data)
        raise NonExistingDataSourceEntity(pipeline_id, data_source_name)
