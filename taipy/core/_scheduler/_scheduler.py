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

import itertools
from multiprocessing import Lock
from queue import Queue
from typing import Callable, Iterable, List, Optional, Union

from taipy.core._scheduler._abstract_scheduler import _AbstractScheduler
from taipy.core._scheduler._job_dispatcher import _JobDispatcher
from taipy.core.config.config import Config
from taipy.core.config.job_config import JobConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task.task import Task


class _Scheduler(_AbstractScheduler):
    """
    Handles the functional scheduling executors and dispatch jobs on it.

    Attributes:

    """

    def __init__(self, job_config: JobConfig = None):
        super().__init__()
        if not job_config:
            job_config = Config.job_config
        self.jobs_to_run: Queue[Job] = Queue()
        self.blocked_jobs: List[Job] = []
        self._dispatcher = _JobDispatcher(job_config.nb_of_workers)  # type: ignore
        self.lock = Lock()

    def submit(
        self, pipeline: Pipeline, callbacks: Optional[Iterable[Callable]] = None, force: bool = False
    ) -> List[Job]:
        """Submit the given `Pipeline^` for an execution.

        Parameters:
             pipeline (Pipeline^): The pipeline to submit for execution.
             callbacks: The optional list of functions that should be executed on jobs status change.
             force (bool) : Enforce execution of the pipeline's tasks even if their output data
                nodes are cached.

        Returns:
            The created Jobs.
        """
        res = []
        tasks = pipeline._get_sorted_tasks()
        for ts in tasks:
            for task in ts:
                res.append(self.submit_task(task, callbacks, force))
        return res

    def submit_task(self, task: Task, callbacks: Optional[Iterable[Callable]] = None, force: bool = False) -> Job:
        """Submit the given `Task^` for an execution.

        Parameters:
             task (Task^): The task to submit for execution.
             callbacks: The optional list of functions that should be executed on job status change.
             force (bool): Enforce execution of the task even if its output data nodes are cached.

        Returns:
            The created `Job^`.
        """
        for dn in task.output.values():
            dn.lock_edition()
            _DataManager._set(dn)
        job = _JobManager._create(task, itertools.chain([self._on_status_change], callbacks or []))
        if self.is_blocked(job):
            job.blocked()
            _JobManager._set(job)
            self.blocked_jobs.append(job)
        else:
            job.pending()
            _JobManager._set(job)
            self.jobs_to_run.put(job)
            self.__run()
        return job

    @staticmethod
    def is_blocked(obj: Union[Task, Job]) -> bool:
        """Returns True if the execution of the `Job^` or the `Task^` is blocked by the execution of another `Job^`.

        Parameters:
             obj (Union[Task^, Job^]): The job or task entity to run.

        Returns:
             True if one of its input data nodes is blocked.
        """
        data_nodes = obj.task.input.values() if isinstance(obj, Job) else obj.input.values()
        return any(not _DataManager._get(dn.id).is_ready_for_reading for dn in data_nodes)

    def __run(self):
        with self.lock:
            self.__execute_jobs()

    def __execute_jobs(self):
        while not self.jobs_to_run.empty() and self._dispatcher._can_execute():
            job_to_run = self.jobs_to_run.get()
            self._dispatcher._dispatch(job_to_run)

    def _on_status_change(self, job: Job):
        if job.is_finished():
            if self.lock.acquire(block=False):
                try:
                    self.__unblock_jobs()
                    self.__execute_jobs()
                except:
                    ...
                finally:
                    self.lock.release()

    def __unblock_jobs(self):
        jobs_to_unblock = [job for job in self.blocked_jobs if not self.is_blocked(job)]
        for job in jobs_to_unblock:
            job.pending()
            _JobManager._set(job)
            self.blocked_jobs.remove(job)
            self.jobs_to_run.put(job)

    def is_running(self) -> bool:
        """Returns False since the default scheduler is not runnable."""
        return False

    def start(self):
        RuntimeError("The default scheduler cannot be started.")

    def stop(self):
        RuntimeError("The default scheduler cannot be started nor stopped.")
