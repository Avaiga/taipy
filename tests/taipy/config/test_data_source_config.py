import pytest

from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.data.scope import Scope
from taipy.exceptions.configuration import ConfigurationIssueError


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_config = _Config()
    Config._applied_config = _Config.default_config()


def test_data_source_config_creation():
    data_source_config = Config.add_data_source("data_sources1", "pickle")
    assert list(Config.data_sources()) == ["default", data_source_config.name]

    data_source2_config = Config.add_data_source("data_sources2", "pickle")
    assert list(Config.data_sources()) == ["default", data_source_config.name, data_source2_config.name]

    data_source3_config = Config.add_data_source("data_sources3", "csv", has_header=True, path="")
    assert list(Config.data_sources()) == [
        "default",
        data_source_config.name,
        data_source2_config.name,
        data_source3_config.name,
    ]

    with pytest.raises(ConfigurationIssueError):
        data_source2_config = Config.add_data_source("data_sources", storage_type="bar")

    with pytest.raises(ConfigurationIssueError):
        data_source2_config = Config.add_data_source("data_sources", scope="bar")

    with pytest.raises(ConfigurationIssueError):
        data_source2_config = Config.add_data_source("data_sources", storage_type="csv")

    with pytest.raises(ConfigurationIssueError):
        data_source2_config = Config.add_data_source("data_sources", storage_type="sql")

    with pytest.raises(ConfigurationIssueError):
        data_source2_config = Config.add_data_source("data_sources", storage_type="excel")


def test_data_source_count():
    Config.add_data_source("data_sources1", "pickle")
    assert len(Config.data_sources()) == 2

    Config.add_data_source("data_sources2", "pickle")
    assert len(Config.data_sources()) == 3

    Config.add_data_source("data_sources3", "pickle")
    assert len(Config.data_sources()) == 4


def test_data_source_getitem():
    data_source_name = "data_sources1"
    data_source_config = Config.add_data_source(data_source_name, "pickle")

    assert Config.data_sources()[data_source_name].name == data_source_config.name
    assert Config.data_sources()[data_source_name].storage_type == data_source_config.storage_type
    assert Config.data_sources()[data_source_name].scope == data_source_config.scope
    assert Config.data_sources()[data_source_name].properties == data_source_config.properties


def test_data_source_creation_no_duplication():
    Config.add_data_source("data_sources1", "pickle")

    assert len(Config.data_sources()) == 2

    Config.add_data_source("data_sources1", "pickle")
    assert len(Config.data_sources()) == 2
