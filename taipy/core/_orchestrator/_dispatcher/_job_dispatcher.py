# Copyright 2021-2024 Avaiga Private Limited
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
import time
from abc import abstractmethod
from queue import Empty
from typing import Optional

from taipy.config.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ...data._data_manager_factory import _DataManagerFactory
from ...job._job_manager_factory import _JobManagerFactory
from ...job.job import Job
from ...task.task import Task
from .._abstract_orchestrator import _AbstractOrchestrator


class _JobDispatcher(threading.Thread):
    """Manages job dispatching (instances of `Job^` class) on executors."""

    _STOP_FLAG = False
    stop_wait = True
    stop_timeout = None
    _logger = _TaipyLogger._get_logger()

    def __init__(self, orchestrator: _AbstractOrchestrator):
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

    def stop(self, wait: bool = True, timeout: Optional[float] = None):
        """Stop the dispatcher.

        Parameters:
            wait (bool): If True, the method will wait for the dispatcher to stop.
            timeout (Optional[float]): The maximum time to wait. If None, the method will wait indefinitely.
        """
        self.stop_wait = wait
        self.stop_timeout = timeout
        self._STOP_FLAG = True

    def run(self):
        self._logger.debug("Job dispatcher started.")
        while not self._STOP_FLAG:
            try:
                if self._can_execute():
                    self.lock.acquire()
                    self._logger.error("-------------------------> Acquired lock to execute job.")
                    if self._STOP_FLAG:
                        self.lock.release()
                        break
                    job = self.orchestrator.jobs_to_run.get(block=True, timeout=0.1)
                    self._logger.error(f"-------------------------> Got job to execute {job.id}.")
                    self._execute_job(job)
                else:
                    time.sleep(0.1)  # We need to sleep to avoid busy waiting.
            except Empty:  # In case the last job of the queue has been removed.
                self._logger.error("-------------------------> Released lock to execute job.")
                self.lock.release()
                pass
            except Exception as e:
                self._logger.error("-------------------------> Released lock to execute job 2.")
                self.lock.release()
                self._logger.exception(e)
                pass
        if self.stop_wait:
            self._logger.debug("Waiting for the dispatcher thread to stop...")
            self.join(timeout=self.stop_timeout)
        self._logger.debug("Job dispatcher stopped.")

    @abstractmethod
    def _can_execute(self) -> bool:
        """Returns True if the dispatcher have resources to dispatch a new job."""
        raise NotImplementedError

    def _execute_job(self, job: Job):
        if job.force or self._needs_to_run(job.task):
            if job.force:
                self._logger.info(f"job {job.id} is forced to be executed.")
            job.running()
            self._dispatch(job)
        else:
            job._unlock_edit_on_outputs()
            job.skipped()
            self._logger.info(f"job {job.id} is skipped.")

    def _execute_jobs_synchronously(self):
        while not self.orchestrator.jobs_to_run.empty():
            with self.lock:
                try:
                    job = self.orchestrator.jobs_to_run.get()
                except Exception:  # In case the last job of the queue has been removed.
                    self._logger.warning(f"{job.id} is no longer in the list of jobs to run.")
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
