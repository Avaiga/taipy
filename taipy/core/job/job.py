__all__ = ["Job"]

import traceback
from concurrent.futures import Future
from datetime import datetime
from typing import Callable, List

from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import JobId
from taipy.core.job.status import Status
from taipy.core.task.task import Task


def _run_callbacks(fn):
    def __run_callbacks(self):
        fn(self)
        for fct in self._subscribers:
            fct(self)

    return __run_callbacks


class Job:
    """Execution of a Task.

    A Job is the execution wrapper around a Task. It handles the status of the execution,
    contains raising exceptions during the execution and notifies subscriber when the job is
    finished.

    Attributes:
        id (str): The identifier of the Job.
        task (`Task^`): The task of the job.
        force (bool): Enforce the job's execution whatever the output data nodes are in cache or not.
        status (`Status^`): The current status of the job.
        creation_date (datetime): The date of the job's creation.
        exceptions (List[Exception]): The list of exceptions raised during the execution.
    """

    def __init__(self, id: JobId, task: Task, force=False):
        self.id = id
        self.task = task
        self.force = force
        self.status = Status.SUBMITTED
        self.creation_date = datetime.now()
        self._subscribers: List[Callable] = []
        self._exceptions: List[Exception] = []
        self.__logger = _TaipyLogger._get_logger()

    def __contains__(self, task: Task):
        return self.task.id == task.id

    def __lt__(self, other):
        return self.creation_date.timestamp() < other.creation_date.timestamp()

    def __le__(self, other):
        return self.creation_date.timestamp() == other.creation_date.timestamp() or self < other

    def __gt__(self, other):
        return self.creation_date.timestamp() > other.creation_date.timestamp()

    def __ge__(self, other):
        return self.creation_date.timestamp() == other.creation_date.timestamp() or self > other

    def __eq__(self, other):
        return self.id == other.id

    @property
    def exceptions(self) -> List[Exception]:
        return self._exceptions

    @_run_callbacks
    def blocked(self):
        """Sets the status to blocked and notifies subscribers."""
        self.status = Status.BLOCKED

    @_run_callbacks
    def pending(self):
        """Sets the status to pending and notifies subscribers."""
        self.status = Status.PENDING

    @_run_callbacks
    def running(self):
        """Sets the status to running and notifies subscribers."""
        self.status = Status.RUNNING

    @_run_callbacks
    def cancelled(self):
        """Sets the status to cancelled and notifies subscribers."""
        self.status = Status.CANCELLED

    @_run_callbacks
    def failed(self):
        """Sets the status to failed and notifies subscribers."""
        self.status = Status.FAILED

    @_run_callbacks
    def completed(self):
        """Sets the status to completed and notifies subscribers."""
        self.status = Status.COMPLETED

    @_run_callbacks
    def skipped(self):
        """Sets the status to skipped and notifies subscribers."""
        self.status = Status.SKIPPED

    def is_failed(self) -> bool:
        """Returns true if the job failed.

        Returns:
            True if the job has failed.
        """
        return self.status == Status.FAILED

    def is_blocked(self) -> bool:
        """Returns true if the job is blocked.

        Returns:
            True if the job is blocked.
        """
        return self.status == Status.BLOCKED

    def is_cancelled(self) -> bool:
        """Returns true if the job is cancelled.

        Returns:
            True if the job is cancelled.
        """
        return self.status == Status.CANCELLED

    def is_submitted(self) -> bool:
        """Returns true if the job is submitted.

        Returns:
            True if the job is submitted.
        """
        return self.status == Status.SUBMITTED

    def is_completed(self) -> bool:
        """Returns true if the job is completed.

        Returns:
            True if the job is completed.
        """
        return self.status == Status.COMPLETED

    def is_skipped(self) -> bool:
        """Returns true if the job is skipped.

        Returns:
            True if the job is skipped.
        """
        return self.status == Status.SKIPPED

    def is_running(self) -> bool:
        """Returns true if the job is running.

        Returns:
            True if the job is running.
        """
        return self.status == Status.RUNNING

    def is_pending(self) -> bool:
        """Returns true if the job is pending.

        Returns:
            True if the job is pending.
        """
        return self.status == Status.PENDING

    def is_finished(self) -> bool:
        """Returns true if the job is finished.

        Returns:
            True if the job is finished.
        """
        return self.is_completed() or self.is_failed() or self.is_cancelled() or self.is_skipped()

    def on_status_change(self, *functions):
        """Allows to be notified when the status of the job changes.

        Job passing through multiple statuses (Submitted, pending, etc.) before being finished.
        You can be triggered on each change through this function unless for the `Submitted` status.

        Args:
            functions: Callables that will be called on each status change.
        """
        functions = list(functions)
        function = functions.pop()
        self._subscribers.append(function)

        if self.status != Status.SUBMITTED:
            function(self)

        if functions:
            self.on_status_change(*functions)

    def update_status(self, ft: Future):
        """Update the Job status based on its execution."""
        self._exceptions = ft.result()
        if self._exceptions:
            self.failed()
            self.__logger.error(f" {len(self._exceptions)} errors occurred during execution of job {self.id}")
            for e in self.exceptions:
                self.__logger.error("".join(traceback.format_exception(type(e), value=e, tb=e.__traceback__)))
        else:
            self.completed()
            self.__logger.info(f"job {self.id} is completed.")
