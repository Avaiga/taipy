import logging
from functools import partial
from typing import Callable, List, Optional, Union

from taipy.common.alias import PipelineId, ScenarioId
from taipy.config.pipeline_config import PipelineConfig
from taipy.data import Scope
from taipy.exceptions import ModelNotFound
from taipy.exceptions.pipeline import MultiplePipelineFromSameConfigWithSameParent, NonExistingPipeline
from taipy.job import Job
from taipy.pipeline.pipeline import Pipeline
from taipy.pipeline.repository import PipelineRepository
from taipy.scheduler.abstract_scheduler import AbstractScheduler
from taipy.task.manager.task_manager import TaskManager


class PipelineManager:
    """
    The Pipeline Manager is responsible for managing all pipeline-related capabilities.
    """

    task_manager = TaskManager()
    repository = PipelineRepository()

    @property
    def scheduler(self) -> AbstractScheduler:
        return self.task_manager.scheduler

    def subscribe(self, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Subscribes a function to be called when the status of a Job changes.
        If pipeline is not passed, the subscription is added to all pipelines.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        if pipeline is None:
            pipelines = self.get_all()
            for pln in pipelines:
                self.__add_subscriber(callback, pln)
            return

        self.__add_subscriber(callback, pipeline)

    def unsubscribe(self, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If pipeline is not passed, the subscription is removed to all pipelines.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        if pipeline is None:
            pipelines = self.get_all()
            for pln in pipelines:
                self.__remove_subscriber(callback, pln)
            return

        self.__remove_subscriber(callback, pipeline)

    def __add_subscriber(self, callback, pipeline):
        pipeline.add_subscriber(callback)
        self.set(pipeline)

    def __remove_subscriber(self, callback, pipeline):
        pipeline.remove_subscriber(callback)
        self.set(pipeline)

    def delete_all(self):
        """
        Deletes all data sources.
        """
        self.repository.delete_all()

    def delete(self, pipeline_id: PipelineId):
        """Deletes the pipeline provided as parameter.

        Parameters:
            pipeline_id (str): identifier of the pipeline to delete.
        Raises:
            ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        self.repository.delete(pipeline_id)

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

    def get(self, pipeline: Union[Pipeline, PipelineId]) -> Pipeline:
        """
        Gets a pipeline.

        Parameters:
            pipeline (Union[Pipeline, PipelineId]): pipeline identifier or the pipeline to get.

        Raises:
            NonExistingPipeline: if no pipeline corresponds to `pipeline_id`.
        """
        try:
            pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
            return self.repository.load(pipeline_id)
        except ModelNotFound:
            logging.error(f"Pipeline entity: {pipeline_id} does not exist.")
            raise NonExistingPipeline(pipeline_id)

    def get_all(self) -> List[Pipeline]:
        """
        Returns all existing pipelines.

        Returns:
            List[Pipeline]: the list of all pipelines managed by this pipeline manager.
        """
        return self.repository.load_all()

    def submit(self, pipeline: Union[PipelineId, Pipeline], callbacks: Optional[List[Callable]] = None):
        """
        Submits the pipeline corresponding to the pipeline or the identifier given as parameter for execution.

        All the tasks of pipeline will be submitted for execution.

        Parameters:
            pipeline (Union[PipelineId, Pipeline]): the pipeline or its id to submit.
        """
        callbacks = callbacks or []
        if isinstance(pipeline, Pipeline):
            pipeline = self.get(pipeline.id)
        else:
            pipeline = self.get(pipeline)
        pipeline_subscription_callback = self.__get_status_notifier_callbacks(pipeline) + callbacks
        self.scheduler.submit(pipeline, pipeline_subscription_callback)

    @staticmethod
    def __get_status_notifier_callbacks(pipeline: Pipeline) -> List:
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

    def hard_delete(self, pipeline_id: PipelineId, scenario_id: Optional[ScenarioId] = None):
        """
        Deletes the pipeline given as parameter and the nested tasks, data sources, and jobs.

        Deletes the pipeline given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested task if the task is not shared by another pipeline or if a scenario id is given as parameter, by another
        scenario.

        Parameters:
        pipeline_id (PipelineId) : identifier of the pipeline to hard delete.
        scenario_id (ScenarioId) : identifier of the optional parent scenario.

        Raises:
        ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        pipeline = self.get(pipeline_id)
        for task in pipeline.tasks.values():
            if scenario_id and task.parent_id == scenario_id:
                self.task_manager.hard_delete(task.id, scenario_id)
            elif task.parent_id == pipeline.id:
                self.task_manager.hard_delete(task.id, None, pipeline_id)
        self.delete(pipeline_id)
