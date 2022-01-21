__all__ = ["Scheduler"]

import itertools
from multiprocessing import Lock
from queue import Queue
from typing import Callable, Iterable, List, Optional, Union

from taipy.config.config import Config
from taipy.config.job_config import JobConfig
from taipy.job.job import Job
from taipy.scheduler.abstract_scheduler import AbstractScheduler
from taipy.scheduler.job_dispatcher import JobDispatcher
from taipy.task.task import Task


class Scheduler(AbstractScheduler):
    def __init__(self, job_config: JobConfig = Config.job_config()):
        super().__init__()
        self.jobs_to_run: Queue[Job] = Queue()
        self.blocked_jobs: List[Job] = []
        self._dispatcher = JobDispatcher(job_config.nb_of_workers)
        self.lock = Lock()

    def submit(self, pipeline, callbacks: Optional[Iterable[Callable]] = None) -> List[Job]:
        """Submit pipeline for execution.

        Args:
             pipeline: Pipeline to be transformed into Job(s) for execution.
             callbacks: Optional list of functions that should be executed once the job is done.

        Returns:
            Job created.
        """
        res = []
        tasks = pipeline.get_sorted_tasks()
        for ts in tasks:
            for task in ts:
                res.append(self.submit_task(task, callbacks))
        return res

    def submit_task(self, task: Task, callbacks: Optional[Iterable[Callable]] = None) -> Job:
        for ds in task.output.values():
            ds.lock_edition()
            self.data_manager.set(ds)
        job = self.job_manager.create(task, itertools.chain([self.on_status_change], callbacks or []))
        if self.is_blocked(job):
            job.blocked()
            self.job_manager.set(job)
            self.blocked_jobs.append(job)
        else:
            job.pending()
            self.job_manager.set(job)
            self.jobs_to_run.put(job)
            self.__run()
        return job

    def is_blocked(self, obj: Union[Task, Job]) -> bool:
        """Returns True if the Job cannot be executed

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
            self.job_manager.set(job)
            self.blocked_jobs.remove(job)
            self.jobs_to_run.put(job)

    def is_running(self) -> bool:
        pass

    def start(self):
        pass

    def stop(self):
        pass
