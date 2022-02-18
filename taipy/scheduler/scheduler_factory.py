from importlib import util

from taipy.config.config import Config
from taipy.exceptions.scheduler import DependencyNotInstalled
from taipy.scheduler.abstract_scheduler import AbstractScheduler
from taipy.scheduler.scheduler import Scheduler


class SchedulerFactory:
    @classmethod
    def build_scheduler(cls) -> AbstractScheduler:
        if Config.job_config().mode == Config.job_config().MODE_VALUE_AIRFLOW:
            if not util.find_spec("taipy_airflow"):
                raise DependencyNotInstalled("airflow")

            from taipy_airflow.scheduler import Scheduler as AirflowScheduler

            return AirflowScheduler()
        return Scheduler()
