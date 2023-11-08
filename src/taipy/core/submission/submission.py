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
from datetime import datetime
from typing import List, Optional, Union

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._reload import _self_reload, _self_setter
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job, JobId
from .submission_id import SubmissionId
from .submission_status import SubmissionStatus


class Submission(_Entity, _Labeled):
    """Hold a user function that will be executed, its parameters and the results.

    A `Task` brings together the user code as function, the inputs and the outputs as data nodes
    (instances of the `DataNode^` class).

    Attributes:
        entity_id (str): The identifier of the `Submittable^` entity.
        jobs (Union[List[JobId], List[Job]]): A list of jobs.
        function (callable): The python function to execute. The _function_ must take as parameter the
            data referenced by inputs data nodes, and must return the data referenced by outputs data nodes.
        input (Union[DataNode^, List[DataNode^]]): The list of inputs.
        output (Union[DataNode^, List[DataNode^]]): The list of outputs.
        id (str): The unique identifier of the task.
        owner_id (str):  The identifier of the owner (sequence_id, scenario_id, cycle_id) or None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent sequences.
        version (str): The string indicates the application version of the task to instantiate. If not provided, the
            latest version is used.
        skippable (bool): If True, indicates that the task can be skipped if no change has been made on inputs. The
            default value is _False_.

    """

    _ID_PREFIX = "SUBMISSION"
    _MANAGER_NAME = "submission"
    __SEPARATOR = "_"

    def __init__(
        self,
        entity_id: str,
        jobs: Optional[Union[List[JobId], List[Job]]] = None,
        submission_id: Optional[str] = None,
    ):
        self.id = submission_id or self.__new_id()
        self._entity_id = entity_id
        self._jobs = jobs or []
        self._creation_date = datetime.now()
        self._submission_status = SubmissionStatus.UNDEFINED

    @staticmethod
    def __new_id() -> str:
        """Generate a unique Submission identifier."""
        return SubmissionId(Submission.__SEPARATOR.join([Submission._ID_PREFIX, str(uuid.uuid4())]))

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def creation_date(self):
        return self._creation_date

    @property
    @_self_reload(_MANAGER_NAME)
    def jobs(self) -> List[Job]:
        jobs = []
        job_manager = _JobManagerFactory._build_manager()

        for job in self._jobs:
            if not isinstance(job, Job):
                jobs.append(job_manager._get(job))
            else:
                jobs.append(job)
        return jobs

    @jobs.setter
    @_self_setter(_MANAGER_NAME)
    def jobs(self, jobs: Union[List[Job], List[JobId]]):
        self._jobs = jobs

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def submission_status(self):
        return self._submission_status

    @submission_status.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def submission_status(self, submission_status):
        self._submission_status = submission_status

    def update_submission_status(self):
        job_manager = _JobManagerFactory._build_manager()

        submission_status = SubmissionStatus.UNDEFINED
        blocked = False
        pending = False
        running = False
        completed = False

        for job in self.jobs:
            # job = job_manager._get(id)
            if not job:
                continue
            if job.is_failed():
                submission_status = SubmissionStatus.FAILED
                break
            if job.is_canceled():
                submission_status = SubmissionStatus.CANCELED
                break
            if not blocked and job.is_blocked():
                blocked = True
            if not pending and job.is_pending():
                pending = True
            if not running and job.is_running():
                running = True
            if not completed and (job.is_completed() or job.is_skipped()):
                completed = True

        if submission_status == SubmissionStatus.UNDEFINED:
            if pending:
                submission_status = SubmissionStatus.PENDING
            elif blocked:
                submission_status = SubmissionStatus.BLOCKED
            elif running:
                submission_status = SubmissionStatus.RUNNING
            elif completed:
                submission_status = SubmissionStatus.COMPLETED

        self.submission_status = submission_status
