import uuid
from typing import Callable, Iterable, List

from taipy.core.common.alias import JobId
from taipy.core.common.logger import TaipyLogger
from taipy.core.exceptions.job import JobNotDeletedException
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.job.job import Job
from taipy.core.job.job_repository import JobRepository
from taipy.core.task.task import Task


class JobManager:
    """
    The Job Manager is responsible for managing all the job-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting jobs.
    """

    __logger = TaipyLogger.get_logger()
    repository = JobRepository()
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
    def set(cls, job: Job):
        """
        Saves or updates a job.

        Parameters:
            job (Job): The job to save.
        """
        cls.repository.save(job)

    @classmethod
    def get(cls, job_id: JobId, default=None) -> Job:
        """Gets the job from the job id given as parameter.

        Parameters:
            job_id (JobId): The job identifier.
            default: Default value to return if no job is found. None is returned if no default value is provided.
        """
        try:
            return cls.repository.load(job_id)
        except ModelNotFound:
            cls.__logger.warning(f"Job: {job_id} does not exist.")
            return default

    @classmethod
    def get_all(cls) -> List[Job]:
        """Gets all the existing jobs.

        Returns:
            List of all jobs.
        """
        return cls.repository.load_all()

    @classmethod
    def delete(cls, job: Job, force=False):
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        if job.is_finished() or force:
            cls.repository.delete(job.id)
        else:
            err = JobNotDeletedException(job.id)
            cls.__logger.warning(err)
            raise err

    @classmethod
    def delete_all(cls):
        """Deletes all jobs."""
        cls.repository.delete_all()

    @classmethod
    def get_latest(cls, task: Task) -> Job:
        """Allows to retrieve the latest computed job of a task.

        Returns:
            The latest computed job of the task.
        """
        return max(filter(lambda job: task in job, cls.get_all()))
