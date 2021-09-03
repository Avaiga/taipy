import uuid
from importlib import import_module

from taipy.data.data_source import DataSource
from taipy.task.types import TaskId


class Task:
    ID_PREFIX = "TASK"
    ID_SEPARATOR = "_"
    input_data_sources = []
    output_data_sources = []
    function = None

    def __init__(self, name: str, input_data_sources: list[DataSource], function, output_data_sources: list[DataSource] = None):
        if output_data_sources is None:
            output_data_sources = []
        self.input_data_sources = input_data_sources
        self.output_data_sources = output_data_sources
        self.name = name
        self.id = TaskId(''.join([self.ID_PREFIX, self.ID_SEPARATOR, self.name, self.ID_SEPARATOR, str(uuid.uuid1())]))
        fct = (function.__module__, function.__name__) if function else function
        self.module = import_module(fct[0])
        self.function = getattr(self.module, fct[1])
