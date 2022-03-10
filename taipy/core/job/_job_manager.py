import uuid
from typing import Callable, Iterable, Optional

from taipy.core.common._manager import _Manager
from taipy.core.common.alias import JobId
from taipy.core.exceptions.exceptions import JobNotDeletedException
from taipy.core.job._job_repository import _JobRepository
from taipy.core.job.job import Job
from taipy.core.task.task import Task


class _JobManager(_Manager[Job]):

    _repository = _JobRepository()
    _ENTITY_NAME = Job.__name__
    _ID_PREFIX = "JOB_"

    @classmethod
    def _create(cls, task: Task, callbacks: Iterable[Callable], force=False) -> Job:
        job = Job(id=JobId(f"{cls._ID_PREFIX}{uuid.uuid4()}"), task=task, force=force)
        cls._set(job)
        job.on_status_change(*callbacks)
        return job

    @classmethod
    def _delete(cls, job: Job, force=False, **kwargs):  # type:ignore
        if job.is_finished() or force:
            super()._delete(job.id)
        else:
            err = JobNotDeletedException(job.id)
            cls._logger.warning(err)
            raise err

    @classmethod
    def _get_latest(cls, task: Task) -> Optional[Job]:
        jobs_of_task = list(filter(lambda job: task in job, cls._get_all()))
        if len(jobs_of_task) == 0:
            return None
        if len(jobs_of_task) == 1:
            return jobs_of_task[0]
        else:
            return max(jobs_of_task)
