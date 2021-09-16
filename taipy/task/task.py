from typing import List, Union

from taipy.data.data_source import DataSource


class Task:
    def __init__(
        self,
        name: str,
        input: Union[DataSource, List[DataSource]],
        function,
        output: Union[DataSource, List[DataSource]],
    ):
        if isinstance(input, DataSource):
            self.input = [input]
        else:
            self.input = input
        if isinstance(output, DataSource):
            self.output = [output]
        else:
            self.output = output
        self.name = name
        self.function = function
