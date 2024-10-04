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

import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..job.job import Job, JobId
from ..notification import Event, EventEntityType, EventOperation, _make_event
from ..reason.reason_collection import ReasonCollection
from .submission_id import SubmissionId
from .submission_status import SubmissionStatus


class Submission(_Entity, _Labeled):
    """Submission of a submittable entity: `Task^`, a `Sequence^` or a `Scenario^`.

    Task, Sequence, and Scenario entities can be submitted for execution. The submission
    represents the unique request to execute a submittable entity. The submission is created
    at the time the entity is submitted.

    The submission holds the jobs created by the execution of the submittable and the
    `SubmissionStatus^`. The status is lively updated by Taipy during the execution of the jobs.

    ??? example

        ```python
        import taipy as tp
        from taipy import Config

        def by_two(x: int):
            return x * 2

        if __name__ == "__main__":
            # Configure scenarios
            input_cfg = Config.configure_data_node("my_input")
            result_cfg = Config.configure_data_node("my_result")
            task_cfg = Config.configure_task("my_double", function=by_two, input=input_cfg, output=result_cfg)
            scenario_cfg = Config.configure_scenario("my_scenario", task_configs=[task_cfg])

            # Create a new scenario from the configuration
            scenario = tp.create_scenario(scenario_cfg)

            # Write the input data and submit the scenario
            scenario.my_input.write(3)
            submission = scenario.submit()

            # Retrieve the list of jobs, the submission status, and the creation date
            jobs = submission.jobs
            status = submission.submission_status
            creation_date = submission.creation_date
        ```
    """

    _ID_PREFIX = "SUBMISSION"
    _MANAGER_NAME = "submission"
    __SEPARATOR = "_"
    lock = threading.Lock()

    id: SubmissionId
    """The identifier of the `Submission` entity."""

    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        entity_config_id: Optional[str] = None,
        id: Optional[SubmissionId] = None,
        jobs: Optional[Union[List[Job], List[JobId]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        creation_date: Optional[datetime] = None,
        submission_status: Optional[SubmissionStatus] = None,
        version: Optional[str] = None,
    ):
        self._entity_id = entity_id
        self._entity_type = entity_type
        self._entity_config_id = entity_config_id
        self.id = id or self.__new_id()
        self._jobs: Union[List[Job], List[JobId], List] = jobs or []
        self._creation_date = creation_date or datetime.now()
        self._submission_status = submission_status or SubmissionStatus.SUBMITTED
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()

        properties = properties or {}
        self._properties = _Properties(self, **properties.copy())

        self._is_abandoned = False
        self._is_completed = False
        self._is_canceled = False

        self._running_jobs: Set = set()
        self._blocked_jobs: Set = set()
        self._pending_jobs: Set = set()

    def __lt__(self, other) -> bool:
        """Compare the creation date of two submissions."""
        return self.creation_date.timestamp() < other.creation_date.timestamp()

    def __le__(self, other) -> bool:
        """Compare the creation date of two submissions."""
        return self.creation_date.timestamp() <= other.creation_date.timestamp()

    def __gt__(self, other) -> bool:
        """Compare the creation date of two submissions."""
        return self.creation_date.timestamp() > other.creation_date.timestamp()

    def __ge__(self, other) -> bool:
        """Compare the creation date of two submissions."""
        return self.creation_date.timestamp() >= other.creation_date.timestamp()

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Check if a submission is equal to another submission."""
        return isinstance(other, Submission) and self.id == other.id

    @property
    def entity_id(self) -> str:
        """The identifier of the entity that was submitted."""
        return self._entity_id

    @property
    def entity_type(self) -> str:
        """The type of the entity that was submitted."""
        return self._entity_type

    @property
    def entity_config_id(self) -> Optional[str]:
        """The config id of the entity that was submitted."""
        return self._entity_config_id

    @property
    def properties(self) -> _Properties:
        """A dictionary of additional properties."""
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property
    def creation_date(self) -> datetime:
        """The date and time when the submission was created."""
        return self._creation_date

    @property
    @_self_reload(_MANAGER_NAME)
    def submitted_at(self) -> Optional[datetime]:
        """The date and time when the submission was submitted.

        The submitted date and time corresponds to the date and time of the first job
        that was submitted. If no job was submitted, the submitted date and time is None.
        """
        jobs_submitted_at = [job.submitted_at for job in self.jobs if job.submitted_at]
        if jobs_submitted_at:
            return min(jobs_submitted_at)
        return None

    @property
    @_self_reload(_MANAGER_NAME)
    def run_at(self) -> Optional[datetime]:
        """The date and time when the submission was run.

        The run date and time corresponds to the date and time of the first job
        that was run. If no job was run, the run date and time is None.
        """
        jobs_run_at = [job.run_at for job in self.jobs if job.run_at]
        if jobs_run_at:
            return min(jobs_run_at)
        return None

    @property
    @_self_reload(_MANAGER_NAME)
    def finished_at(self) -> Optional[datetime]:
        """The date and time when the submission was finished.

        The finished date and time corresponds to the date and time of the last job
        that was completed. If at least one of the jobs is not finished, the finished
        date and time is None.
        """
        if all(job.finished_at for job in self.jobs):
            return max([job.finished_at for job in self.jobs if job.finished_at])
        return None

    @property
    @_self_reload(_MANAGER_NAME)
    def execution_duration(self) -> Optional[float]:
        """The duration of the submission execution in seconds.

        The execution duration in seconds is the duration from the first job running
        to the last job completion. If no job was run, the execution duration is None.
        If at least one job is not finished, the execution duration is the duration
        from the first job running time to the current time.
        """
        if self.finished_at and self.run_at:
            return (self.finished_at - self.run_at).total_seconds()
        elif self.run_at and self.finished_at is None:
            return (datetime.now() - self.run_at).total_seconds()
        return None

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def jobs(self) -> List[Job]:
        """The list of jobs created by the submission."""
        from ..job._job_manager_factory import _JobManagerFactory

        job_manager = _JobManagerFactory._build_manager()
        return [job_manager._get(job) for job in self._jobs]

    @jobs.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def jobs(self, jobs: Union[List[Job], List[JobId]]) -> None:
        self._jobs = jobs

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def submission_status(self) -> SubmissionStatus:
        """The status of the submission."""
        return self._submission_status

    @submission_status.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def submission_status(self, submission_status) -> None:
        self._submission_status = submission_status

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_abandoned(self) -> bool:
        """Indicate if the submission is abandoned."""
        return self._is_abandoned

    @is_abandoned.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def is_abandoned(self, val) -> None:
        self._is_abandoned = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_completed(self) -> bool:
        """Indicate if the submission is completed."""
        return self._is_completed

    @is_completed.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def is_completed(self, val) -> None:
        self._is_completed = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_canceled(self) -> bool:
        """Indicate if the submission is canceled."""
        return self._is_canceled

    @is_canceled.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def is_canceled(self, val) -> None:
        self._is_canceled = val

    @property
    def version(self) -> str:
        """The application version of the submission.

        The string indicates the application version of the submission. If not
        provided, the latest version is used."""
        return self._version

    def get_label(self) -> str:
        """Returns the submission simple label prefixed by its owner label.

        Returns:
            The label of the submission as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the submission simple label.

        Returns:
            The simple label of the submission as a string.
        """
        return self._get_simple_label()

    def is_finished(self) -> bool:
        """Indicate if the submission is finished.

        A submission is considered as finished if its submission status is
        `COMPLETED`, `FAILED`, or `CANCELED`.

        Returns:
            True if the submission is finished.
        """
        return self.submission_status in [
            SubmissionStatus.COMPLETED,
            SubmissionStatus.FAILED,
            SubmissionStatus.CANCELED,
        ]

    def is_deletable(self) -> ReasonCollection:
        """Indicate if the submission can be deleted.

        Returns:
            A ReasonCollection object that can function as a Boolean value,
                which is True if the submission can be deleted. False otherwise.
        """
        from ... import core as tp

        return tp.is_deletable(self)

    @staticmethod
    def __new_id() -> SubmissionId:
        """Generate a unique Submission identifier."""
        return SubmissionId(Submission.__SEPARATOR.join([Submission._ID_PREFIX, str(uuid.uuid4())]))


@_make_event.register(Submission)
def _make_event_for_submission(
    submission: Submission,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {
        "origin_entity_id": submission.entity_id,
        "origin_entity_type": submission.entity_type,
        "origin_entity_config_id": submission.entity_config_id,
        "creation_date": submission.creation_date,
        "version": submission._version,
        **kwargs,
    }
    return Event(
        entity_type=EventEntityType.SUBMISSION,
        entity_id=submission.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
