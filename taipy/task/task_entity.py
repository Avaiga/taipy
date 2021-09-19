import uuid
from typing import List, NewType, Optional

from taipy.data.data_source_entity import DataSourceEntity

TaskId = NewType("TaskId", str)


class TaskEntity:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        input: List[DataSourceEntity],
        function,
        output: Optional[List[DataSourceEntity]],
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
