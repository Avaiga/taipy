__all__ = ["Job", "JobId"]

import collections
import logging
from concurrent.futures import Future
from datetime import datetime
from functools import partial, singledispatchmethod
from typing import Any, Callable, Iterable, List, NewType

from taipy.data.manager import DataManager
from taipy.exceptions.job import DataSourceWritingError
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
        self.__reasons: List[Exception] = []

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
    def reasons(self) -> List[Exception]:
        return self.__reasons

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

    def execute(self, executor: Callable[[partial], Future]):
        self.running()
        task_input_ids = self._get_data_source_id(self.task.input.values())
        task_output_ids = self._get_data_source_id(self.task.output.values())
        ft = executor(
            partial(
                self._call_function,
                task_input_ids,
                self.task.function,
                task_output_ids,
            )
        )
        ft.add_done_callback(self.__update_status)

    @classmethod
    def _call_function(cls, inputs, fct, outputs):
        try:
            inputs = [DataManager().get(i).get() for i in inputs]
            r = fct(*inputs)
            return cls.__write(outputs, r)
        except Exception as e:
            return [e]

    @classmethod
    def __write(cls, outputs, r):
        try:
            results = cls.__extract_results(outputs, r)
            return cls.__write_results_in_output(outputs, results)
        except Exception as e:
            return [e]

    @staticmethod
    def __extract_results(outputs: List[str], ft: Any) -> List[Any]:
        results: List[Any] = [ft] if len(outputs) == 1 else ft

        if len(results) != len(outputs):
            logging.error("Error, wrong number of result or task output")
            raise DataSourceWritingError("Error, wrong number of result or task output")

        return results

    @staticmethod
    def __write_results_in_output(outputs, results: List[Any]):
        r = []
        for res, output in zip(results, outputs):
            try:
                data_source = DataManager().get(output)
                data_source.write(res)
            except Exception as e:
                r.append(DataSourceWritingError(f"Error on writing in datasource id {output}: {e}"))
                logging.error(f"Error on writing output {e}")
        return r

    def __update_status(self, ft: Future):
        self.__reasons = ft.result()
        if self.__reasons:
            self.failed()
        else:
            self.completed()

    @staticmethod
    def _get_data_source_id(data_sources):
        return [i.id for i in data_sources]
