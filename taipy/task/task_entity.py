import uuid
from importlib import import_module
from typing import List, NewType

from taipy.data.data_source import DataSourceEntity

TaskId = NewType("TaskId", str)


class TaskEntity:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(self, name: str, inputs: List[DataSourceEntity], function,
                 outputs: List[DataSourceEntity] = None, id: TaskId = None):
        if outputs is None:
            outputs = []
        self.input_data_sources = inputs
        self.output_data_sources = outputs
        self.name = name
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())]))
        fct = (function.__module__, function.__name__) if function else function
        self.module = import_module(fct[0])
        self.function = getattr(self.module, fct[1])
