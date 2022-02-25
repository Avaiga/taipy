from importlib import util

from taipy.core.config.config import Config
from taipy.core.exceptions.scheduler import DependencyNotInstalled
from taipy.core.scheduler.abstract_scheduler import AbstractScheduler
from taipy.core.scheduler.scheduler import Scheduler


class SchedulerFactory:
    @classmethod
    def build_scheduler(cls) -> AbstractScheduler:
        if Config.job_config.mode == Config.job_config.MODE_VALUE_AIRFLOW:
            if not util.find_spec("taipy_airflow"):
                raise DependencyNotInstalled("airflow")

            from taipy_airflow.scheduler import Scheduler as AirflowScheduler

            return AirflowScheduler()
        return Scheduler()
