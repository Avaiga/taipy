from taipy.task.task import *
from taipy.task.types import TaskId


class TaskManager:

    # This represents the task database.
    tasks: dict[(TaskId, Task)] = {}

    def save_task(self, task: Task):
        self.tasks[task.id] = task

    def get_task(self, task_id: TaskId) -> Task:
        return self.tasks[task_id]
