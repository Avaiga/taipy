__all__ = ["Scheduler"]

import itertools
from multiprocessing import Lock
from queue import Queue
from typing import Callable, Iterable, List, Optional, Union

from taipy.core.config.config import Config
from taipy.core.config.job_config import JobConfig
from taipy.core.data.data_manager import DataManager
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scheduler.abstract_scheduler import AbstractScheduler
from taipy.core.scheduler.job_dispatcher import JobDispatcher
from taipy.core.task.task import Task


class Scheduler(AbstractScheduler):
    def __init__(self, job_config: JobConfig = None):
        super().__init__()
        if not job_config:
            job_config = Config.job_config
        self.jobs_to_run: Queue[Job] = Queue()
        self.blocked_jobs: List[Job] = []
        self._dispatcher = JobDispatcher(job_config.nb_of_workers)  # type: ignore
        self.lock = Lock()

    def submit(
        self, pipeline: Pipeline, callbacks: Optional[Iterable[Callable]] = None, force: bool = False
    ) -> List[Job]:
        """Submit pipeline for execution.

        Args:
             pipeline: Pipeline to be transformed into Job(s) for execution.
             callbacks: Optional list of functions that should be executed once the job is done.
             force: Boolean to enforce re execution of the tasks whatever the cache data nodes.

        Returns:
            The created Jobs.
        """
        res = []
        tasks = pipeline.get_sorted_tasks()
        for ts in tasks:
            for task in ts:
                res.append(self.submit_task(task, callbacks, force))
        return res

    def submit_task(self, task: Task, callbacks: Optional[Iterable[Callable]] = None, force: bool = False) -> Job:
        for dn in task.output.values():
            dn.lock_edition()
            DataManager.set(dn)
        job = JobManager.create(task, itertools.chain([self.on_status_change], callbacks or []))
        if self.is_blocked(job):
            job.blocked()
            JobManager.set(job)
            self.blocked_jobs.append(job)
        else:
            job.pending()
            JobManager.set(job)
            self.jobs_to_run.put(job)
            self.__run()
        return job

    @staticmethod
    def is_blocked(obj: Union[Task, Job]) -> bool:
        """Returns True if the execution of the job or the task is blocked by the execution of another job.

        Args:
             obj: Task or Job.

        Returns:
             True if one of its input data nodes is blocked.
        """
        data_nodes = obj.task.input.values() if isinstance(obj, Job) else obj.input.values()
        return any(not DataManager.get(dn.id).is_ready_for_reading for dn in data_nodes)

    def __run(self):
        with self.lock:
            self.__execute_jobs()

    def __execute_jobs(self):
        while not self.jobs_to_run.empty() and self._dispatcher.can_execute():
            job_to_run = self.jobs_to_run.get()
            self._dispatcher.dispatch(job_to_run)

    def on_status_change(self, job: Job):
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
            JobManager.set(job)
            self.blocked_jobs.remove(job)
            self.jobs_to_run.put(job)

    def is_running(self) -> bool:
        pass

    def start(self):
        pass

    def stop(self):
        pass
