from abc import abstractmethod
from typing import Callable, Iterable, List, Optional

from taipy.core.data._data_manager import _DataManager
from taipy.core.job.job import Job
from taipy.core.task.task import Task


class AbstractScheduler:
    """Creates and schedules Jobs.

    Attributes:
        data_manager: DataManager is an element that retrieves and deals with Data Node.

    """

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
