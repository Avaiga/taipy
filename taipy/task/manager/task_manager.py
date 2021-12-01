import itertools
import logging
from typing import Dict, List, Optional

from taipy.common.alias import PipelineId, ScenarioId, TaskId
from taipy.config import TaskConfig
from taipy.data import Scope
from taipy.data.manager import DataManager
from taipy.exceptions import ModelNotFound, NonExistingTask
from taipy.exceptions.task import MultipleTaskFromSameConfigWithSameParent
from taipy.task import TaskScheduler
from taipy.task.repository import TaskRepository
from taipy.task.task import Task


class TaskManager:
    """Allow to save and retrieve Tasks.

    Attributes:
        tasks: Dict of all tasks with ID.
        task_scheduler: Allow to run task.
        data_manager: For interaction with DataSource.
        repository: Repository for saving tasks.
    """

    tasks: Dict[(TaskId, Task)] = {}
    task_scheduler = TaskScheduler()
    data_manager = DataManager()
    repository = TaskRepository()

    def delete_all(self):
        """Deletes all data sources."""
        self.repository.delete_all()

    def get_all(self):
        """Returns the list of all existing tasks.

        Returns:
            List of tasks.
        """
        return self.repository.load_all()

    def set(self, task: Task):
        """Saves or Updates the task given as parameter.

        Args:
            task (Task) : task to save.
        """
        logging.info(f"Task: {task.id} created or updated.")
        self.__save_data_sources(task.input.values())
        self.__save_data_sources(task.output.values())
        self.repository.save(task)

    def get_or_create(
        self,
        task_config: TaskConfig,
        scenario_id: Optional[ScenarioId] = None,
        pipeline_id: Optional[PipelineId] = None,
    ) -> Task:
        """Returns the task created from the task_config, by (pipeline_id and scenario_id) if it already
        exists, or creates and returns a new task.

        Args:
            task_config (TaskConfig) : task configuration object.
            scenario_id (Optional[ScenarioId]) : id of the scenario creating the data source. Default value : None.
            pipeline_id (Optional[PipelineId]) : id of the pipeline creating the data source. Default value : None.

        Returns:
            Task created

        Raises:
            MultipleTaskFromSameConfigWithSameParent error if more than 1 task already exist with the same
            config, and the same parent id (scenario_id, or pipeline_id depending on the scope of the data source).
        """
        data_sources = {
            ds_config: self.data_manager.get_or_create(ds_config, scenario_id, pipeline_id)
            for ds_config in set(itertools.chain(task_config.input, task_config.output))
        }
        scope = min(ds.scope for ds in data_sources.values()) if len(data_sources) != 0 else Scope.GLOBAL
        parent_id = pipeline_id if scope == Scope.PIPELINE else scenario_id if scope == Scope.SCENARIO else None
        tasks_from_config_name = self._get_all_by_config_name(task_config.name)
        tasks_from_parent = [task for task in tasks_from_config_name if task.parent_id == parent_id]
        if len(tasks_from_parent) == 1:
            return tasks_from_parent[0]
        elif len(tasks_from_parent) > 1:
            logging.error("Multiple tasks from same config exist with the same parent_id.")
            raise MultipleTaskFromSameConfigWithSameParent
        else:
            inputs = [data_sources[input_config] for input_config in task_config.input]
            outputs = [data_sources[output_config] for output_config in task_config.output]
            task = Task(task_config.name, inputs, task_config.function, outputs, parent_id=parent_id)
            self.set(task)
            return task

    def get(self, task_id: TaskId) -> Task:
        """Gets the task corresponding to the identifier given as parameter.

        Args:
            task_id (TaskId) : task to get.

        Returns:
            Task corresponding to the id.

        Raises:
            ModelNotFound error if no task corresponds to task_id.
        """
        try:
            if opt_task := self.repository.load(task_id):
                return opt_task
            else:
                logging.error(f"Task: {task_id} does not exist.")
                raise NonExistingTask(task_id)
        except ModelNotFound:
            logging.error(f"Task: {task_id} does not exist.")
            raise NonExistingTask(task_id)

    def __save_data_sources(self, data_sources):
        for i in data_sources:
            self.data_manager.set(i)

    def _get_all_by_config_name(self, config_name: str) -> List[Task]:
        """
        Returns the list of all existing tasks with the corresponding config name.

        Args:
             config_name (str) : task config's name.

        Returns:
            List of tasks of this config name
        """
        return self.repository.search_all("config_name", config_name)
