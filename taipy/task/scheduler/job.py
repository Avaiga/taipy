__all__ = ["Job", "JobId"]

from concurrent.futures import Future
from datetime import datetime
from typing import Callable, List, NewType

from taipy.task.scheduler.status import Status
from taipy.task.task import Task

JobId = NewType("JobId", str)


def _run_callbacks(fn):
    def __run_callbacks(self):
        fn(self)
        for fct in self._subscribers:
            fct(self)

    return __run_callbacks


class Job:
    def __init__(self, id: JobId, task: Task):
        self.id = id
        self.task = task
        self.status = Status.SUBMITTED
        self.creation_date = datetime.now()
        self._subscribers: List[Callable] = []
        self.__exceptions: List[Exception] = []

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
        return self.__exceptions

    @_run_callbacks
    def blocked(self):
        self.status = Status.BLOCKED

    @_run_callbacks
    def pending(self):
        self.status = Status.PENDING

    @_run_callbacks
    def running(self):
        self.status = Status.RUNNING

    @_run_callbacks
    def cancelled(self):
        self.status = Status.CANCELLED

    @_run_callbacks
    def failed(self):
        self.status = Status.FAILED

    @_run_callbacks
    def completed(self):
        self.status = Status.COMPLETED

    def is_failed(self) -> bool:
        return self.status == Status.FAILED

    def is_blocked(self) -> bool:
        return self.status == Status.BLOCKED

    def is_cancelled(self) -> bool:
        return self.status == Status.CANCELLED

    def is_submitted(self) -> bool:
        return self.status == Status.SUBMITTED

    def is_completed(self) -> bool:
        return self.status == Status.COMPLETED

    def is_running(self) -> bool:
        return self.status == Status.RUNNING

    def is_pending(self) -> bool:
        return self.status == Status.PENDING

    def is_finished(self) -> bool:
        return self.is_completed() or self.is_failed() or self.is_cancelled()

    def on_status_change(self, function, *functions):
        self._subscribers.append(function)

        if self.status != Status.SUBMITTED:
            function(self)

        if functions:
            self.on_status_change(*functions)

    def update_status(self, ft: Future):
        self.__exceptions = ft.result()
        if self.__exceptions:
            self.failed()
        else:
            self.completed()
