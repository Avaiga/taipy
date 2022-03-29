import os
from unittest import mock

import pytest

from taipy.core.config._config import _Config
from taipy.core.config.config import Config


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config._default_config()


task1_config = Config.configure_task("task1", print, [], [])
task2_config = Config.configure_task("task2", print, [], [])


def test_pipeline_config_creation():
    pipeline_config = Config.configure_pipeline("pipelines1", [task1_config, task2_config])

    assert list(Config.pipelines) == ["default", pipeline_config.id]

    pipeline2_config = Config.configure_pipeline("pipelines2", [task1_config, task2_config])
    assert list(Config.pipelines) == ["default", pipeline_config.id, pipeline2_config.id]


def test_pipeline_count():
    Config.configure_pipeline("pipelines1", [task1_config, task2_config])
    assert len(Config.pipelines) == 2

    Config.configure_pipeline("pipelines2", [task1_config, task2_config])
    assert len(Config.pipelines) == 3

    Config.configure_pipeline("pipelines3", [task1_config, task2_config])
    assert len(Config.pipelines) == 4


def test_pipeline_getitem():
    pipeline_config_id = "pipelines1"
    pipeline = Config.configure_pipeline(pipeline_config_id, [task1_config, task2_config])

    assert Config.pipelines[pipeline_config_id].id == pipeline.id
    assert Config.pipelines[pipeline_config_id]._tasks == pipeline._tasks
    assert Config.pipelines[pipeline_config_id].properties == pipeline.properties


def test_pipeline_creation_no_duplication():
    Config.configure_pipeline("pipelines1", [task1_config, task2_config])

    assert len(Config.pipelines) == 2

    Config.configure_pipeline("pipelines1", [task1_config, task2_config])
    assert len(Config.pipelines) == 2


def test_pipeline_config_with_env_variable_value():
    with mock.patch.dict(os.environ, {"FOO": "bar"}):
        Config.configure_pipeline("pipeline_name", [task1_config, task2_config], prop="ENV[FOO]")
        assert Config.pipelines["pipeline_name"].prop == "bar"
