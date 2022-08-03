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
import uuid
from multiprocessing import Lock
from queue import Queue
from typing import Callable, Iterable, List, Optional, Set, Union

from taipy.config.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ..data._data_manager_factory import _DataManagerFactory
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..pipeline.pipeline import Pipeline
from ..task.task import Task
from ._abstract_scheduler import _AbstractScheduler


class _Scheduler(_AbstractScheduler):
    """
    Handles the functional scheduling.

    Attributes:

    """

    jobs_to_run: Queue = Queue()
    blocked_jobs: List = []
    lock = Lock()
    __logger = _TaipyLogger._get_logger()

    @classmethod
    def initialize(cls):
        pass

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
        submit_id = cls.__generate_submit_id()
        res = []
        tasks = pipeline._get_sorted_tasks()
        for ts in tasks:
            for task in ts:
                res.append(cls.submit_task(task, submit_id, callbacks=callbacks, force=force))
        return res

    @classmethod
    def submit_task(
        cls, task: Task, submit_id: str = None, callbacks: Optional[Iterable[Callable]] = None, force: bool = False
    ) -> Job:
        """Submit the given `Task^` for an execution.

        Parameters:
             task (Task^): The task to submit for execution.
             submit_id (str): The optional id to differentiate each submission.
             callbacks: The optional list of functions that should be executed on job status change.
             force (bool): Enforce execution of the task even if its output data nodes are cached.

        Returns:
            The created `Job^`.
        """
        submit_id = submit_id if submit_id else cls.__generate_submit_id()

        for dn in task.output.values():
            dn.lock_edit()
        job = _JobManagerFactory._build_manager()._create(
            task, itertools.chain([cls._on_status_change], callbacks or []), submit_id
        )
        cls._schedule_job_to_run_or_block(job)

        return job

    @staticmethod
    def __generate_submit_id():
        return f"SUBMISSION_{str(uuid.uuid4())}"

    @classmethod
    def _schedule_job_to_run_or_block(cls, job: Job):
        if cls._is_blocked(job):
            job.blocked()
            with cls.lock:
                cls.blocked_jobs.append(job)
        else:
            job.pending()
            with cls.lock:
                cls.jobs_to_run.put(job)
            cls.__check_and_execute_jobs_if_development_mode()

    @staticmethod
    def _is_blocked(obj: Union[Task, Job]) -> bool:
        """Returns True if the execution of the `Job^` or the `Task^` is blocked by the execution of another `Job^`.

        Parameters:
             obj (Union[Task^, Job^]): The job or task entity to run.

        Returns:
             True if one of its input data nodes is blocked.
        """
        data_nodes = obj.task.input.values() if isinstance(obj, Job) else obj.input.values()
        data_manager = _DataManagerFactory._build_manager()
        return any(not data_manager._get(dn.id).is_ready_for_reading for dn in data_nodes)

    @staticmethod
    def _unlock_edit_on_outputs(jobs: Union[Job, List[Job], Set[Job]]):
        jobs = [jobs] if isinstance(jobs, Job) else jobs
        for job in jobs:
            for dn in job.task.output.values():
                dn.unlock_edit(at=dn.last_edit_date)

    @classmethod
    def _on_status_change(cls, job: Job):
        if job.is_completed():
            cls.__unblock_jobs()
            cls.__check_and_execute_jobs_if_development_mode()
        elif job.is_canceled():
            cls.__check_and_execute_jobs_if_development_mode()

    @classmethod
    def __unblock_jobs(cls):
        for job in cls.blocked_jobs:
            if not cls._is_blocked(job):
                with cls.lock:
                    job.pending()
                    cls.__remove_blocked_job(job)
                    cls.jobs_to_run.put(job)

    @classmethod
    def __remove_blocked_job(cls, job):
        try:  # In case the job has been removed from the list of blocked_jobs.
            cls.blocked_jobs.remove(job)
        except:
            cls.__logger.warning(f"{job.id} is not in the blocked list anymore.")

    @classmethod
    def cancel_job(cls, job: Job):
        to_cancel_jobs = set([job])
        to_cancel_jobs.update(cls.__find_subsequent_jobs(job.submit_id, set(job.task.output.keys())))
        with cls.lock:
            cls.__remove_blocked_jobs(to_cancel_jobs)
            cls.__remove_jobs_to_run(to_cancel_jobs)
            cls.__cancel_jobs(job.id, to_cancel_jobs)
            cls._unlock_edit_on_outputs(to_cancel_jobs)

    @classmethod
    def __find_subsequent_jobs(cls, submit_id, output_dn_config_ids: Set) -> Set[Job]:
        next_output_dn_config_ids = set()
        subsequent_jobs = set()
        for job in cls.blocked_jobs:
            job_input_dn_config_ids = job.task.input.keys()
            if job.submit_id == submit_id and len(output_dn_config_ids.intersection(job_input_dn_config_ids)) > 0:
                next_output_dn_config_ids.update(job.task.output.keys())
                subsequent_jobs.update([job])
        if len(next_output_dn_config_ids) > 0:
            subsequent_jobs.update(
                cls.__find_subsequent_jobs(submit_id, output_dn_config_ids=next_output_dn_config_ids)
            )
        return subsequent_jobs

    @classmethod
    def __remove_blocked_jobs(cls, jobs):
        for job in jobs:
            cls.__remove_blocked_job(job)

    @classmethod
    def __remove_jobs_to_run(cls, jobs):
        new_jobs_to_run: Queue = Queue()
        while not cls.jobs_to_run.empty():
            current_job = cls.jobs_to_run.get()
            if current_job not in jobs:
                new_jobs_to_run.put(current_job)
        cls.jobs_to_run = new_jobs_to_run

    @classmethod
    def __cancel_jobs(cls, job_id_to_cancel, jobs):
        from ._scheduler_factory import _SchedulerFactory

        for job in jobs:
            if job.id in _SchedulerFactory._dispatcher._dispatched_processes.keys():
                cls.__logger.warning(f"{job.id} is running and cannot be canceled.")
            else:
                if job_id_to_cancel == job.id:
                    job.canceled()
                else:
                    job.abandoned()

    @staticmethod
    def __check_and_execute_jobs_if_development_mode():
        if Config.job_config.is_development:
            from ._scheduler_factory import _SchedulerFactory

            _SchedulerFactory._get_dispatcher()._execute_jobs_synchronously()
