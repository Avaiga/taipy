from dataclasses import dataclass
from typing import Optional

from taipy.config.interface import ConfigRepository
from taipy.config.task_scheduler import TaskSchedulerSerializer


@dataclass
class TaskSchedulerConfig:
    parallel_execution: bool
    max_number_of_parallel_execution: Optional[int]


class TaskSchedulerConfigs(ConfigRepository):
    TASK_SCHEDULER_CONFIG_NAME = "task_scheduler_repository"

    def __init__(self, config: TaskSchedulerSerializer):
        super().__init__()
        self.__config = config

    def create(self, parallel_execution: Optional[bool] = None, max_number_of_parallel_execution: Optional[int] = None) -> TaskSchedulerConfig:  # type: ignore
        task_scheduler_config = TaskSchedulerConfig(
            parallel_execution=self._parallel_execution(parallel_execution),
            max_number_of_parallel_execution=self._max_number_of_parallel_execution(max_number_of_parallel_execution),
        )
        self._data[self.TASK_SCHEDULER_CONFIG_NAME] = task_scheduler_config
        return task_scheduler_config

    def _parallel_execution(self, parallel_execution: Optional[bool]) -> bool:
        if self.__config.parallel_execution is not None:
            return self.__config.parallel_execution
        if parallel_execution is not None:
            return parallel_execution
        return False

    def _max_number_of_parallel_execution(self, max_number_of_parallel_execution) -> Optional[int]:
        return self.__config.max_number_of_parallel_execution or max_number_of_parallel_execution
