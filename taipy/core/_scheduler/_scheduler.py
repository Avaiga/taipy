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
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.job.job import Job
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task.task import Task


class _Scheduler(_AbstractScheduler):
    """
    Handles the functional scheduling executors and dispatch jobs on it.

    Attributes:

    """

    jobs_to_run: Queue = Queue()
    blocked_jobs: List = []
    _dispatcher = _JobDispatcher()  # type: ignore
    lock = Lock()

    @classmethod
    def _check_block_and_run_job(cls, job):
        if cls.is_blocked(job):
            cls.__set_block_job(job)
        else:
            cls.__set_pending_job(job)
            cls.__run()

    @classmethod
    def __set_block_job(cls, job):
        job.blocked()
        cls.blocked_jobs.append(job)

    @classmethod
    def __set_pending_job(cls, job):
        job.pending()
        cls.jobs_to_run.put(job)

    @classmethod
    def submit(
        cls, pipeline: Pipeline, callbacks: Optional[Iterable[Callable]] = None, force: bool = False
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
                res.append(cls.submit_task(task, callbacks, force))
        return res

    @classmethod
    def submit_task(cls, task: Task, callbacks: Optional[Iterable[Callable]] = None, force: bool = False) -> Job:
        """Submit the given `Task^` for an execution.

        Parameters:
             task (Task^): The task to submit for execution.
             callbacks: The optional list of functions that should be executed on job status change.
             force (bool): Enforce execution of the task even if its output data nodes are cached.

        Returns:
            The created `Job^`.
        """
        for dn in task.output.values():
            dn.lock_edit()
        job = _JobManagerFactory._build_manager()._create(
            task, itertools.chain([cls._on_status_change], callbacks or [])
        )
        cls._check_block_and_run_job(job)

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
        data_manager = _DataManagerFactory._build_manager()
        return any(not data_manager._get(dn.id).is_ready_for_reading for dn in data_nodes)

    @classmethod
    def __run(cls):
        with cls.lock:
            cls.__execute_jobs()

    @classmethod
    def __execute_jobs(cls):
        while not cls.jobs_to_run.empty() and cls._dispatcher._can_execute():
            job_to_run = cls.jobs_to_run.get()
            cls._dispatcher._dispatch(job_to_run)

    @classmethod
    def _on_status_change(cls, job: Job):
        if job.is_finished():
            if cls.lock.acquire(block=False):
                try:
                    cls.__unblock_jobs()
                    cls.__execute_jobs()
                except:
                    ...
                finally:
                    cls.lock.release()

    @classmethod
    def __unblock_jobs(cls):
        for job in cls.blocked_jobs:
            if not cls.is_blocked(job):
                job.pending()
                cls.blocked_jobs.remove(job)
                cls.jobs_to_run.put(job)

    @classmethod
    def is_running(cls) -> bool:
        """Returns False since the default scheduler is not runnable."""
        return False

    @classmethod
    def initialize(cls):
        pass

    @classmethod
    def start(cls):
        RuntimeError("The default scheduler cannot be started.")

    @classmethod
    def stop(cls):
        RuntimeError("The default scheduler cannot be started nor stopped.")

    @classmethod
    def _set_job_config(cls, job_config: JobConfig = None):
        if not job_config:
            job_config = Config.job_config

        cls._dispatcher._set_executer_and_nb_available_workers(job_config)  # type: ignore
