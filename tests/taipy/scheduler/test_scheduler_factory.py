from importlib import util

import pytest

from taipy.config import Config, JobConfig
from taipy.scheduler.scheduler import Scheduler
from taipy.scheduler.scheduler_factory import SchedulerFactory


def test_build_scheduler():
    sc = SchedulerFactory.build_scheduler()
    assert isinstance(sc, Scheduler)


def test_airflow_scheduler():
    if not util.find_spec("taipy_airflow"):
        pytest.skip("skipping tests because Taipy[airflow] is not installed", allow_module_level=True)

    Config.set_job_config(mode=JobConfig.MODE_VALUE_AIRFLOW)
    sc = SchedulerFactory.build_scheduler()

    from taipy_airflow import Scheduler

    assert isinstance(sc, Scheduler)
