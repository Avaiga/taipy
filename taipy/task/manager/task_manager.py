import itertools
import logging
from typing import Dict, Optional

from taipy.data import DataSource
from taipy.data.data_source_config import DataSourceConfig
from taipy.data.manager import DataManager
from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.task import NonExistingTask
from taipy.task.task import Task, TaskId
from taipy.task.task_config import TaskConfig


class TaskManager:
    # This represents the task database.
    task_entities: Dict[(TaskId, Task)] = {}
    __TASKS: Dict[(str, TaskConfig)] = {}
    data_manager = DataManager()

    def delete_all(self):
        self.task_entities: Dict[(TaskId, Task)] = {}
        self.__TASKS: Dict[(str, TaskConfig)] = {}

    def register_task(self, task: TaskConfig):
        [self.data_manager.register_data_source_config(data_source) for data_source in task.input]
        [self.data_manager.register_data_source_config(data_source) for data_source in task.output]
        self.__TASKS[task.name] = task

    def get_task(self, name: str) -> TaskConfig:
        try:
            return self.__TASKS[name]
        except KeyError:
            logging.error(f"Task : {name} does not exist.")
            raise NonExistingTask(name)

    def get_tasks(self):
        return self.__TASKS

    def save_task_entity(self, task: Task):
        logging.info(f"Task : {task.id} created or updated.")
        self.task_entities[task.id] = task

    def create_task_entity(
        self, task: TaskConfig, data_sources: Optional[Dict[DataSourceConfig, DataSource]] = None
    ) -> Task:
        if data_sources is None:
            data_sources = {
                ds: self.data_manager.get_or_create(ds) for ds in set(itertools.chain(task.input, task.output))
            }
        input_entities = [data_sources[input] for input in task.input]
        output_entities = [data_sources[output] for output in task.output]
        task_entity = Task(task.name, input_entities, task.function, output_entities)
        self.save_task_entity(task_entity)
        return task_entity

    def get_task_entity(self, task_id: TaskId) -> Task:
        try:
            return self.task_entities[task_id]
        except KeyError:
            logging.error(f"Task entity : {task_id} does not exist.")
            raise NonExistingTaskEntity(task_id)
