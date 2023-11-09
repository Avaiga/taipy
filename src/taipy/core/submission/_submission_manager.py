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

from typing import Callable, List, Optional, Type, Union

from taipy.config import Config
from taipy.config.common.scope import Scope

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._orchestrator._abstract_orchestrator import _AbstractOrchestrator
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_manager_factory import _VersionManagerFactory
from .._version._version_mixin import _VersionMixin
from ..common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from ..config.task_config import TaskConfig
from ..cycle.cycle_id import CycleId
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions.exceptions import NonExistingTask
from ..notification import EventEntityType, EventOperation, _publish_event
from ..scenario.scenario_id import ScenarioId
from ..sequence.sequence_id import SequenceId
from ..submission.submission import Submission, SubmissionId


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
    def _create(
        cls,
        entity_id: str,
    ) -> Submission:
        submission = Submission(entity_id=entity_id)
        cls._set(submission)

        _publish_event(cls._EVENT_ENTITY_TYPE, submission.id, EventOperation.CREATION, None)

        return submission

    @classmethod
    def _get_latest(cls, submittable) -> Optional[Submission]:
        # TODO: add get latest as api in tp
        submittable_id = submittable.id if not isinstance(submittable, str) else submittable
        submissions_of_task = list(filter(lambda submission: submission.entity_id == submittable_id, cls._get_all()))
        if len(submissions_of_task) == 0:
            return None
        if len(submissions_of_task) == 1:
            return submissions_of_task[0]
        else:
            return max(submissions_of_task)
