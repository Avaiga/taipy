__all__ = ["JobDispatcher"]

from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any, List

from taipy.core.common.alias import JobId
from taipy.core.common.logger import TaipyLogger
from taipy.core.data.data_manager import DataManager
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.job import DataNodeWritingError
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.scheduler.executor.synchronous import Synchronous
from taipy.core.task.task import Task


class JobDispatcher:
    """Wrapper around executor that will run jobs.

    Job can be executed on different contexts (locally, etc.). This wrapper
    instantiate the executor based on its args then deal with its low level interface to provide
    a homogeneous way to execute jobs.
    """

    def __init__(self, max_number_of_parallel_execution):
        self._executor, self._nb_worker_available = self.__create(max_number_of_parallel_execution or 1)
        self.__logger = TaipyLogger.get_logger()

    def can_execute(self) -> bool:
        """Returns True if a worker is available for a new run."""
        return self._nb_worker_available > 0

    def dispatch(self, job: Job):
        """Dispatches a Job on an available worker for execution.

        Args:
            job: Element to execute.
        """
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self.__logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            JobManager.set(job)
            self._nb_worker_available -= 1
            future = self._executor.submit(self._call_function, job.id, job.task)
            future.add_done_callback(self.__release_worker)
            future.add_done_callback(partial(self.__update_status, job))
        else:
            job.skipped()
            JobManager.set(job)
            self.__logger.info(f"job {job.id} is skipped.")

    def __release_worker(self, _):
        self._nb_worker_available += 1

    def __update_status(self, job, ft):
        job.update_status(ft)
        JobManager.set(job)

    @staticmethod
    def _needs_to_run(task: Task) -> bool:
        """Returns True if the task outputs are in cache and if the output's last edition date is prior the input's last
        edition date.

        Args:
             task: Task
        Returns:
             True if the task needs to run.
        """
        if len(task.output) == 0:
            return True
        are_outputs_in_cache = all(DataManager().get(dn.id).is_in_cache for dn in task.output.values())
        if not are_outputs_in_cache:
            return True
        if len(task.input) == 0:
            return False
        input_last_edition = max(DataManager().get(dn.id).last_edition_date for dn in task.input.values())
        output_last_edition = min(DataManager().get(dn.id).last_edition_date for dn in task.output.values())
        return input_last_edition > output_last_edition

    @classmethod
    def _call_function(cls, job_id: JobId, task: Task):
        try:
            inputs: List[DataNode] = list(task.input.values())
            outputs: List[DataNode] = list(task.output.values())
            fct = task.function
            results = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, results, job_id)
        except Exception as e:
            return [e]

    @classmethod
    def __read_inputs(cls, inputs: List[DataNode]) -> List[Any]:
        return [DataManager.get(dn.id).read_or_raise() for dn in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataNode], results, job_id: JobId):
        try:
            _results = cls.__extract_results(outputs, results)
            exceptions = []
            for res, dn in zip(_results, outputs):
                try:
                    data_node = DataManager.get(dn.id)
                    data_node.write(res, job_id=job_id)
                    DataManager.set(data_node)
                except Exception as e:
                    exceptions.append(DataNodeWritingError(f"Error writing in datanode id {dn.id}: {e}"))
            return exceptions
        except Exception as e:
            return [e]

    @classmethod
    def __extract_results(cls, outputs: List[DataNode], results: Any) -> List[Any]:
        _results: List[Any] = [results] if len(outputs) == 1 else results

        if len(_results) != len(outputs):
            raise DataNodeWritingError("Error: wrong number of result or task output")

        return _results

    @staticmethod
    def __create(max_number_of_parallel_execution):
        if max_number_of_parallel_execution > 1:
            executor = ProcessPoolExecutor(max_number_of_parallel_execution)
            return executor, (executor._max_workers)
        else:
            return Synchronous(), 1
