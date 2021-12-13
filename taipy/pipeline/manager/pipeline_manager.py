import logging
from functools import partial
from typing import Callable, List, Optional, Set

from taipy.common.alias import PipelineId, ScenarioId
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
    """
    The Pipeline Manager is responsible for managing all pipeline-related capabilities.
    """

    task_manager = TaskManager()
    data_manager = task_manager.data_manager
    task_scheduler = task_manager.task_scheduler
    __status_notifier: Set[Callable] = set()

    def __init__(self):
        """
        Initializes a new pipeline manager.
        """
        self.repository = PipelineRepository(model=PipelineModel, dir_name="pipelines")

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
        """
        Deletes all data sources.
        """
        self.repository.delete_all()

    def get_or_create(self, pipeline_config: PipelineConfig, scenario_id: Optional[ScenarioId] = None) -> Pipeline:
        """
        Returns a pipeline created from the pipeline configuration.

        created from the pipeline_config, by scenario_id if it already
        exists, or creates and returns a new pipeline.

        Parameters:
            pipeline_config (PipelineConfig): The pipeline configuration object.
            scenario_id (Optional[ScenarioId]): id of the scenario creating the pipeline. Default value : `None`.
        Raises:
            MultiplePipelineFromSameConfigWithSameParent: if more than one pipeline already exists with the
                same config, and the same parent id (scenario_id, or pipeline_id depending on the scope of
                the data source).
        """
        pipeline_id = Pipeline.new_id(pipeline_config.name)
        tasks = [
            self.task_manager.get_or_create(t_config, scenario_id, pipeline_id)
            for t_config in pipeline_config.tasks_configs
        ]
        scope = min(task.scope for task in tasks) if len(tasks) != 0 else Scope.GLOBAL
        parent_id = scenario_id if scope == Scope.SCENARIO else pipeline_id if scope == Scope.PIPELINE else None
        pipelines_from_config_name = self._get_all_by_config_name(pipeline_config.name)
        pipelines_from_parent = [pipeline for pipeline in pipelines_from_config_name if pipeline.parent_id == parent_id]
        if len(pipelines_from_parent) == 1:
            return pipelines_from_parent[0]
        elif len(pipelines_from_parent) > 1:
            logging.error("Multiple pipelines from same config exist with the same parent_id.")
            raise MultiplePipelineFromSameConfigWithSameParent
        else:
            pipeline = Pipeline(pipeline_config.name, pipeline_config.properties, tasks, pipeline_id, parent_id)
            self.set(pipeline)
            return pipeline

    def set(self, pipeline: Pipeline):
        """
        Saves or updates a pipeline.

        Parameters:
            pipeline (Pipeline): the pipeline to save or update.
        """
        self.repository.save(pipeline)

    def get(self, pipeline_id: PipelineId) -> Pipeline:
        """
        Gets a pipeline.

        Parameters:
            pipeline_id (PipelineId): pipeline identifier or the pipeline to get.

        Raises:
            NonExistingPipeline: if no pipeline corresponds to `pipeline_id`.
        """
        try:
            return self.repository.load(pipeline_id)
        except ModelNotFound:
            raise NonExistingPipeline(pipeline_id)

    def get_all(self) -> List[Pipeline]:
        """
        Returns all existing pipelines.

        Returns:
            List[Pipeline]: the list of all pipelines managed by this pipeline manager.
        """
        return self.repository.load_all()

    def submit(self, pipeline_id: PipelineId, callbacks: Optional[List[Callable]] = None):
        callbacks = callbacks or []
        pipeline_to_submit = self.get(pipeline_id)
        pipeline_subscription_callback = self.__get_status_notifier_callbacks(pipeline_to_submit) + callbacks
        for tasks in pipeline_to_submit.get_sorted_tasks():
            for task in tasks:
                self.task_scheduler.submit(task, pipeline_subscription_callback)

    def __get_status_notifier_callbacks(self, pipeline: Pipeline) -> List:
        return [partial(c, pipeline) for c in pipeline.subscribers]

    def _get_all_by_config_name(self, config_name: str) -> List[Pipeline]:
        """
        Returns all the existing pipelines for a configuration.

        Parameters:
            config_name (str): The pipeline configuration name to be looked for.
        Returns:
            List[Pipeline]: the list of all pipelines, managed by this pipeline manager,
                that use the indicated configuration name.
        """
        return self.repository.search_all("config_name", config_name)
