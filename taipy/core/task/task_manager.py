import itertools
import logging
from typing import Dict, List, Optional, Union

from taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from taipy.core.config.task_config import TaskConfig
from taipy.core.data.data_manager import DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions import ModelNotFound
from taipy.core.exceptions.task import MultipleTaskFromSameConfigWithSameParent
from taipy.core.job.job_manager import JobManager
from taipy.core.scheduler.abstract_scheduler import AbstractScheduler
from taipy.core.scheduler.scheduler_factory import SchedulerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_repository import TaskRepository


class TaskManager:
    """
    The Task Manager saves and retrieves Tasks.

    Attributes:
        tasks (Dict[(TaskId, Task)]): A dictionary that associates every task with its identifier.
        scheduler (AbstractScheduler): The scheduler for submitting tasks.
        data_manager (DataManager): The Data Manager that interacts with data nodes.
        repository (TaskRepository): The repository where tasks are saved.
    """

    repository: TaskRepository = TaskRepository()
    _scheduler = None

    @classmethod
    def scheduler(cls) -> AbstractScheduler:
        if not cls._scheduler:
            cls._scheduler = SchedulerFactory.build_scheduler()
        return cls._scheduler

    @classmethod
    def delete_all(cls):
        """
        Deletes all the persisted tasks.
        """
        cls.repository.delete_all()

    @classmethod
    def delete(cls, task_id: TaskId):
        """Deletes the cycle provided as parameter.

        Parameters:
            task_id (str): identifier of the task to delete.
        Raises:
            ModelNotFound error if no task corresponds to task_id.
        """
        cls.repository.delete(task_id)

    @classmethod
    def get_all(cls) -> List[Task]:
        """
        Returns the list of all existing tasks.

        Returns:
            List: The list of tasks handled by this Task Manager.
        """
        return cls.repository.load_all()

    @classmethod
    def set(cls, task: Task):
        """
        Saves or updates a task.

        Args:
            task (Task): The task to save.
        """
        logging.info(f"Task: {task.id} created or updated.")
        cls.__save_data_nodes(task.input.values())
        cls.__save_data_nodes(task.output.values())
        cls.repository.save(task)

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
            for dn_config in set(itertools.chain(task_config.input, task_config.output))
        }
        scope = min(dn.scope for dn in data_nodes.values()) if len(data_nodes) != 0 else Scope.GLOBAL
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        tasks_from_config_name = cls._get_all_by_config_name(task_config.name)
        tasks_from_parent = [task for task in tasks_from_config_name if task.parent_id == parent_id]
        if len(tasks_from_parent) == 1:
            return tasks_from_parent[0]
        elif len(tasks_from_parent) > 1:
            logging.error("Multiple tasks from same config exist with the same parent_id.")
            raise MultipleTaskFromSameConfigWithSameParent
        else:
            inputs = [data_nodes[input_config] for input_config in task_config.input]
            outputs = [data_nodes[output_config] for output_config in task_config.output]
            task = Task(task_config.name, task_config.function, inputs, outputs, parent_id=parent_id)
            cls.set(task)
            return task

    @classmethod
    def get(cls, task: Union[Task, TaskId], default=None) -> Task:
        """
        Gets a task given the Task or the identifier.

        Args:
            task (Union[Task, TaskId]): The task identifier of the task to get.
            default: The default value to return if no task is found. None is returned if no default value is provided.
        """
        try:
            task_id = task.id if isinstance(task, Task) else task
            return cls.repository.load(task_id)
        except ModelNotFound:
            logging.error(f"Task: {task_id} does not exist.")
            return default

    @classmethod
    def __save_data_nodes(cls, data_nodes):
        for i in data_nodes:
            DataManager.set(i)

    @classmethod
    def _get_all_by_config_name(cls, config_name: str) -> List[Task]:
        """
        Returns the list of all existing tasks with the corresponding config name.

        Args:
             config_name (str) : task config's name.

        Returns:
            List of tasks of this config name
        """
        return cls.repository.search_all("config_name", config_name)

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
        pipeline_id (PipelineId) : identifier of the optional parent pipeline.
        scenario_id (ScenarioId) : identifier of the optional parent scenario.

        Raises:
        ModelNotFound error if no pipeline corresponds to pipeline_id.
        """
        task = cls.get(task_id)

        jobs = JobManager.get_all()
        for job in jobs:
            if job.task.id == task.id:
                JobManager.delete(job)

        if scenario_id:
            cls._remove_if_parent_id_eq(task.input.values(), scenario_id)
            cls._remove_if_parent_id_eq(task.output.values(), scenario_id)
        if pipeline_id:
            cls._remove_if_parent_id_eq(task.input.values(), pipeline_id)
            cls._remove_if_parent_id_eq(task.output.values(), pipeline_id)

        cls.delete(task_id)

    @classmethod
    def _remove_if_parent_id_eq(cls, data_nodes, id_):
        for data_node in data_nodes:
            if data_node.parent_id == id_:
                DataManager.delete(data_node.id)
