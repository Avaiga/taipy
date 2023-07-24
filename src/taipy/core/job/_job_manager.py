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
from typing import Callable, Iterable, List, Optional, Union

from .._manager._manager import _Manager
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_manager_factory import _VersionManagerFactory
from .._version._version_mixin import _VersionMixin
from ..exceptions.exceptions import JobNotDeletedException
from ..notification import EventEntityType, EventOperation, _publish_event
from ..task.task import Task
from .job import Job
from .job_id import JobId


class _JobManager(_Manager[Job], _VersionMixin):

    _ENTITY_NAME = Job.__name__
    _ID_PREFIX = "JOB_"
    _repository: _AbstractRepository

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Job]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    _EVENT_ENTITY_TYPE = EventEntityType.JOB

    @classmethod
    def _create(
        cls, task: Task, callbacks: Iterable[Callable], submit_id: str, submit_entity_id: str, force=False
    ) -> Job:
        version = _VersionManagerFactory._build_manager()._get_latest_version()
        job = Job(
            id=JobId(f"{Job._ID_PREFIX}_{task.config_id}_{uuid.uuid4()}"),
            task=task,
            submit_id=submit_id,
            submit_entity_id=submit_entity_id,
            force=force,
            version=version,
        )
        cls._set(job)
        _publish_event(cls._EVENT_ENTITY_TYPE, job.id, EventOperation.CREATION, None)
        job._on_status_change(*callbacks)
        return job

    @classmethod
    def _delete(cls, job: Job, force=False):
        if job.is_finished() or force:
            super()._delete(job.id)
            from .._orchestrator._dispatcher._job_dispatcher import _JobDispatcher

            _JobDispatcher._pop_dispatched_process(job.id)
        else:
            err = JobNotDeletedException(job.id)
            cls._logger.warning(err)
            raise err

    @classmethod
    def _cancel(cls, job: Union[str, Job]):
        job = cls._get(job) if isinstance(job, str) else job

        from .._orchestrator._orchestrator_factory import _OrchestratorFactory

        _OrchestratorFactory._build_orchestrator().cancel_job(job)

    @classmethod
    def _get_latest(cls, task: Task) -> Optional[Job]:
        jobs_of_task = list(filter(lambda job: task in job, cls._get_all()))
        if len(jobs_of_task) == 0:
            return None
        if len(jobs_of_task) == 1:
            return jobs_of_task[0]
        else:
            return max(jobs_of_task)

    @classmethod
    def _is_deletable(cls, job: Union[Job, JobId]) -> bool:
        if isinstance(job, str):
            job = cls._get(job)
        if job.is_finished():
            return True
        return False
