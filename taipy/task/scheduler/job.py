__all__ = ["Job", "JobId"]

import logging
from datetime import datetime
from functools import partial
from typing import Any, Callable, List, NewType

from taipy.data import DataSource
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
        self.creation_date = datetime.now()
        self._subscribers: List[Callable] = []
        self.__task = task
        self.__status = Status.SUBMITTED

    def __contains__(self, task: Task):
        return self.__task.id == task.id

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

    @_run_callbacks
    def blocked(self):
        self.__status = Status.BLOCKED

    @_run_callbacks
    def pending(self):
        self.__status = Status.PENDING

    @_run_callbacks
    def running(self):
        self.__status = Status.RUNNING

    @_run_callbacks
    def cancelled(self):
        self.__status = Status.CANCELLED

    @_run_callbacks
    def failed(self):
        self.__status = Status.FAILED

    @_run_callbacks
    def completed(self):
        self.__status = Status.COMPLETED

    def is_failed(self) -> bool:
        return self.__status == Status.FAILED

    def is_blocked(self) -> bool:
        return self.__status == Status.BLOCKED

    def is_cancelled(self) -> bool:
        return self.__status == Status.CANCELLED

    def is_submitted(self) -> bool:
        return self.__status == Status.SUBMITTED

    def is_completed(self) -> bool:
        return self.__status == Status.COMPLETED

    def is_running(self) -> bool:
        return self.__status == Status.RUNNING

    def is_pending(self) -> bool:
        return self.__status == Status.PENDING

    def is_finished(self) -> bool:
        return self.is_completed() or self.is_failed() or self.is_cancelled()

    def on_status_change(self, function: Callable):
        self._subscribers.append(function)

        if self.__status != Status.SUBMITTED:
            function(self)

    def to_execute(self) -> partial:
        self.running()
        return partial(self.__task.function, *[i.get() for i in self.__task.input.values()])

    def write(self, result: Any):
        results = [result] if len(self.__task.output) == 1 else result
        if self._write(results, self.__task.output):
            self.completed()
        else:
            self.failed()

    @classmethod
    def _write(cls, results, outputs) -> bool:
        if len(results) == len(outputs):
            return all([cls._write_result_in_output(res, output) for res, output in zip(results, outputs.values())])
        else:
            logging.error("Error, wrong number of result or task output")
            return False

    @staticmethod
    def _write_result_in_output(result: Any, output: DataSource):
        try:
            output.write(result)
            return True
        except Exception as e:
            logging.error(f"Error on writing output {e}")
            return False
