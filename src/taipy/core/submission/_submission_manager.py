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
from ..job.job import Job, JobId
from ..notification import EventEntityType, EventOperation, _publish_event
from ..scenario.scenario_id import ScenarioId
from ..sequence.sequence_id import SequenceId
from ..submission.submission import Submission, SubmissionId


class _SubmissionManager(_Manager[Submission], _VersionMixin):

    _ENTITY_NAME = Submission.__name__
    _repository: _AbstractRepository
    _EVENT_ENTITY_TYPE = EventEntityType.SUBMISSION

    @classmethod
    def _create(
        cls,
        entity_id: str,
        jobs: Union[List[Job], List[JobId]] = None,
    ) -> Submission:
        submission = Submission(entity_id=entity_id, jobs=jobs)
        cls._set(submission)

        return submission
