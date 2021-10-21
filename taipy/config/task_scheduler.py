from dataclasses import dataclass, field
from typing import Optional

from .interface import Configurable


@dataclass
class TaskScheduler(Configurable):
    parallel_execution: bool = field(default=False)
    _max_number_of_parallel_execution: int = field(default=-1)

    @property
    def max_number_of_parallel_execution(self) -> Optional[int]:
        if self._max_number_of_parallel_execution > 0:
            return self._max_number_of_parallel_execution
        return None

    def update(self, config):
        self.parallel_execution = config.get("parallel_execution", self.parallel_execution)
        self._max_number_of_parallel_execution = config.get(
            "max_number_of_parallel_execution", self._max_number_of_parallel_execution
        )

    def export(self):
        return {
            "parallel_execution": self.parallel_execution,
            "max_number_of_parallel_execution": self._max_number_of_parallel_execution,
        }
