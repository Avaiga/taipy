from copy import copy
from typing import List, Union

from taipy.data import DataSource


class Task:
    def __init__(
        self,
        name: str,
        input: Union[DataSource, List[DataSource]],
        function,
        output: Union[DataSource, List[DataSource]],
    ):
        if isinstance(input, DataSource):
            self.__input = [input]
        else:
            self.__input = copy(input)
        if isinstance(output, DataSource):
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
