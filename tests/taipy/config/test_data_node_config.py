import os
from datetime import datetime
from unittest import mock

import pytest

from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.data.data_manager import DataManager
from taipy.exceptions.configuration import ConfigurationIssueError


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config.default_config()


def test_data_node_config_check():
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
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", scope="bar")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="csv")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="sql")
        Config.check()

    with pytest.raises(ConfigurationIssueError):
        Config.add_data_node("data_nodes", storage_type="excel")
        Config.check()


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


def test_date_node_create_with_datetime():
    data_manager = DataManager()
    data_node_config = Config.add_data_node(
        name="datetime_data", my_property=datetime(1991, 1, 1), foo="hello", test=1, dict={"type": "Datetime", 2: "daw"}
    )
    ds = data_manager.get_or_create(data_node_config)
    ds = data_manager.get(ds)
    assert ds.foo == "hello"
    assert ds.my_property == datetime(1991, 1, 1)
    assert ds.test == 1
    assert ds.dict.get("type") == "Datetime"


def test_data_node_with_env_variable_value():
    with mock.patch.dict(os.environ, {"BAR": "baz"}):
        Config.add_data_node("data_node", prop="ENV[BAR]")
        assert Config.data_nodes()["data_node"].prop == "baz"
