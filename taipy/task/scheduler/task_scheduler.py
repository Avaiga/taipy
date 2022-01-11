__all__ = ["TaskScheduler"]

import logging
import uuid
from multiprocessing import Lock
from queue import Queue
from typing import Callable, Dict, Iterable, List, Optional, Union

from taipy.config.config import Config
from taipy.config.job_config import JobConfig
from taipy.exceptions import JobNotDeletedException, NonExistingJob
from taipy.task.task import Task

from ...common.alias import JobId
from ...data.manager import DataManager
from .job import Job
from .job_dispatcher import JobDispatcher


class TaskScheduler:
    """Creates and schedules Jobs from their Task.

    Attributes:
        data_manager: DataManager is an element that retrieves and deals with Data Source.
        jobs_to_run: Queue of Jobs to execute.
        blocked_jobs:
            List of Jobs that can't be executed because some of their input is waiting for the output of other jobs.
    """

    def __init__(self, job_config: JobConfig = Config.job_config()):
        self.__JOBS: Dict[JobId, Job] = {}
        self.jobs_to_run: Queue[Job] = Queue()
        self.blocked_jobs: List[Job] = []
        self.__executor = JobDispatcher(
            job_config.parallel_execution or JobConfig.DEFAULT_PARALLEL_EXECUTION,
            job_config.nb_of_workers,
        )
        self.data_manager: DataManager = DataManager()
        self.lock = Lock()

    def submit(self, task: Task, callbacks: Optional[Iterable[Callable]] = None) -> Job:
        """Submit task to execution.

        Transforms task to job and enqueues it for execution.

        Args:
             task: Task to be transformed into Job for execution.
             callbacks: Optional list of functions that should be executed once the job is done.

        Returns:
            Job created.
        """
        for ds in task.output.values():
            ds.lock_edition()
            self.data_manager.set(ds)
        job = self.__create_job(task, callbacks or [])
        if self.is_blocked(job):
            job.blocked()
            self.blocked_jobs.append(job)
        else:
            job.pending()
            self.jobs_to_run.put(job)
            self.__run()
        return job

    def get_job(self, job_id: JobId) -> Job:
        """Allows to retrieve a job from its id.

        Returns:
            The Job corresponding to this id.

        Raises:
            NonExistingJob: if not found.
        """
        try:
            return self.__JOBS[job_id]
        except KeyError:
            logging.error(f"Job: {job_id} does not exist.")
            raise NonExistingJob(job_id)

    def get_jobs(self) -> List[Job]:
        """Allows to retrieve all jobs.

        Returns:
            List of all jobs.
        """
        return list(self.__JOBS.values())

    def delete(self, job: Job):
        """Deletes a job if finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        if job.is_finished():
            del self.__JOBS[job.id]
        else:
            err = JobNotDeletedException(job.id)
            logging.warning(err)
            raise err

    def delete_all(self):
        """Deletes all jobs."""
        self.__JOBS: Dict[JobId, Job] = {}

    def get_latest_job(self, task: Task) -> Job:
        """Allows to retrieve the latest computed job of a task.

        Returns:
            The latest computed job of the task.
        """
        return max(filter(lambda job: task in job, self.__JOBS.values()))

    def is_blocked(self, obj: Union[Task, Job]) -> bool:
        """Allows to know if all data sources of a task or a job are ready

        Args:
             obj: Task or Job

        Returns:
             True if one of its input data source is blocked
        """
        data_sources = obj.task.input.values() if isinstance(obj, Job) else obj.input.values()
        return any(not self.data_manager.get(ds.id).is_ready_for_reading for ds in data_sources)

    def __run(self):
        with self.lock:
            self.__execute_jobs()

    def __execute_jobs(self):
        while not self.jobs_to_run.empty() and self.__executor.can_execute():
            job_to_run = self.jobs_to_run.get()
            self.__executor.execute(job_to_run)

    def __create_job(self, task: Task, callbacks: Iterable[Callable]) -> Job:
        job = Job(id=JobId(f"job_id_{task.id}_{uuid.uuid4()}"), task=task)
        self.__JOBS[job.id] = job
        job.on_status_change(self.__job_finished, *callbacks)
        return job

    def __job_finished(self, job: Job):
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
            self.blocked_jobs.remove(job)
            self.jobs_to_run.put(job)
