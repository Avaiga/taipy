# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from threading import Lock
from typing import List, Optional, Union

from taipy.common.logger._taipy_logger import _TaipyLogger

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_mixin import _VersionMixin
from ..exceptions.exceptions import SubmissionNotDeletedException
from ..job.job import Job, Status
from ..notification import EventEntityType, EventOperation, Notifier, _make_event
from ..reason import EntityDoesNotExist, ReasonCollection, SubmissionIsNotFinished
from ..scenario.scenario import Scenario
from ..sequence.sequence import Sequence
from ..submission.submission import Submission, SubmissionId, SubmissionStatus
from ..task.task import Task


class _SubmissionManager(_Manager[Submission], _VersionMixin):
    _ENTITY_NAME = Submission.__name__
    _repository: _AbstractRepository
    _EVENT_ENTITY_TYPE = EventEntityType.SUBMISSION
    __lock = Lock()
    __logger = _TaipyLogger._get_logger()

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Submission]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    @classmethod
    def _create(cls, entity_id: str, entity_type: str, entity_config: Optional[str], **properties) -> Submission:
        submission = Submission(
            entity_id=entity_id, entity_type=entity_type, entity_config_id=entity_config, properties=properties
        )
        cls._set(submission)

        Notifier.publish(_make_event(submission, EventOperation.CREATION))

        return submission

    @classmethod
    def _update_submission_status(cls, submission: Submission, job: Job) -> None:
        with cls.__lock:
            submission = cls._get(submission)

            if submission._submission_status == SubmissionStatus.FAILED:
                return

            job_status = job.status
            if job_status == Status.FAILED:
                cls.__set_submission_status(submission, SubmissionStatus.FAILED, job)
                cls.__logger.debug(
                    f"{job.id} status is {job_status}. Submission status set to `{submission._submission_status}`."
                )
                return
            if job_status == Status.CANCELED:
                submission._is_canceled = True
            elif job_status == Status.BLOCKED:
                submission._blocked_jobs.add(job.id)
                submission._pending_jobs.discard(job.id)
            elif job_status == Status.PENDING or job_status == Status.SUBMITTED:
                submission._pending_jobs.add(job.id)
                submission._blocked_jobs.discard(job.id)
            elif job_status == Status.RUNNING:
                submission._running_jobs.add(job.id)
                submission._pending_jobs.discard(job.id)
            elif job_status == Status.COMPLETED or job_status == Status.SKIPPED:
                submission._is_completed = True  # type: ignore
                submission._blocked_jobs.discard(job.id)
                submission._pending_jobs.discard(job.id)
                submission._running_jobs.discard(job.id)
            elif job_status == Status.ABANDONED:
                submission._is_abandoned = True  # type: ignore
                submission._running_jobs.discard(job.id)
                submission._blocked_jobs.discard(job.id)
                submission._pending_jobs.discard(job.id)
            cls._set(submission)

            # The submission_status is set later to make sure notification for updating
            # the submission_status attribute is triggered
            if submission._is_canceled:
                cls.__set_submission_status(submission, SubmissionStatus.CANCELED, job)
            elif submission._is_abandoned:
                cls.__set_submission_status(submission, SubmissionStatus.UNDEFINED, job)
            elif submission._running_jobs:
                cls.__set_submission_status(submission, SubmissionStatus.RUNNING, job)
            elif submission._pending_jobs:
                cls.__set_submission_status(submission, SubmissionStatus.PENDING, job)
            elif submission._blocked_jobs:
                cls.__set_submission_status(submission, SubmissionStatus.BLOCKED, job)
            elif submission._is_completed:
                cls.__set_submission_status(submission, SubmissionStatus.COMPLETED, job)
            else:
                cls.__set_submission_status(submission, SubmissionStatus.UNDEFINED, job)
            cls.__logger.debug(
                f"{job.id} status is {job_status}. Submission status set to `{submission._submission_status}`."
            )

    @classmethod
    def __set_submission_status(cls, submission: Submission, new_submission_status: SubmissionStatus, job: Job) -> None:
        if not submission._is_in_context:
            submission = cls._get(submission)
        _current_submission_status = submission._submission_status
        submission._submission_status = new_submission_status

        cls._set(submission)

        if _current_submission_status != submission._submission_status:
            event = _make_event(
                submission,
                EventOperation.UPDATE,
                "submission_status",
                submission._submission_status,
                job_triggered_submission_status_changed=job.id,
            )

            if not submission._is_in_context:
                Notifier.publish(event)
            else:
                submission._in_context_attributes_changed_collector.append(event)

    @classmethod
    def _get_latest(cls, entity: Union[Scenario, Sequence, Task]) -> Optional[Submission]:
        entity_id = entity.id if not isinstance(entity, str) else entity
        submissions_of_task = list(filter(lambda submission: submission.entity_id == entity_id, cls._get_all()))
        if len(submissions_of_task) == 0:
            return None
        if len(submissions_of_task) == 1:
            return submissions_of_task[0]
        else:
            return max(submissions_of_task)

    @classmethod
    def _delete(cls, submission: Union[Submission, SubmissionId]) -> None:
        if isinstance(submission, str):
            submission = cls._get(submission)
        if cls._is_deletable(submission):
            super()._delete(submission.id)
        else:
            err = SubmissionNotDeletedException(submission.id)
            cls._logger.error(err)
            raise err

    @classmethod
    def _hard_delete(cls, submission_id: SubmissionId) -> None:
        submission = cls._get(submission_id)
        entity_ids_to_delete = cls._get_children_entity_ids(submission)
        entity_ids_to_delete.submission_ids.add(submission.id)
        cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _get_children_entity_ids(cls, submission: Submission) -> _EntityIds:
        entity_ids = _EntityIds()

        for job in submission.jobs:
            entity_ids.job_ids.add(job.id)

        return entity_ids

    @classmethod
    def _is_deletable(cls, submission: Union[Submission, SubmissionId]) -> ReasonCollection:
        reason_collector = ReasonCollection()

        if isinstance(submission, str):
            submission_id = submission
            submission = cls._get(submission)
            if submission is None:
                reason_collector._add_reason(submission_id, EntityDoesNotExist(submission_id))
                return reason_collector

        if not submission.is_finished() and submission.submission_status != SubmissionStatus.UNDEFINED:
            reason_collector._add_reason(submission.id, SubmissionIsNotFinished(submission.id))

        return reason_collector
