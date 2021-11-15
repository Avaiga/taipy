from dataclasses import dataclass, field
from typing import Optional

from taipy.config.interface import ConfigRepository
from taipy.config.task_scheduler import TaskSchedulerSerializer


@dataclass
class TaskSchedulerConfig:
    remote_execution: bool
    parallel_execution: bool
    nb_of_workers: Optional[int]
    hostname: Optional[str]


class TaskSchedulerConfigs(ConfigRepository):
    TASK_SCHEDULER_CONFIG_NAME = "task_scheduler_repository"

    def __init__(self, config: TaskSchedulerSerializer):
        super().__init__()
        self.__config = config

    def create(self, parallel_execution: Optional[bool] = None, remote_execution: Optional[bool] = None, nb_of_workers: Optional[int] = None, hostname: Optional[str] = None) -> TaskSchedulerConfig:  # type: ignore
        task_scheduler_config = TaskSchedulerConfig(
            remote_execution=self._remote_execution(remote_execution),
            parallel_execution=self._parallel_execution(parallel_execution),
            nb_of_workers=self._nb_of_workers(nb_of_workers),
            hostname=self._hostname(hostname),
        )
        self._data[self.TASK_SCHEDULER_CONFIG_NAME] = task_scheduler_config
        return task_scheduler_config

    def _parallel_execution(self, parallel_execution: Optional[bool]) -> bool:
        return self.__get_compile_value(self.__config.parallel_execution, parallel_execution, False)

    def _remote_execution(self, remote_execution):
        return self.__get_compile_value(self.__config.remote_execution, remote_execution, False)

    def _nb_of_workers(self, nb_of_workers) -> Optional[int]:
        return self.__get_compile_value(self.__config.nb_of_workers, nb_of_workers)

    def _hostname(self, hostname):
        return self.__get_compile_value(self.__config.hostname, hostname)

    @staticmethod
    def __get_compile_value(config_value, override_with, default=None):
        if config_value is not None:
            return config_value
        if override_with is not None:
            return override_with
        return default
