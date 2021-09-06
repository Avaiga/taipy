import uuid
from importlib import import_module

from taipy.data.data_source import DataSource
from taipy.task.types import TaskId


class Task:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(self, task_id: TaskId, name: str, input_data_sources: list[DataSource], function, output_data_sources: list[DataSource] = None):
        if output_data_sources is None:
            output_data_sources = []
        self.input_data_sources = input_data_sources
        self.output_data_sources = output_data_sources
        self.name = name
        self.id = task_id
        fct = (function.__module__, function.__name__) if function else function
        self.module = import_module(fct[0])
        self.function = getattr(self.module, fct[1])

    @classmethod
    def create_task(cls, name: str, input_data_sources: list[DataSource], function, output_data_sources: list[DataSource] = None):
        taskId = TaskId(''.join([cls.__ID_PREFIX, cls.__ID_SEPARATOR, name, cls.__ID_SEPARATOR, str(uuid.uuid4())]))
        return Task(taskId, name, input_data_sources, function, output_data_sources)
