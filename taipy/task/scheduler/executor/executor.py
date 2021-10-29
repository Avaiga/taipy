__all__ = ["Executor"]

import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any, List, Optional

from taipy.data import DataSource
from taipy.data.manager import DataManager
from taipy.exceptions.job import DataSourceWritingError

from ..job import Job
from .synchronous import Synchronous


class Executor:
    def __init__(self, parallel_execution: bool, max_number_of_parallel_execution: Optional[int]):
        self.__executor, self.__nb_worker_available = self.__create(
            max_number_of_parallel_execution, parallel_execution
        )

    def can_execute(self) -> bool:
        return self.__nb_worker_available > 0

    def execute(self, job: Job):
        job.running()
        inputs = job.task.input.values()
        outputs = job.task.output.values()
        self.__nb_worker_available -= 1
        future = self.__executor.submit(partial(self._call_function, inputs, job.task.function, outputs))
        future.add_done_callback(self.__release_worker)
        future.add_done_callback(job.update_status)

    def __release_worker(self, _):
        self.__nb_worker_available += 1

    @classmethod
    def _call_function(cls, inputs: List[DataSource], fct, outputs: List[DataSource]):
        try:
            r = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, r)
        except Exception as e:
            return [e]

    @classmethod
    def __read_inputs(cls, inputs: List[DataSource]) -> List[Any]:
        return [DataManager().get(ds.id).get() for ds in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataSource], results):
        try:
            _results = cls.__extract_results(outputs, results)
            exceptions = []
            for res, ds in zip(_results, outputs):
                try:
                    DataManager().get(ds.id).write(res)
                except Exception as e:
                    exceptions.append(DataSourceWritingError(f"Error on writing in datasource id {ds.id}: {e}"))
                    logging.error(f"Error on writing output {e}")
            return exceptions
        except Exception as e:
            return [e]

    @staticmethod
    def __extract_results(outputs: List[DataSource], results: Any) -> List[Any]:
        _results: List[Any] = [results] if len(outputs) == 1 else results

        if len(_results) != len(outputs):
            logging.error("Error, wrong number of result or task output")
            raise DataSourceWritingError("Error, wrong number of result or task output")

        return _results

    @staticmethod
    def __create(max_number_of_parallel_execution, parallel_execution):
        if parallel_execution:
            executor = ProcessPoolExecutor(max_number_of_parallel_execution)
            return executor, (executor._max_workers)
        else:
            return Synchronous(), 1
