import logging
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
        self.input = {ds.name: ds for ds in input}
        self.output = {ds.name: ds for ds in output}
        self.name = name.strip().lower().replace(' ', '_')
        self.id = id or TaskId(
            self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.function = function

    def __getattr__(self, attribute_name):
        if attribute_name in self.input:
            return self.input[attribute_name]
        if attribute_name in self.output:
            return self.output[attribute_name]
        logging.error(f"{attribute_name} is not a data source of task {self.id}")
        raise AttributeError
