from abc import abstractmethod
from typing import Callable, Iterable, List, Optional

from taipy.core.job.job import Job
from taipy.core.task.task import Task


class _AbstractScheduler:
    """Creates, Enqueues and schedules Jobs."""

    @abstractmethod
    def submit(self, pipeline, callbacks: Optional[Iterable[Callable]], force: bool = False) -> List[Job]:
        return NotImplemented

    @abstractmethod
    def submit_task(self, task: Task, callbacks: Optional[Iterable[Callable]] = None, force: bool = False) -> Job:
        return NotImplemented

    @abstractmethod
    def is_running(self) -> bool:
        return NotImplemented

    @abstractmethod
    def start(self):
        return NotImplemented

    @abstractmethod
    def stop(self):
        return NotImplemented
