from copy import copy
from typing import List, Union

from taipy.common import protect_name
from taipy.config import DataSourceConfig
from taipy.config.interface import ConfigRepository


class TaskConfig:
    def __init__(
        self,
        name: str,
        input: Union[DataSourceConfig, List[DataSourceConfig]],
        function,
        output: Union[DataSourceConfig, List[DataSourceConfig]],
    ):
        if isinstance(input, DataSourceConfig):
            self.__input = [input]
        else:
            self.__input = copy(input)
        if isinstance(output, DataSourceConfig):
            self.__output = [output]
        else:
            self.__output = copy(output)
        self.name = protect_name(name)
        self.function = function

    @property
    def output(self) -> List:
        return list(self.__output)

    @property
    def input(self) -> List:
        return list(self.__input)


class TaskConfigs(ConfigRepository):
    def create(  # type: ignore
        self,
        name: str,
        input: Union[DataSourceConfig, List[DataSourceConfig]],
        function,
        output: Union[DataSourceConfig, List[DataSourceConfig]],
    ):
        task_config = TaskConfig(name, input, function, output)
        self._data[name] = task_config
        return task_config
