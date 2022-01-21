__all__ = ["JobDispatcher"]

import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any, List, Optional

from taipy.common.alias import JobId
from taipy.data import DataSource
from taipy.data.manager import DataManager
from taipy.exceptions.job import DataSourceWritingError
from taipy.job import JobManager
from taipy.job.job import Job
from taipy.scheduler.executor.synchronous import Synchronous
from taipy.task.task import Task


class JobDispatcher:
    """Wrapper around executor that will run jobs.

    Job can be executed on different contexts (locally, etc.). This wrapper
    instantiate the executor based on its args then deal with its low level interface to provide
    a homogeneous way to execute jobs.
    """

    def __init__(self, max_number_of_parallel_execution: Optional[int]):
        self.job_manager = JobManager()
        self._executor, self._nb_worker_available = self.__create(max_number_of_parallel_execution or 1)

    def can_execute(self) -> bool:
        """Returns True if a worker is available for a new run."""
        return self._nb_worker_available > 0

    def dispatch(self, job: Job):
        """Dispatches a Job on an available worker for execution.

        Args:
            job: Element to execute.
        """
        job.running()
        self.job_manager.set(job)
        self._nb_worker_available -= 1
        future = self._executor.submit(self._call_function, job.id, job.task)
        future.add_done_callback(self.__release_worker)
        future.add_done_callback(partial(self.__update_status, job))

    def __release_worker(self, _):
        self._nb_worker_available += 1

    def __update_status(self, job, ft):
        job.update_status(ft)
        self.job_manager.set(job)

    @classmethod
    def _call_function(cls, job_id: JobId, task: Task):
        try:
            inputs: List[DataSource] = list(task.input.values())
            outputs: List[DataSource] = list(task.output.values())
            fct = task.function
            results = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, results, job_id)
        except Exception as e:
            return [e]

    @classmethod
    def __read_inputs(cls, inputs: List[DataSource]) -> List[Any]:
        return [DataManager().get(ds.id).read() for ds in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataSource], results, job_id: JobId):
        try:
            _results = cls.__extract_results(outputs, results)
            exceptions = []
            for res, ds in zip(_results, outputs):
                try:
                    data_source = DataManager().get(ds.id)
                    data_source.write(res, job_id=job_id)
                    DataManager().set(data_source)
                except Exception as e:
                    exceptions.append(DataSourceWritingError(f"Error writing in datasource id {ds.id}: {e}"))
                    logging.error(f"Error writing output {e}")
            return exceptions
        except Exception as e:
            return [e]

    @staticmethod
    def __extract_results(outputs: List[DataSource], results: Any) -> List[Any]:
        _results: List[Any] = [results] if len(outputs) == 1 else results

        if len(_results) != len(outputs):
            logging.error("Error: wrong number of result or task output")
            raise DataSourceWritingError("Error: wrong number of result or task output")

        return _results

    @staticmethod
    def __create(max_number_of_parallel_execution):
        if max_number_of_parallel_execution > 1:
            executor = ProcessPoolExecutor(max_number_of_parallel_execution)
            return executor, (executor._max_workers)
        else:
            return Synchronous(), 1
