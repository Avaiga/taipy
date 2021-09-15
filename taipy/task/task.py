from typing import List, Union

from taipy.data.data_source import DataSource


class Task:

    def __init__(self, name: str,
                 inputs: Union[DataSource, List[DataSource]],
                 function,
                 outputs:  Union[DataSource, List[DataSource]]):
        if isinstance(inputs, DataSource):
            self.inputs = List[inputs]
        else:
            self.inputs = inputs
        if isinstance(outputs, DataSource):
            self.outputs = List[outputs]
        else:
            self.outputs = outputs
        self.name = name
        self.function = function
