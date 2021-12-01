__all__ = ["JobDispatcher"]

import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Any, List, Optional

from taipy.common.alias import JobId
from taipy.data import DataSource
from taipy.data.manager import DataManager
from taipy.exceptions.job import DataSourceWritingError
from taipy.task import Task
from taipy.task.scheduler.executor.remote_pool_executor import RemotePoolExecutor
from taipy.task.scheduler.executor.synchronous import Synchronous
from taipy.task.scheduler.job import Job


class JobDispatcher:
    """Wrapper around executor that will run jobs.

    Job can be executed on different contexts (locally, remotly, etc.). This wrapper
    instantiate the executor based on its args then deal with its low level interface to provide
    a homogeneous way to execute jobs.
    """

    def __init__(
        self,
        parallel_execution: bool,
        remote_execution: bool,
        max_number_of_parallel_execution: Optional[int],
        hostname: Optional[str] = None,
    ):
        self.__executor, self.__nb_worker_available = self.__create(
            parallel_execution, remote_execution, max_number_of_parallel_execution, hostname
        )

    def can_execute(self) -> bool:
        """Allow to know if another job can be executed.

        Returns:
            True if another job can be executed.
        """
        return self.__nb_worker_available > 0

    def execute(self, job: Job):
        """Start the execution of a Job.

        Args:
            job: Element to execute.
        """
        job.running()
        self.__nb_worker_available -= 1
        future = self.__executor.submit(self._call_function, job.id, job.task)
        future.add_done_callback(self.__release_worker)
        future.add_done_callback(job.update_status)

    def __release_worker(self, _):
        self.__nb_worker_available += 1

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
                    data_source.write(res, job_id)
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
    def __create(parallel_execution, remote_execution, max_number_of_parallel_execution, hostname):
        if parallel_execution:
            executor = ProcessPoolExecutor(max_number_of_parallel_execution)
            return executor, (executor._max_workers)
        elif remote_execution:
            executor = RemotePoolExecutor(max_number_of_parallel_execution, hostname)
            return executor, (executor._max_workers)
        else:
            return Synchronous(), 1
