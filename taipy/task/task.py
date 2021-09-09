import uuid
from importlib import import_module
from typing import List, NewType

from taipy.data.data_source import DataSourceEntity

TaskId = NewType("TaskId", str)


class Task:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        task_id: TaskId,
        name: str,
        input_data_sources: List[DataSourceEntity],
        function,
        output_data_sources: List[DataSourceEntity] = None,
    ):
        if output_data_sources is None:
            output_data_sources = []
        self.input_data_sources = input_data_sources
        self.output_data_sources = output_data_sources
        self.name = name
        self.id = task_id
        self.function = function

    @classmethod
    def create_task(
        cls,
        name: str,
        input_data_sources: List[DataSourceEntity],
        function,
        output_data_sources: List[DataSourceEntity] = None,
    ):
        task_id = TaskId(
            cls.__ID_SEPARATOR.join([cls.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        return Task(task_id, name, input_data_sources, function, output_data_sources)
