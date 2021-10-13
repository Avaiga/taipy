__all__ = ["Executor"]

from concurrent.futures import ProcessPoolExecutor
from typing import Optional

from ..job import Job
from .synchronous import Synchronous


class Executor:
    def __init__(self, parallel_execution: bool, max_number_of_parallel_execution: Optional[int]):
        self.__executor, self.__nb_worker_available = self.__create_executor(
            parallel_execution, max_number_of_parallel_execution
        )

    def can_execute(self) -> bool:
        return self.__nb_worker_available > 0

    def execute(self, job: Job):
        self.__nb_worker_available -= 1
        future = self.__executor.submit(job.to_execute())
        future.add_done_callback(self._job_finished)
        future.add_done_callback(lambda ft: job.write(ft.result()))

    def _job_finished(self, _):
        self.__nb_worker_available += 1

    @staticmethod
    def __create_executor(parallel_execution, max_number_of_parallel_execution):
        if parallel_execution:
            executor = ProcessPoolExecutor(max_number_of_parallel_execution)
            nb_worker_available = executor._max_workers
        else:
            executor = Synchronous()
            nb_worker_available = 1
        return executor, nb_worker_available
