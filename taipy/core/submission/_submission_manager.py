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

from typing import List, Optional, Union

from .._manager._manager import _Manager
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_mixin import _VersionMixin
from ..exceptions.exceptions import SubmissionNotDeletedException
from ..notification import EventEntityType, EventOperation, Notifier, _make_event
from ..scenario.scenario import Scenario
from ..sequence.sequence import Sequence
from ..submission.submission import Submission, SubmissionId, SubmissionStatus
from ..task.task import Task


class _SubmissionManager(_Manager[Submission], _VersionMixin):
    _ENTITY_NAME = Submission.__name__
    _repository: _AbstractRepository
    _EVENT_ENTITY_TYPE = EventEntityType.SUBMISSION

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Submission]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    @classmethod
    def _create(cls, entity_id: str, entity_type: str, entity_config: Optional[str]) -> Submission:
        submission = Submission(entity_id=entity_id, entity_type=entity_type, entity_config_id=entity_config)
        cls._set(submission)

        Notifier.publish(_make_event(submission, EventOperation.CREATION))

        return submission

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
    def _is_editable(cls, entity: Union[Submission, str]) -> bool:
        return False

    @classmethod
    def _delete(cls, submission: Union[Submission, SubmissionId]):
        if isinstance(submission, str):
            submission = cls._get(submission)
        if cls._is_deletable(submission):
            super()._delete(submission.id)
        else:
            err = SubmissionNotDeletedException(submission.id)
            cls._logger.error(err)
            raise err

    @classmethod
    def _is_deletable(cls, submission: Union[Submission, SubmissionId]) -> bool:
        if isinstance(submission, str):
            submission = cls._get(submission)
        return submission.is_finished() or submission.submission_status == SubmissionStatus.UNDEFINED
