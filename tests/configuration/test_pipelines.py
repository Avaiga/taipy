import pytest

from taipy.config import Config
from taipy.config.pipeline import PipelinesRepository


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config.pipeline_configs = PipelinesRepository()


def test_pipeline_creation():
    pipeline = Config.pipeline_configs.create("pipelines1", ["task1", "task2"])

    assert list(Config.pipeline_configs) == [pipeline]

    pipeline2 = Config.pipeline_configs.create("pipelines2", ["task1", "task2"])
    assert list(Config.pipeline_configs) == [pipeline, pipeline2]


def test_pipeline_count():
    Config.pipeline_configs.create("pipelines1", ["task1", "task2"])
    assert len(Config.pipeline_configs) == 1

    Config.pipeline_configs.create("pipelines2", ["task1", "task2"])
    assert len(Config.pipeline_configs) == 2

    Config.pipeline_configs.create("pipelines3", ["task1", "task2"])
    assert len(Config.pipeline_configs) == 3


def test_pipeline_getitem():
    pipeline_name = "pipelines1"
    pipeline = Config.pipeline_configs.create(pipeline_name, ["task1", "task2"])

    assert Config.pipeline_configs[pipeline_name] == pipeline


def test_pipeline_creation_no_duplication():
    Config.pipeline_configs.create("pipelines1", ["task1", "task2"])

    assert len(Config.pipeline_configs) == 1

    Config.pipeline_configs.create("pipelines1", ["task1", "task2"])
    assert len(Config.pipeline_configs) == 1
