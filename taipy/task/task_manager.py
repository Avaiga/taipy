import logging
from typing import Dict

from taipy.data.data_manager import DataManager
from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.task import NonExistingTask
from taipy.task import Task
from taipy.task.task_entity import TaskEntity, TaskId


class TaskManager:
    # This represents the task database.
    task_entities: Dict[(TaskId, TaskEntity)] = {}
    __TASKS: Dict[(str, Task)] = {}
    data_manager = DataManager()

    def delete_all(self):
        self.task_entities: Dict[(TaskId, TaskEntity)] = {}

    def register_task(self, task: Task):
        self.__TASKS[task.name] = task

    def get_task(self, name: str) -> Task:
        try:
            return self.__TASKS[name]
        except KeyError:
            logging.error(f"Task : {name} does not exist.")
            raise NonExistingTask(name)

    def get_tasks(self):
        return self.__TASKS

    def save_task_entity(self, task: TaskEntity):
        logging.info(f"Task : {task.id} created or updated.")
        self.task_entities[task.id] = task
        for datasource in task.input_data_sources:
            # self.data_manager.save_data_source(task)
            ...
        for datasource in task.output_data_sources:
            # self.data_manager.save_data_source(task)
            ...

    def create_task_entity(self, task: Task) -> TaskEntity:
        entity = TaskEntity(task.name, task.input_data_sources, task.function, task.output_data_sources)
        self.save_task_entity(entity)
        return entity

    def get_task_entity(self, task_id: TaskId) -> TaskEntity:
        try:
            return self.task_entities[task_id]
        except KeyError:
            logging.error(f"Task entity : {task_id} does not exist.")
            raise NonExistingTaskEntity(task_id)
