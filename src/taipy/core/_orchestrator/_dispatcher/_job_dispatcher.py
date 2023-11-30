# Copyright 2023 Avaiga Private Limited
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
from typing import Dict, Optional

from taipy.config.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ...data._data_manager_factory import _DataManagerFactory
from ...job._job_manager_factory import _JobManagerFactory
from ...job.job import Job
from ...task.task import Task
from .._abstract_orchestrator import _AbstractOrchestrator
from ._task_function_wrapper import _TaskFunctionWrapper


class _JobDispatcher(threading.Thread, _TaskFunctionWrapper):
    """Manages job dispatching (instances of `Job^` class) on executors."""

    _STOP_FLAG = False
    _dispatched_processes: Dict = {}
    __logger = _TaipyLogger._get_logger()
    _nb_available_workers: int = 1

    def __init__(self, orchestrator: Optional[_AbstractOrchestrator]):
        threading.Thread.__init__(self, name="Thread-Taipy-JobDispatcher")
        self.daemon = True
        self.orchestrator = orchestrator
        self.lock = self.orchestrator.lock  # type: ignore
        Config.block_update()

    def start(self):
        """Start the dispatcher"""
        threading.Thread.start(self)

    def is_running(self) -> bool:
        """Return True if the dispatcher is running"""
        return self.is_alive()

    def stop(self):
        """Stop the dispatcher"""
        self._STOP_FLAG = True

    def run(self):
        _TaipyLogger._get_logger().info("Start job dispatcher...")
        while not self._STOP_FLAG:
            try:
                if self._can_execute():
                    with self.lock:
                        job = self.orchestrator.jobs_to_run.get(block=True, timeout=0.1)
                    self._execute_job(job)
            except Exception:  # In case the last job of the queue has been removed.
                pass

    def _can_execute(self) -> bool:
        """Returns True if the dispatcher have resources to execute a new job."""
        return self._nb_available_workers > 0

    def _execute_job(self, job: Job):
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self.__logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            self._dispatch(job)
        else:
            job._unlock_edit_on_outputs()
            job.skipped()
            self.__logger.info(f"job {job.id} is skipped.")

    def _execute_jobs_synchronously(self):
        while not self.orchestrator.jobs_to_run.empty():
            with self.lock:
                try:
                    job = self.orchestrator.jobs_to_run.get()
                except Exception:  # In case the last job of the queue has been removed.
                    self.__logger.warning(f"{job.id} is no longer in the list of jobs to run.")
            self._execute_job(job)

    @staticmethod
    def _needs_to_run(task: Task) -> bool:
        """
        Returns True if the task has no output or if at least one input was modified since the latest run.

        Parameters:
             task (Task^): The task to run.
        Returns:
             True if the task needs to run. False otherwise.
        """
        if not task.skippable:
            return True
        data_manager = _DataManagerFactory._build_manager()
        if len(task.output) == 0:
            return True
        are_outputs_in_cache = all(data_manager._get(dn.id).is_valid for dn in task.output.values())
        if not are_outputs_in_cache:
            return True
        if len(task.input) == 0:
            return False
        input_last_edit = max(data_manager._get(dn.id).last_edit_date for dn in task.input.values())
        output_last_edit = min(data_manager._get(dn.id).last_edit_date for dn in task.output.values())
        return input_last_edit > output_last_edit

    @abstractmethod
    def _dispatch(self, job: Job):
        """
        Dispatches the given `Job^` on an available worker for execution.

        Parameters:
            job (Job^): The job to submit on an executor with an available worker.
        """
        raise NotImplementedError

    @staticmethod
    def _update_job_status(job: Job, exceptions):
        job.update_status(exceptions)
        _JobManagerFactory._build_manager()._set(job)

    @classmethod
    def _set_dispatched_processes(cls, job_id, process):
        cls._dispatched_processes[job_id] = process

    @classmethod
    def _pop_dispatched_process(cls, job_id, default=None):
        return cls._dispatched_processes.pop(job_id, default)  # type: ignore
