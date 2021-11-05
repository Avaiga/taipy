import logging
import uuid
from collections.abc import Iterable
from typing import Dict, Optional

from taipy.common import protect_name
from taipy.common.alias import TaskId
from taipy.data.data_source import DataSource


class Task:
    __ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        input: Iterable[DataSource],
        function,
        output: Optional[Iterable[DataSource]] = None,
        id: TaskId = None,
    ):
        self.__input = {ds.config_name: ds for ds in input}
        self.__output = {ds.config_name: ds for ds in output or []}
        self.config_name = self.__protect_name(config_name)
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self.__ID_PREFIX, self.config_name, str(uuid.uuid4())]))
        self.function = function

    @property
    def output(self) -> Dict[str, DataSource]:
        return self.__output

    @property
    def input(self) -> Dict[str, DataSource]:
        return self.__input

    @staticmethod
    def __protect_name(config_name):
        return protect_name(config_name)
    

    def __getattr__(self, attribute_name):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.input:
            return self.input[protected_attribute_name]
        if protected_attribute_name in self.output:
            return self.output[protected_attribute_name]
        logging.error(f"{attribute_name} is not a data source of task {self.id}")
        raise AttributeError
