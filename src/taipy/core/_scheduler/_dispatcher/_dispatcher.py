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

import threading
from abc import abstractmethod
from multiprocessing import Lock
from typing import Any, Dict, List

from taipy.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ...common.alias import JobId
from ...data._data_manager_factory import _DataManagerFactory
from ...data.data_node import DataNode
from ...exceptions.exceptions import DataNodeWritingError
from ...job._job_manager_factory import _JobManagerFactory
from ...job.job import Job
from ...task.task import Task


class _JobDispatcher(threading.Thread):
    def __init__(self, scheduler):
        threading.Thread.__init__(self)
        self.daemon = True
        self.scheduler = scheduler
        self.lock = Lock()
        _processes: Dict = {}
        self.__logger = _TaipyLogger._get_logger()

    @classmethod
    @abstractmethod
    def is_running(cls) -> bool:
        return NotImplemented

    def run(self):
        while True:
            # try:
            # if self._can_execute() and job := self.scheduler.jobs_to_run.get(block=True):
            # self.__execute_jobs(job)
            # else:
            # except:  # In case the last job of the queue has been removed.
            # TODO: instantiate logger object
            # self.__logger.warning(f"{job.id} is no longer in the list of jobs to run.")

            from time import sleep

            print("going to sleep")
            sleep(1)

    @abstractmethod
    def _can_execute(self) -> bool:
        """Returns True if the dispatcher have resources to execute a new job."""
        raise NotImplementedError

    @abstractmethod
    def _dispatch(self, job: Job):
        """
        Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        raise NotImplementedError

    def __execute_jobs(self, job):
        with self.lock:
            try:
                job = self.scheduler.jobs_to_run.get()
            except:  # In case the last job of the queue has been removed.
                # TODO: instantiate logger object
                self.__logger.warning(f"{job.id} is no longer in the list of jobs to run.")
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self.__logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            _JobManagerFactory._build_manager()._set(job)
            self._dispatch(job)
        else:
            # TODO: unlock_edit_on_outputs function where?
            self.scheduler._unlock_edit_on_outputs(job)
            job.skipped()
            _JobManagerFactory._build_manager()._set(job)
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
        """
        Reads inputs, execute function, and write outputs.

        Parameters:
             job_id (JobId^): The id of the job.
             task (Task^): The task to be executed.
        Returns:
             True if the task needs to run. False otherwise.
        """
        try:
            Config.global_config.storage_folder = storage_folder
            inputs: List[DataNode] = list(task.input.values())
            outputs: List[DataNode] = list(task.output.values())
            fct = task.function
            results = fct(*cls.__read_inputs(inputs))
            return cls.__write_data(outputs, results, job_id)
        except Exception as e:
            return [e]

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
    def _update_status(job, exceptions):
        job.update_status(exceptions)
        _JobManagerFactory._build_manager()._set(job)

    @classmethod
    def _set_process_in_scheduler(cls, job_id, process):
        cls._processes[job_id] = process

    @classmethod
    def _pop_process_in_scheduler(cls, job_id, default=None):
        return cls._processes.pop(job_id, default)  # type: ignore
