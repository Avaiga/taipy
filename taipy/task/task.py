from importlib import import_module
from typing import List

from taipy.data.data_source import DataSource


class Task:

    def __init__(self, name: str, inputs: List[DataSource], function, outputs: List[DataSource] = None):
        if outputs is None:
            outputs = []
        self.input_data_sources = inputs
        self.output_data_sources = outputs
        self.name = name
        self.function = function
