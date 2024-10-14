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

__all__ = ["Job"]

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from taipy.common.logger._taipy_logger import _TaipyLogger

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._reload import _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._utils import _fcts_to_dict
from ..notification.event import Event, EventEntityType, EventOperation, _make_event
from ..reason import ReasonCollection
from .job_id import JobId
from .status import Status

if TYPE_CHECKING:
    from ..task.task import Task


def _run_callbacks(fn):
    def __run_callbacks(job):
        fn(job)
        _TaipyLogger._get_logger().debug(f"{job.id} status has changed to {job.status}.")
        for fct in job._subscribers:
            fct(job)

    return __run_callbacks


class Job(_Entity, _Labeled):
    """Execution of a `Task^`.

    Task, Sequence, and Scenario entities can be submitted for execution. The submission
    of a scenario triggers the submission of all the contained tasks. Similarly, the submission
    of a sequence also triggers the execution of all the ordered tasks.

    Every time a task is submitted for execution, a new *Job* is created. A job represents a
    single execution of a task. It holds all the information related to the task execution,
    including the **creation date**, the execution `Status^`, the timestamp of status changes,
    and the **stacktrace** of any exception that may be raised by the user function.

    In addition, a job notifies scenario or sequence subscribers on its status change.
    """

    _MANAGER_NAME = "job"
    _ID_PREFIX = "JOB"

    id: JobId
    """The identifier of this job."""

    def __init__(self, id: JobId, task: "Task", submit_id: str, submit_entity_id: str, force=False, version=None):
        self.id = id
        self._task = task
        self._force = force
        self._status = Status.SUBMITTED
        self._creation_date = datetime.now()
        self._submit_id: str = submit_id
        self._submit_entity_id: str = submit_entity_id
        self._status_change_records: Dict[str, datetime] = {"SUBMITTED": self._creation_date}
        self._subscribers: List[Callable] = []
        self._stacktrace: List[str] = []
        self.__logger = _TaipyLogger._get_logger()
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()

    def __hash__(self) -> int:
        """Return the hash of the job id."""
        return hash(self.id)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def task(self) -> "Task":
        """The task associated to this job."""
        return self._task

    @task.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def task(self, val):
        self._task = val

    @property
    def owner_id(self) -> str:
        """The identifier of the task of this job."""
        return self.task.id

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def force(self) -> bool:
        """Enforce the job's execution whatever the output data nodes are in cache or not."""
        return self._force

    @force.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def force(self, val):
        self._force = val

    @property
    def submit_id(self) -> str:
        """The identifier of the submission that triggered the job creation."""
        return self._submit_id

    @property
    def submit_entity_id(self) -> str:
        """The identifier of the submitted entity that triggered the job creation."""
        return self._submit_entity_id

    @property  # type: ignore
    def submit_entity(self):
        """The submitted entity that triggered the job creation."""
        from ..taipy import get as tp_get

        return tp_get(self._submit_entity_id)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def status(self) -> Status:
        """The current status of this job."""
        return self._status

    @status.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def status(self, val):
        self._status_change_records[val.name] = datetime.now()
        self._status = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def creation_date(self) -> datetime:
        """The date time when the job was created."""
        return self._creation_date

    @creation_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property
    @_self_reload(_MANAGER_NAME)
    def submitted_at(self) -> datetime:
        """The date time when the job was submitted."""
        return self._status_change_records["SUBMITTED"]

    @property
    @_self_reload(_MANAGER_NAME)
    def run_at(self) -> Optional[datetime]:
        """The date time when the job was run.

        If the job has not been run, the run_at time is None.
        """
        return self._status_change_records.get(Status.RUNNING.name, None)

    @property
    @_self_reload(_MANAGER_NAME)
    def finished_at(self) -> Optional[datetime]:
        """The date time when the job was finished.

        If the job is not finished, the finished_at time is None.
        """
        if self.is_finished():
            if self.is_completed():
                return self._status_change_records[Status.COMPLETED.name]
            elif self.is_failed():
                return self._status_change_records[Status.FAILED.name]
            elif self.is_canceled():
                return self._status_change_records[Status.CANCELED.name]
            elif self.is_skipped():
                return self._status_change_records[Status.SKIPPED.name]
            elif self.is_abandoned():
                return self._status_change_records[Status.ABANDONED.name]

        return None

    @property
    @_self_reload(_MANAGER_NAME)
    def execution_duration(self) -> Optional[float]:
        """The duration of the job execution in seconds.

        The execution duration is the duration in seconds from the job running time to the
        job completion time. If the job was not run, the execution duration is None. If the
        job is not finished yet, the execution duration is the duration from the running time
        to the current time.
        """
        if Status.RUNNING.name not in self._status_change_records:
            return None

        if self.is_finished():
            return (self.finished_at - self._status_change_records[Status.RUNNING.name]).total_seconds()

        return (datetime.now() - self._status_change_records[Status.RUNNING.name]).total_seconds()

    @property
    @_self_reload(_MANAGER_NAME)
    def pending_duration(self) -> Optional[float]:
        """The duration of the job in seconds spent in the pending status.

        If the job has never been pending, the pending_duration is None. If the
        job is currently pending, the pending duration is the duration from the submission to the current time.
        """
        if Status.PENDING.name not in self._status_change_records:
            return None

        if self.is_finished() or self.is_running():
            return (
                self._status_change_records[Status.RUNNING.name] - self._status_change_records[Status.PENDING.name]
            ).total_seconds()

        return (datetime.now() - self._status_change_records[Status.PENDING.name]).total_seconds()

    @property
    @_self_reload(_MANAGER_NAME)
    def blocked_duration(self) -> Optional[float]:
        """The duration of the job in seconds spent in the blocked status.

        The duration of the job in seconds spent in the blocked status. If the job has
        never been blocked, None is returned. If the job is currently blocked, the blocked
        duration is the duration from the submission to the current time.
        """
        if Status.BLOCKED.name not in self._status_change_records:
            return None

        if Status.PENDING.name in self._status_change_records:
            return (
                self._status_change_records[Status.PENDING.name] - self._status_change_records[Status.BLOCKED.name]
            ).total_seconds()
        if self.is_finished():
            return (self.finished_at - self._status_change_records[Status.BLOCKED.name]).total_seconds()

        # If pending time is not recorded, and the job is not finished, the only possible status left is blocked
        # which means the current status is blocked.
        return (datetime.now() - self._status_change_records[Status.BLOCKED.name]).total_seconds()

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def stacktrace(self) -> List[str]:
        """The list of stacktraces of the exceptions raised during the execution."""
        return self._stacktrace

    @stacktrace.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def stacktrace(self, val):
        self._stacktrace = val

    @property
    def version(self) -> str:
        """The application version of the job.

        If not provided, the latest version is used.
        """
        return self._version

    def __contains__(self, task: "Task") -> bool:
        """Check if the job contains the task."""
        return self.task.id == task.id

    def __lt__(self, other) -> bool:
        """Compare the creation date of the job with another job."""
        return self.creation_date.timestamp() < other.creation_date.timestamp()

    def __le__(self, other) -> bool:
        """Compare the creation date of the job with another job."""
        return self.creation_date.timestamp() <= other.creation_date.timestamp()

    def __gt__(self, other) -> bool:
        """Compare the creation date of the job with another job."""
        return self.creation_date.timestamp() > other.creation_date.timestamp()

    def __ge__(self, other) -> bool:
        """Compare the creation date of the job with another job."""
        return self.creation_date.timestamp() >= other.creation_date.timestamp()

    def __eq__(self, other) -> bool:
        """Check if the job is equal to another job."""
        return isinstance(other, Job) and self.id == other.id

    @_run_callbacks
    def blocked(self) -> None:
        """Set the status to _blocked_ and notify subscribers."""
        self.status = Status.BLOCKED

    @_run_callbacks
    def pending(self) -> None:
        """Set the status to _pending_ and notify subscribers."""
        self.status = Status.PENDING

    @_run_callbacks
    def running(self) -> None:
        """Set the status to _running_ and notify subscribers."""
        self.status = Status.RUNNING

    @_run_callbacks
    def canceled(self) -> None:
        """Set the status to _canceled_ and notify subscribers."""
        self.status = Status.CANCELED

    @_run_callbacks
    def abandoned(self) -> None:
        """Set the status to _abandoned_ and notify subscribers."""
        self.status = Status.ABANDONED

    @_run_callbacks
    def failed(self) -> None:
        """Set the status to _failed_ and notify subscribers."""
        self.status = Status.FAILED

    @_run_callbacks
    def completed(self) -> None:
        """Set the status to _completed_ and notify subscribers."""
        self.status = Status.COMPLETED
        self.__logger.info(f"job {self.id} is completed.")

    @_run_callbacks
    def skipped(self) -> None:
        """Set the status to _skipped_ and notify subscribers."""
        self.status = Status.SKIPPED

    def is_failed(self) -> bool:
        """Indicate if the job has failed.

        Returns:
            True if the job has failed.
        """
        return self.status == Status.FAILED

    def is_blocked(self) -> bool:
        """Indicate if the job is blocked.

        Returns:
            True if the job is blocked.
        """
        return self.status == Status.BLOCKED

    def is_canceled(self) -> bool:
        """Indicate if the job was canceled.

        Returns:
            True if the job was canceled.
        """
        return self.status == Status.CANCELED

    def is_abandoned(self) -> bool:
        """Indicate if the job was abandoned.

        Returns:
            True if the job was abandoned.
        """
        return self.status == Status.ABANDONED

    def is_submitted(self) -> bool:
        """Indicate if the job is submitted.

        Returns:
            True if the job is submitted.
        """
        return self.status == Status.SUBMITTED

    def is_completed(self) -> bool:
        """Indicate if the job has completed.

        Returns:
            True if the job has completed.
        """
        return self.status == Status.COMPLETED

    def is_skipped(self) -> bool:
        """Indicate if the job was skipped.

        Returns:
            True if the job was skipped.
        """
        return self.status == Status.SKIPPED

    def is_running(self) -> bool:
        """Indicate if the job is running.

        Returns:
            True if the job is running.
        """
        return self.status == Status.RUNNING

    def is_pending(self) -> bool:
        """Indicate if the job is pending.

        Returns:
            True if the job is pending.
        """
        return self.status == Status.PENDING

    def is_finished(self) -> bool:
        """Indicate if the job is finished.

        A job is considered finished if it is completed, failed, canceled, skipped, or abandoned.

        Returns:
            True if the job is finished.
        """
        return self.is_completed() or self.is_failed() or self.is_canceled() or self.is_skipped() or self.is_abandoned()

    def _is_finished(self) -> bool:
        """Indicate if the job is finished.

        This function will not trigger the persistence feature unlike is_finished().

        Returns:
            True if the job is finished.
        """
        return self._status in [Status.COMPLETED, Status.FAILED, Status.CANCELED, Status.SKIPPED, Status.ABANDONED]

    def _on_status_change(self, *functions) -> None:
        """Get a notification when the status of the job changes.

        Job are assigned different statuses (_submitted_, _pending_, etc.) before being finished.
        You can be triggered on each change through this function except for the _submitted_
        status.

        Parameters:
            functions: Callables that will be called on each status change.
        """
        functions = list(functions)  # type: ignore
        function = functions.pop()
        self._subscribers.append(function)

        if functions:
            self._on_status_change(*functions)

    def get_label(self) -> str:
        """Returns the job simple label prefixed by its owner label.

        Returns:
            The label of the job as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the job simple label.

        Returns:
            The simple label of the job as a string.
        """
        return self._get_simple_label()

    def is_deletable(self) -> ReasonCollection:
        """Indicate if the job can be deleted.

        Returns:
            A ReasonCollection object that can function as a Boolean value,
                which is True if the job can be deleted. False otherwise.
        """
        from ... import core as tp

        return tp.is_deletable(self)

    def get_event_context(self):
        return {"task_config_id": self._task.config_id}

    def _unlock_edit_on_outputs(self) -> None:
        for dn in self.task.output.values():
            dn.unlock_edit()

    @staticmethod
    def _serialize_subscribers(subscribers: List) -> List:
        return _fcts_to_dict(subscribers)


@_make_event.register(Job)
def _make_event_for_job(
    job: Job,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {
        "creation_date": job._creation_date,
        "task_config_id": job._task.config_id,
        "version": job._version,
        **kwargs,
    }
    return Event(
        entity_type=EventEntityType.JOB,
        entity_id=job.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
