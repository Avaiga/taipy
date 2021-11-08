from dataclasses import dataclass
from typing import Optional

from taipy.config.interface import ConfigRepository
from taipy.config.task_scheduler import TaskSchedulerSerializer


@dataclass
class TaskSchedulerConfig:
    remote_execution: bool
    parallel_execution: bool
    nb_of_workers: Optional[int]


class TaskSchedulerConfigs(ConfigRepository):
    TASK_SCHEDULER_CONFIG_NAME = "task_scheduler_repository"

    def __init__(self, config: TaskSchedulerSerializer):
        super().__init__()
        self.__config = config

    def create(self, parallel_execution: Optional[bool] = None, remote_execution: Optional[bool] = None, nb_of_workers: Optional[int] = None) -> TaskSchedulerConfig:  # type: ignore
        task_scheduler_config = TaskSchedulerConfig(
            remote_execution=self._remote_execution(remote_execution),
            parallel_execution=self._parallel_execution(parallel_execution),
            nb_of_workers=self._nb_of_workers(nb_of_workers),
        )
        self._data[self.TASK_SCHEDULER_CONFIG_NAME] = task_scheduler_config
        return task_scheduler_config

    def _parallel_execution(self, parallel_execution: Optional[bool]) -> bool:
        if self.__config.parallel_execution is not None:
            return self.__config.parallel_execution
        if parallel_execution is not None:
            return parallel_execution
        return False

    def _remote_execution(self, remote_execution):
        if self.__config.remote_execution is not None:
            return self.__config.remote_execution
        if remote_execution is not None:
            return remote_execution
        return False

    def _nb_of_workers(self, nb_of_workers) -> Optional[int]:
        if self.__config.nb_of_workers is not None:
            return self.__config.nb_of_workers
        return nb_of_workers
