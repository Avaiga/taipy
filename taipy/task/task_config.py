from copy import copy
from typing import List, Union

from taipy.data import DataSourceConfig


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
        self.name = name.strip().lower().replace(' ', '_')
        self.function = function

    @property
    def output(self) -> List:
        return list(self.__output)

    @property
    def input(self) -> List:
        return list(self.__input)
