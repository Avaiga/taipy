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
        self.inputs = inputs
        self.outputs = outputs
        self.name = name
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())]))
        self.function = function
