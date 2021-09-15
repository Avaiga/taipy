import uuid
from importlib import import_module
from typing import List, NewType

from taipy.data.data_source import DataSourceEntity

TaskId = NewType("TaskId", str)


class TaskEntity:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        input: List[DataSourceEntity],
        function,
        output: List[DataSourceEntity] = None,
        id: TaskId = None,
    ):
        if output is None:
            output = []
        self.input = input
        self.output = output
        self.name = name
        self.id = id or TaskId(
            self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.function = function
