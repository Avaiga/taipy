import copy
import os

import pytest

from taipy.config import Config
from taipy.config.data_source import DataSourceConfigs, DataSourceSerializer
from taipy.config.scenario import ScenarioConfigs
from taipy.config.task_scheduler import TaskSchedulerConfigs, TaskSchedulerSerializer


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    _env = copy.deepcopy(os.environ)
    yield
    Config._data_source_serializer = DataSourceSerializer()
    Config._task_scheduler_serializer = TaskSchedulerSerializer()
    Config.data_source_configs = DataSourceConfigs(Config._data_source_serializer)
    Config.task_scheduler_configs = TaskSchedulerConfigs(Config._task_scheduler_serializer)
    Config.scenario_configs = ScenarioConfigs()
    os.environ = _env
