# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any, List

from taipy.core._scheduler._executor._synchronous import _Synchronous
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import JobId
from taipy.core.config import Config, JobConfig
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node import DataNode
from taipy.core.exceptions.exceptions import DataNodeWritingError
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.task.task import Task


class _JobDispatcher:
    """Manages executors and dispatch jobs (instances of `Job^` class) on it."""

    def __init__(self):
        self._set_executer_and_nb_available_workers(Config.job_config)
        self.__logger = _TaipyLogger._get_logger()

    def _can_execute(self) -> bool:
        """Returns True if a worker is available for a new run."""
        return self._nb_available_workers > 0

    def _dispatch(self, job: Job):
        """Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self.__logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            _JobManagerFactory._build_manager()._set(job)
            self._nb_available_workers -= 1
            future = self._executor.submit(
                self._run_wrapped_function, Config.global_config.storage_folder, job.id, job.task
            )
            future.add_done_callback(self.__release_worker)
            future.add_done_callback(partial(self.__update_status, job))
        else:
            job.skipped()
            _JobManagerFactory._build_manager()._set(job)
            self.__unlock_edit_on_outputs(job)
            self.__logger.info(f"job {job.id} is skipped.")

    @staticmethod
    def _needs_to_run(task: Task) -> bool:
        """
        Returns True if the task has no output or if at least one input was modified since the latest run.

        Parameters:
             task (Task^): The task to run.
        Returns:
             True if the task needs to run. False otherwise.
        """
        data_manager = _DataManagerFactory._build_manager()
        if len(task.output) == 0:
            return True
        are_outputs_in_cache = all(data_manager._get(dn.id)._is_in_cache for dn in task.output.values())
        if not are_outputs_in_cache:
            return True
        if len(task.input) == 0:
            return False
        input_last_edit = max(data_manager._get(dn.id).last_edit_date for dn in task.input.values())
        output_last_edit = min(data_manager._get(dn.id).last_edit_date for dn in task.output.values())
        return input_last_edit > output_last_edit

    @classmethod
    def _run_wrapped_function(cls, storage_folder: str, job_id: JobId, task: Task):
        """)
        Reads inputs, execute function, and write outputs.

        Parameters:
             job_id (JobId^): The id of the job.
             task (Task^): The task to be executed.
        Returns:
             True if the task needs to run. False otherwise.
        """
        try:
            Config.configure_global_app(storage_folder=storage_folder)
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
        _JobManagerFactory._build_manager()._set(job)

    @classmethod
    def __read_inputs(cls, inputs: List[DataNode]) -> List[Any]:
        data_manager = _DataManagerFactory._build_manager()
        return [data_manager._get(dn.id).read_or_raise() for dn in inputs]

    @classmethod
    def __write_data(cls, outputs: List[DataNode], results, job_id: JobId):
        data_manager = _DataManagerFactory._build_manager()
        try:
            if outputs:
                _results = cls.__extract_results(outputs, results)
                exceptions = []
                for res, dn in zip(_results, outputs):
                    try:
                        data_node = data_manager._get(dn.id)
                        data_node.write(res, job_id=job_id)
                        data_manager._set(data_node)
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
    def __create(job_config: JobConfig):
        if job_config.is_standalone:
            executor = ProcessPoolExecutor(job_config.nb_of_workers or 1)
            return executor, (executor._max_workers)  # type: ignore
        else:
            return _Synchronous(), 1

    def _set_executer_and_nb_available_workers(self, job_config: JobConfig):
        self._executor, self._nb_available_workers = self.__create(job_config)

    @staticmethod
    def __unlock_edit_on_outputs(job):
        for dn in job.task.output.values():
            dn.unlock_edit(job_id=job.id)
