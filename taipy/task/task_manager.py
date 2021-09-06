import logging
from typing import Dict

from taipy.exceptions import NonExistingTask
from taipy.task.task import Task
from taipy.task.types import TaskId


class TaskManager:

    # This represents the task database.
    tasks: Dict[(TaskId, Task)] = {}

    def delete_all(self):
        self.tasks: Dict[(TaskId, Task)] = {}

    def save_task(self, task: Task):
        logging.info(f"Task : {task.id} created or updated.")
        self.tasks[task.id] = task

    def get_task(self, task_id: TaskId) -> Task:
        try:
            return self.tasks[task_id]
        except KeyError:
            logging.error(f"Task : {task_id} does not exist.")
            raise NonExistingTask(task_id)
