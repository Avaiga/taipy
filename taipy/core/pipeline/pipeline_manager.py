import logging
from functools import partial
from typing import Callable, List, Optional, Union

from taipy.core.common.alias import PipelineId, ScenarioId
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.data.scope import Scope
from taipy.core.exceptions import ModelNotFound
from taipy.core.exceptions.pipeline import MultiplePipelineFromSameConfigWithSameParent, NonExistingPipeline
from taipy.core.exceptions.task import NonExistingTask
from taipy.core.job.job import Job
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_repository import PipelineRepository
from taipy.core.task.task_manager import TaskManager


class PipelineManager:
    """
    The Pipeline Manager is responsible for managing all pipeline-related capabilities.
    """

    repository = PipelineRepository()

    @classmethod
    def subscribe(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Subscribes a function to be called when the status of a Job changes.
        If pipeline is not passed, the subscription is added to all pipelines.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        if pipeline is None:
            pipelines = cls.get_all()
            for pln in pipelines:
                cls.__add_subscriber(callback, pln)
            return

        cls.__add_subscriber(callback, pipeline)

    @classmethod
    def unsubscribe(cls, callback: Callable[[Pipeline, Job], None], pipeline: Optional[Pipeline] = None):
        """
        Unsubscribes a function that is called when the status of a Job changes.
        If pipeline is not passed, the subscription is removed to all pipelines.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        if pipeline is None:
            pipelines = cls.get_all()
            for pln in pipelines:
                cls.__remove_subscriber(callback, pln)
            return

        cls.__remove_subscriber(callback, pipeline)

    @classmethod
    def __add_subscriber(cls, callback, pipeline):
        pipeline.add_subscriber(callback)
        cls.set(pipeline)

    @classmethod
    def __remove_subscriber(cls, callback, pipeline):
        pipeline.remove_subscriber(callback)
        cls.set(pipeline)

    @classmethod
    def delete_all(cls):
        """
        Deletes all pipelines.
        """
        cls.repository.delete_all()

    @classmethod
    def delete(cls, pipeline_id: PipelineId):
        """Deletes the pipeline provided as parameter.

        Parameters:
            pipeline_id (str): identifier of the pipeline to delete.
        Raises:
            ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        cls.repository.delete(pipeline_id)

    @classmethod
    def get_or_create(cls, pipeline_config: PipelineConfig, scenario_id: Optional[ScenarioId] = None) -> Pipeline:
        """
        Returns a pipeline created from the pipeline configuration.

        Parameters:
            pipeline_config (PipelineConfig): The pipeline configuration object.
            scenario_id (Optional[ScenarioId]): id of the scenario creating the pipeline. Default value : `None`.
        Raises:
            MultiplePipelineFromSameConfigWithSameParent: if more than one pipeline already exists with the
                same config, and the same parent id (scenario_id, or pipeline_id depending on the scope of
                the data nodes).
        """
        pipeline_id = Pipeline.new_id(pipeline_config.name)
        tasks = [
            TaskManager.get_or_create(t_config, scenario_id, pipeline_id) for t_config in pipeline_config.tasks_configs
        ]
        scope = min(task.scope for task in tasks) if len(tasks) != 0 else Scope.GLOBAL
        parent_id = scenario_id if scope == Scope.SCENARIO else pipeline_id if scope == Scope.PIPELINE else None
        pipelines_from_config_name = cls._get_all_by_config_name(pipeline_config.name)
        pipelines_from_parent = [pipeline for pipeline in pipelines_from_config_name if pipeline.parent_id == parent_id]
        if len(pipelines_from_parent) == 1:
            return pipelines_from_parent[0]
        elif len(pipelines_from_parent) > 1:
            logging.error("Multiple pipelines from same config exist with the same parent_id.")
            raise MultiplePipelineFromSameConfigWithSameParent
        else:
            pipeline = Pipeline(pipeline_config.name, dict(**pipeline_config.properties), tasks, pipeline_id, parent_id)
            cls.set(pipeline)
            return pipeline

    @classmethod
    def set(cls, pipeline: Pipeline):
        """
        Saves or updates a pipeline.

        Parameters:
            pipeline (Pipeline): the pipeline to save or update.
        """
        cls.repository.save(pipeline)

    @classmethod
    def get(cls, pipeline: Union[Pipeline, PipelineId], default=None) -> Pipeline:
        """
        Gets a pipeline.

        Parameters:
            pipeline (Union[Pipeline, PipelineId]): pipeline identifier or the pipeline to get.
            default: default value to return if no pipeline is found. None is returned if no default value is provided.
        """
        try:
            pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
            return cls.repository.load(pipeline_id)
        except ModelNotFound:
            logging.error(f"Pipeline entity: {pipeline_id} does not exist.")
            return default

    @classmethod
    def get_all(cls) -> List[Pipeline]:
        """
        Returns all existing pipelines.

        Returns:
            List[Pipeline]: the list of all pipelines managed by this pipeline manager.
        """
        return cls.repository.load_all()

    @classmethod
    def submit(
        cls, pipeline: Union[PipelineId, Pipeline], callbacks: Optional[List[Callable]] = None, force: bool = False
    ):
        """
        Submits the pipeline corresponding to the pipeline or the identifier given as parameter for execution.

        All the tasks of pipeline will be submitted for execution.

        Parameters:
            pipeline (Union[PipelineId, Pipeline]): the pipeline or its id to submit.
            callbacks: Callbacks on job status changes.
            force: Boolean to enforce re execution of the tasks whatever the cache data nodes.

        Raises:
            NonExistingPipeline: if no pipeline corresponds to the pipeline identifier.
        """
        callbacks = callbacks or []
        pipeline_id = pipeline.id if isinstance(pipeline, Pipeline) else pipeline
        pipeline = cls.get(pipeline_id)
        if pipeline is None:
            raise NonExistingPipeline(pipeline_id)
        pipeline_subscription_callback = cls.__get_status_notifier_callbacks(pipeline) + callbacks
        TaskManager.scheduler().submit(pipeline, callbacks=pipeline_subscription_callback, force=force)

    @staticmethod
    def __get_status_notifier_callbacks(pipeline: Pipeline) -> List:
        return [partial(c, pipeline) for c in pipeline.subscribers]

    @classmethod
    def _get_all_by_config_name(cls, config_name: str) -> List[Pipeline]:
        """
        Returns all the existing pipelines for a configuration.

        Parameters:
            config_name (str): The pipeline configuration name to be looked for.
        Returns:
            List[Pipeline]: the list of all pipelines, managed by this pipeline manager,
                that use the indicated configuration name.
        """
        return cls.repository.search_all("config_name", config_name)

    @classmethod
    def hard_delete(cls, pipeline_id: PipelineId, scenario_id: Optional[ScenarioId] = None):
        """
        Deletes the pipeline given as parameter and the nested tasks, data nodes, and jobs.

        Deletes the pipeline given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested task if the task is not shared by another pipeline or if a scenario id is given as parameter, by another
        scenario.

        Parameters:
        pipeline_id (PipelineId) : identifier of the pipeline to hard delete.
        scenario_id (ScenarioId) : identifier of the optional parent scenario.

        Raises:
        ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        pipeline = cls.get(pipeline_id)
        for task in pipeline.tasks.values():
            if scenario_id and task.parent_id == scenario_id:
                TaskManager.hard_delete(task.id, scenario_id)
            elif task.parent_id == pipeline.id:
                TaskManager.hard_delete(task.id, None, pipeline_id)
        cls.delete(pipeline_id)
