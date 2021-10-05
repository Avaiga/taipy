import logging
import uuid
from collections.abc import Iterable
from typing import Dict, NewType, Optional

from taipy.data.data_source_entity import DataSourceEntity

TaskId = NewType("TaskId", str)


class TaskEntity:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        input: Iterable[DataSourceEntity],
        function,
        output: Optional[Iterable[DataSourceEntity]] = None,
        id: TaskId = None,
    ):
        self.__input = {ds.name: ds for ds in input}
        self.__output = {ds.name: ds for ds in output or []}
        self.name = self.__protect_name(name)
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())]))
        self.function = function

    @property
    def output(self) -> Dict[str, DataSourceEntity]:
        return self.__output

    @property
    def input(self) -> Dict[str, DataSourceEntity]:
        return self.__input

    @staticmethod
    def __protect_name(name):
        return name.strip().lower().replace(" ", "_")

    def __getattr__(self, attribute_name):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.input:
            return self.input[protected_attribute_name]
        if protected_attribute_name in self.output:
            return self.output[protected_attribute_name]
        logging.error(f"{attribute_name} is not a data source of task {self.id}")
        raise AttributeError
