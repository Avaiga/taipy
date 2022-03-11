from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any, List

from taipy.core._scheduler._executor._synchronous import _Synchronous
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import JobId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.exceptions import DataNodeWritingError
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job
from taipy.core.task.task import Task


class _JobDispatcher:
    """Manages executors and dispatch jobs on it."""

    def __init__(self, max_number_of_parallel_execution):
        self._executor, self._nb_available_workers = self.__create(max_number_of_parallel_execution or 1)
        self.__logger = _TaipyLogger._get_logger()

    def _can_execute(self) -> bool:
        """Returns True if a worker is available for a new run."""
        return self._nb_available_workers > 0

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (`Job^`): The job to submit on an executor with an available worker.
        """
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self.__logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            _JobManager._set(job)
            self._nb_available_workers -= 1
            future = self._executor.submit(self._run_wrapped_function, job.id, job.task)
            future.add_done_callback(self.__release_worker)
            future.add_done_callback(partial(self.__update_status, job))
        else:
            job.skipped()
            _JobManager._set(job)
            self.__logger.info(f"job {job.id} is skipped.")

    @staticmethod
    def _needs_to_run(task: Task) -> bool:
        """
        Returns True if the task outputs are in cache and if the output's last edition date is prior the input's last
        edition date.

        Parameters:
             task (`Task^`): The task to run.
        Returns:
             True if the task needs to run. False otherwise.
        """
        if len(task.output) == 0:
            return True
        are_outputs_in_cache = all(_DataManager()._get(dn.id)._is_in_cache for dn in task.output.values())
        if not are_outputs_in_cache:
            return True
        if len(task.input) == 0:
            return False
        input_last_edition = max(_DataManager()._get(dn.id).last_edition_date for dn in task.input.values())
        output_last_edition = min(_DataManager()._get(dn.id).last_edition_date for dn in task.output.values())
        return input_last_edition > output_last_edition

    @classmethod
    def _run_wrapped_function(cls, job_id: JobId, task: Task):
        """
        Reads inputs, execute function, and write outputs.

        Parameters:
             job_id (`JobId^`): The id of the job.
             task (`Task^`): The task to be executed.
        Returns:
             True if the task needs to run. False otherwise.
        """
        try:
            inputs: List[DataNode] = list(task.input.values())
            outputs: List[DataNode] = list(task.output.values())
            fct = task.function
            results = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, results, job_id)
        except Exception as e:
            return [e]

    def __release_worker(self, _):
        self._nb_available_workers += 1

    @staticmethod
    def __update_status(job: Job, ft):
        job.update_status(ft)
        _JobManager._set(job)

    @classmethod
    def __read_inputs(cls, inputs: List[DataNode]) -> List[Any]:
        return [_DataManager._get(dn.id).read_or_raise() for dn in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataNode], results, job_id: JobId):
        try:
            if outputs:
                _results = cls.__extract_results(outputs, results)
                exceptions = []
                for res, dn in zip(_results, outputs):
                    try:
                        data_node = _DataManager._get(dn.id)
                        data_node.write(res, job_id=job_id)
                        _DataManager._set(data_node)
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
            return _Synchronous(), 1
