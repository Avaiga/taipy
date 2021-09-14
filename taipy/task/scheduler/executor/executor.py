import functools
from concurrent.futures import Future
from typing import NoReturn, Iterable

from taipy.data.data_source import DataSource
from .future import FutureExecutor


class Executor:
    def __init__(self):
        self._executor = FutureExecutor()

    def submit(self, task):
        future = self._executor.submit(task.function, *task.input_data_sources)
        future.add_done_callback(
            functools.partial(self.set_output_data_sources, task.output_data_sources)
        )

    @staticmethod
    def set_output_data_sources(output_data_sources: Iterable[DataSource], future: Future) -> NoReturn:
        for ds in output_data_sources:
            ds.write(future.result())
