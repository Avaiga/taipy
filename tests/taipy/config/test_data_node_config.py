import pytest

from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.exceptions.configuration import ConfigurationIssueError


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_config = _Config()
    Config._applied_config = _Config.default_config()


def test_data_node_config_creation():
    data_node_config = Config.add_data_node("data_nodes1", "pickle")
    assert list(Config.data_nodes()) == ["default", data_node_config.name]

    data_node2_config = Config.add_data_node("data_nodes2", "pickle")
    assert list(Config.data_nodes()) == ["default", data_node_config.name, data_node2_config.name]

    data_node3_config = Config.add_data_node("data_nodes3", "csv", has_header=True, path="")
    assert list(Config.data_nodes()) == [
        "default",
        data_node_config.name,
        data_node2_config.name,
        data_node3_config.name,
    ]

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="bar")

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", scope="bar")

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="csv")

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="sql")

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="excel")


def test_data_node_count():
    Config.add_data_node("data_nodes1", "pickle")
    assert len(Config.data_nodes()) == 2

    Config.add_data_node("data_nodes2", "pickle")
    assert len(Config.data_nodes()) == 3

    Config.add_data_node("data_nodes3", "pickle")
    assert len(Config.data_nodes()) == 4


def test_data_node_getitem():
    data_node_name = "data_nodes1"
    data_node_config = Config.add_data_node(data_node_name, "pickle")

    assert Config.data_nodes()[data_node_name].name == data_node_config.name
    assert Config.data_nodes()[data_node_name].storage_type == data_node_config.storage_type
    assert Config.data_nodes()[data_node_name].scope == data_node_config.scope
    assert Config.data_nodes()[data_node_name].properties == data_node_config.properties


def test_data_node_creation_no_duplication():
    Config.add_data_node("data_nodes1", "pickle")

    assert len(Config.data_nodes()) == 2

    Config.add_data_node("data_nodes1", "pickle")
    assert len(Config.data_nodes()) == 2
