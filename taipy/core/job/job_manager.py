import uuid
from typing import Callable, Iterable, List, Optional

from taipy.core.common.alias import JobId
from taipy.core.common.manager import Manager
from taipy.core.exceptions.job import JobNotDeletedException
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.job.job import Job
from taipy.core.job.job_repository import JobRepository
from taipy.core.task.task import Task


class JobManager(Manager[Job]):
    """
    The Job Manager is responsible for managing all the job-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting jobs.
    """

    _repository = JobRepository()
    ENTITY_NAME = Job.__name__
    ID_PREFIX = "JOB_"

    @classmethod
    def create(cls, task: Task, callbacks: Iterable[Callable], force=False) -> Job:
        """Returns a new job representing a unique execution of the provided task.

        Args:
            task (Task): The task to execute.
            callbacks (Iterable[Callable]): Iterable of callable to be executed on job status change.
            force: Boolean to enforce re execution of the task whatever the cache of the output data nodes.
        Returns:
            A new job, that is created for executing given task.
        """
        job = Job(id=JobId(f"{cls.ID_PREFIX}{uuid.uuid4()}"), task=task, force=force)
        cls.set(job)
        job.on_status_change(*callbacks)
        return job

    @classmethod
    def delete(cls, job: Job, force=False):  # type:ignore
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        if job.is_finished() or force:
            super().delete(job.id)
        else:
            err = JobNotDeletedException(job.id)
            cls._logger.warning(err)
            raise err

    @classmethod
    def get_latest(cls, task: Task) -> Optional[Job]:
        """Allows to retrieve the latest computed job of a task.

        Returns:
            The latest computed job of the task.
        """
        jobs_of_task = list(filter(lambda job: task in job, cls.get_all()))
        if len(jobs_of_task) == 0:
            return None
        if len(jobs_of_task) == 1:
            return jobs_of_task[0]
        else:
            return max(jobs_of_task)
