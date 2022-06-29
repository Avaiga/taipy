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

import uuid
from typing import Callable, Iterable, Optional

from ._job_repository import _JobRepository
from .job import Job
from .._manager._manager import _Manager
from ..common.alias import JobId
from ..exceptions.exceptions import JobNotDeletedException
from ..task.task import Task


class _JobManager(_Manager[Job]):

    _repository = _JobRepository()
    _ENTITY_NAME = Job.__name__
    _ID_PREFIX = "JOB_"

    @classmethod
    def _create(cls, task: Task, callbacks: Iterable[Callable], force=False) -> Job:
        job = Job(id=JobId(f"{cls._ID_PREFIX}{task.config_id}_{uuid.uuid4()}"), task=task, force=force)
        cls._set(job)
        job._on_status_change(*callbacks)
        return job

    @classmethod
    def _delete(cls, job: Job, force=False):  # type:ignore
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
