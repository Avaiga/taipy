import pytest

from taipy.config import Config
from taipy.config.data_source import DataSourcesRepository


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config.data_source_configs = DataSourcesRepository(Config._data_source_serializer)


def test_data_source_creation():
    data_source = Config.data_source_configs.create("data_sources1", "csv")

    assert list(Config.data_source_configs) == [data_source]

    data_source2 = Config.data_source_configs.create("data_sources2", "csv")
    assert list(Config.data_source_configs) == [data_source, data_source2]


def test_data_source_count():
    Config.data_source_configs.create("data_sources1", "csv")
    assert len(Config.data_source_configs) == 1

    Config.data_source_configs.create("data_sources2", "csv")
    assert len(Config.data_source_configs) == 2

    Config.data_source_configs.create("data_sources3", "csv")
    assert len(Config.data_source_configs) == 3


def test_data_source_getitem():
    data_source_name = "data_sources1"
    data_source = Config.data_source_configs.create(data_source_name, "csv")

    assert Config.data_source_configs[data_source_name] == data_source


def test_data_source_creation_no_duplication():
    Config.data_source_configs.create("data_sources1", "csv")

    assert len(Config.data_source_configs) == 1

    Config.data_source_configs.create("data_sources1", "csv")
    assert len(Config.data_source_configs) == 1
