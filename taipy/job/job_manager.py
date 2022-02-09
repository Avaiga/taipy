import logging
import uuid
from typing import Callable, Iterable, List

from taipy.common.alias import JobId
from taipy.exceptions import JobNotDeletedException, ModelNotFound, NonExistingJob
from taipy.job.job import Job
from taipy.job.job_repository import JobRepository
from taipy.task.task import Task


class JobManager:
    """
    The Job Manager is responsible for managing all the job-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting jobs.
    """

    repository = JobRepository()
    ID_PREFIX = "JOB_"

    def create(self, task: Task, callbacks: Iterable[Callable]) -> Job:
        """Returns a new job representing a unique execution of the provided task.

        Args:
            task (Task): The task to execute.
            callbacks (Iterable[Callable]): Iterable of callable to be executed on job status change.

        Returns:
            A new job, that is created for executing given task.
        """
        job = Job(id=JobId(f"{self.ID_PREFIX}{uuid.uuid4()}"), task=task)
        self.set(job)
        job.on_status_change(*callbacks)
        return job

    def set(self, job: Job):
        """
        Saves or updates a job.

        Parameters:
            job (Job): The job to save.
        """
        self.repository.save(job)

    def get(self, job_id: JobId) -> Job:
        """Gets the job from the job id given as parameter.

        Returns:
            The Job corresponding to the id.

        Raises:
            NonExistingJob: if not found.
        """
        try:
            return self.repository.load(job_id)
        except ModelNotFound:
            logging.error(f"Job: {job_id} does not exist.")
            raise NonExistingJob(job_id)

    def get_all(self) -> List[Job]:
        """Gets all the existing jobs.

        Returns:
            List of all jobs.
        """
        return self.repository.load_all()

    def delete(self, job: Job, force=False):
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        if job.is_finished() or force:
            self.repository.delete(job.id)
        else:
            err = JobNotDeletedException(job.id)
            logging.warning(err)
            raise err

    def delete_all(self):
        """Deletes all jobs."""
        self.repository.delete_all()

    def get_latest(self, task: Task) -> Job:
        """Allows to retrieve the latest computed job of a task.

        Returns:
            The latest computed job of the task.
        """
        return max(filter(lambda job: task in job, self.get_all()))
