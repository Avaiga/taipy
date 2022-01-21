from taipy.config import Config, JobConfig
from taipy.scheduler.airflow.airflow_scheduler import AirflowScheduler
from taipy.scheduler.scheduler import Scheduler
from taipy.scheduler.Scheduler_factory import SchedulerFactory


def test_build_scheduler():
    sc = SchedulerFactory.build_scheduler()
    assert isinstance(sc, Scheduler)
    Config.set_job_config(mode=JobConfig.MODE_VALUE_AIRFLOW)
    sc = SchedulerFactory.build_scheduler()
    assert isinstance(sc, AirflowScheduler)
