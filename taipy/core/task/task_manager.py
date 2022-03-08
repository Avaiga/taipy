import itertools
from typing import Dict, List, Optional, Union

from taipy.core.common._manager import _Manager
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from taipy.core.config.task_config import TaskConfig
from taipy.core.data.data_manager import DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.exceptions.task import MultipleTaskFromSameConfigWithSameParent
from taipy.core.job.job_manager import JobManager
from taipy.core.scheduler.abstract_scheduler import AbstractScheduler
from taipy.core.scheduler.scheduler_factory import SchedulerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_repository import TaskRepository


class TaskManager(_Manager[Task]):
    """
    The Task Manager saves and retrieves Tasks.

    Attributes:
        tasks (Dict[(TaskId, Task)]): A dictionary that associates every task with its identifier.
        scheduler (AbstractScheduler): The scheduler for submitting tasks.
        data_manager (DataManager): The Data Manager that interacts with data nodes.
        repository (TaskRepository): The repository where tasks are saved.
    """

    _repository: TaskRepository = TaskRepository()
    ENTITY_NAME = Task.__name__
    _scheduler = None

    @classmethod
    def scheduler(cls) -> AbstractScheduler:
        if not cls._scheduler:
            cls._scheduler = SchedulerFactory.build_scheduler()
        return cls._scheduler

    @classmethod
    def _set(cls, task: Task):
        """
        Saves or updates a task.

        Args:
            task (Task): The task to save.
        """
        cls.__save_data_nodes(task.input.values())
        cls.__save_data_nodes(task.output.values())
        super()._set(task)

    @classmethod
    def get_or_create(
        cls,
        task_config: TaskConfig,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> Task:
        """Returns a task created from the provided task configuration.

        If no task exists for that task configuration, in the provided `scenario_id` and `pipeline_id`, then
        a new task is created and returned.

        Args:
            task_config (TaskConfig): The task configuration object.
            scenario_id (ScenarioId): The identifier of the scenario creating the task.
            pipeline_id (PipelineId): The identifier of the pipeline creating the task.

        Returns:
            A task, potentially new, that is created for that task configuration.

        Raises:
            MultipleTaskFromSameConfigWithSameParent: if more than one task already exists with the same
                configuration, and the same parent id (scenario or pipeline identifier, depending on the
                scope of the data node). TODO: This comment makes no sense - Data Node scope
        """
        data_nodes = {
            dn_config: DataManager.get_or_create(dn_config, scenario_id, pipeline_id)
            for dn_config in set(itertools.chain(task_config.input_configs, task_config.output_configs))
        }
        scope = min(dn.scope for dn in data_nodes.values()) if len(data_nodes) != 0 else Scope.GLOBAL
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        tasks_from_config_id = cls._get_all_by_config_id(task_config.id)
        tasks_from_parent = [task for task in tasks_from_config_id if task.parent_id == parent_id]
        if len(tasks_from_parent) == 1:
            return tasks_from_parent[0]
        elif len(tasks_from_parent) > 1:
            raise MultipleTaskFromSameConfigWithSameParent
        else:
            inputs = [data_nodes[input_config] for input_config in task_config.input_configs]
            outputs = [data_nodes[output_config] for output_config in task_config.output_configs]
            task = Task(task_config.id, task_config.function, inputs, outputs, parent_id=parent_id)
            cls._set(task)
            return task

    @classmethod
    def __save_data_nodes(cls, data_nodes):
        for i in data_nodes:
            DataManager._set(i)

    @classmethod
    def hard_delete(
        cls, task_id: TaskId, scenario_id: Optional[ScenarioId] = None, pipeline_id: Optional[PipelineId] = None
    ):
        """
        Deletes the task given as parameter and the nested data nodes, and jobs.

        Deletes the task given as parameter and propagate the hard deletion. The hard delete is propagated to a
        nested data nodes if the data nodes is not shared by another pipeline or if a scenario id is given as
        parameter, by another scenario.

        Parameters:
            task_id (TaskId): identifier of the task to hard delete.
            scenario_id (ScenarioId) : identifier of the optional parent scenario.
            pipeline_id (PipelineId) : identifier of the optional parent pipeline.

        Raises:
            ModelNotFound: No task corresponds to task_id.
        """
        task = cls._get(task_id)

        jobs = JobManager._get_all()
        for job in jobs:
            if job.task.id == task.id:
                JobManager._delete(job)

        if scenario_id:
            cls._remove_if_parent_id_eq(task.input.values(), scenario_id)
            cls._remove_if_parent_id_eq(task.output.values(), scenario_id)
        if pipeline_id:
            cls._remove_if_parent_id_eq(task.input.values(), pipeline_id)
            cls._remove_if_parent_id_eq(task.output.values(), pipeline_id)

        cls._delete(task_id)

    @classmethod
    def _remove_if_parent_id_eq(cls, data_nodes, id_):
        for data_node in data_nodes:
            if data_node.parent_id == id_:
                DataManager._delete(data_node.id)

    @classmethod
    def _get_all_by_config_id(cls, config_id: str) -> List[Task]:
        return cls._repository.search_all("config_id", config_id)
