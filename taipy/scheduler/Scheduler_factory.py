from taipy.config import Config
from taipy.scheduler.abstract_scheduler import AbstractScheduler
from taipy.scheduler.airflow.airflow_scheduler import AirflowScheduler
from taipy.scheduler.scheduler import Scheduler


class SchedulerFactory:
    @classmethod
    def build_scheduler(cls) -> AbstractScheduler:
        if Config.job_config().mode == Config.job_config().MODE_VALUE_AIRFLOW:
            return AirflowScheduler()
        return Scheduler()
