"""
Pipeline Manager is responsible for managing the pipelines.
This is the entry point for operations (such as creating, reading, updating,
deleting, duplicating, executing) related to pipelines.
"""
import logging
from typing import Callable, Dict, Iterable, List, Optional, Set

from taipy.data import DataSource
from taipy.data.data_source_config import DataSourceConfig
from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipeline, NonExistingPipelineConfig
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.pipeline_config import PipelineConfig
from taipy.pipeline.pipeline_model import PipelineId, PipelineModel
from taipy.task import TaskId
from taipy.task.manager.task_manager import TaskManager
from taipy.task.scheduler.task_scheduler import TaskScheduler


class PipelineManager:
    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = TaskScheduler()

    __PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}
    __PIPELINE_CONFIGS_DB: Dict[str, PipelineConfig] = {}

    def delete_all(self):
        self.__PIPELINE_MODEL_DB: Dict[PipelineId, PipelineModel] = {}
        self.__PIPELINE_CONFIGS_DB: Dict[str, PipelineConfig] = {}

    def register(self, pipeline_config: PipelineConfig):
        [self.task_manager.register(task_config) for task_config in pipeline_config.tasks]
        self.__PIPELINE_CONFIGS_DB[pipeline_config.name] = pipeline_config

    def get_pipeline_config(self, config_name: str) -> PipelineConfig:
        try:
            return self.__PIPELINE_CONFIGS_DB[config_name]
        except KeyError:
            err = NonExistingPipelineConfig(config_name)
            logging.error(err.message)
            raise err

    def get_pipeline_configs(self) -> Iterable[PipelineConfig]:
        return self.__PIPELINE_CONFIGS_DB.values()

    def create(
        self,
        pipeline_config: PipelineConfig,
        data_sources: Dict[DataSourceConfig, DataSource] = None,
    ) -> Pipeline:
        if data_sources is None:
            all_ds_configs: Set[DataSourceConfig] = set()
            for task_config in pipeline_config.tasks:
                for ds_config in task_config.input:
                    all_ds_configs.add(ds_config)
                for ds_config in task_config.output:
                    all_ds_configs.add(ds_config)
            data_sources = {ds_config: self.data_manager.create_data_source(ds_config) for ds_config in all_ds_configs}
        tasks = [self.task_manager.create(task_config, data_sources) for task_config in pipeline_config.tasks]
        pipeline = Pipeline(pipeline_config.name, pipeline_config.properties, tasks)
        self.save(pipeline)
        return pipeline

    def save(self, pipeline: Pipeline):
        self.__PIPELINE_MODEL_DB[pipeline.id] = pipeline.to_model()

    def get_pipeline(self, pipeline_id: PipelineId) -> Pipeline:
        try:
            model = self.__PIPELINE_MODEL_DB[pipeline_id]
            tasks = [self.task_manager.get_task(TaskId(task_id)) for task_id in model.task_source_edges.keys()]
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
