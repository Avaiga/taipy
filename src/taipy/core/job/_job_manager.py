# Copyright 2023 Avaiga Private Limited
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
from typing import Callable, Iterable, Optional, Union

from .._manager._manager import _Manager
from .._version._version_manager_factory import _VersionManagerFactory
from ..common.alias import JobId
from ..exceptions.exceptions import JobNotDeletedException
from ..task.task import Task
from ._job_repository_factory import _JobRepositoryFactory
from .job import Job


class _JobManager(_Manager[Job]):
    _repository = _JobRepositoryFactory._build_repository()  # type: ignore
    _ENTITY_NAME = Job.__name__
    _ID_PREFIX = "JOB_"

    @classmethod
    def _create(cls, task: Task, callbacks: Iterable[Callable], submit_id: str, force=False) -> Job:
        version = _VersionManagerFactory._build_manager()._get_latest_version()
        job = Job(
            id=JobId(f"{cls._ID_PREFIX}{task.config_id}_{uuid.uuid4()}"),
            task=task,
            submit_id=submit_id,
            force=force,
            version=version,
        )
        cls._set(job)
        job._on_status_change(*callbacks)
        return job

    @classmethod
    def _delete(cls, job: Job, force=False):  # type:ignore
        if job.is_finished() or force:
            super()._delete(job.id)
            from .._scheduler._dispatcher._job_dispatcher import _JobDispatcher

            _JobDispatcher._pop_dispatched_process(job.id)  # type: ignore
        else:
            err = JobNotDeletedException(job.id)
            cls._logger.warning(err)
            raise err

    @classmethod
    def _cancel(cls, job: Union[str, Job]):
        job = cls._get(job) if isinstance(job, str) else job

        from .._scheduler._scheduler_factory import _SchedulerFactory

        _SchedulerFactory._build_scheduler().cancel_job(job)

    @classmethod
    def _get_latest(cls, task: Task) -> Optional[Job]:
        jobs_of_task = list(filter(lambda job: task in job, cls._get_all()))
        if len(jobs_of_task) == 0:
            return None
        if len(jobs_of_task) == 1:
            return jobs_of_task[0]
        else:
            return max(jobs_of_task)
