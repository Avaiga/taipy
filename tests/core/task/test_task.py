import pytest

from taipy.core.config.config import Config
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node import DataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.exceptions import InvalidConfigurationId
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task


@pytest.fixture
def output():
    return [DataNode("name_1"), DataNode("name_2"), DataNode("name_3")]


@pytest.fixture
def output_config():
    return [DataNodeConfig("name_1"), DataNodeConfig("name_2"), DataNodeConfig("name_3")]


@pytest.fixture
def input():
    return [DataNode("input_name_1"), DataNode("input_name_2"), DataNode("input_name_3")]


@pytest.fixture
def input_config():
    return [DataNodeConfig("input_name_1"), DataNodeConfig("input_name_2"), DataNodeConfig("input_name_3")]


def test_create_task():
    name = "name_1"
    task = Task(name, print, [], [])
    assert f"TASK_{name}_" in task.id
    assert task.config_id == "name_1"

    with pytest.raises(InvalidConfigurationId):
        Task("foo bar", print, [], [])

    path = "my/csv/path"
    foo_dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": path, "has_header": True})
    task = Task("name_1", print, [foo_dn], [])
    assert task.config_id == "name_1"
    assert task.id is not None
    assert task.parent_id is None
    assert task.foo == foo_dn
    assert task.foo.path == path
    with pytest.raises(AttributeError):
        task.bar

    path = "my/csv/path"
    abc_dn = InMemoryDataNode("name_1ea", Scope.SCENARIO, properties={"path": path})
    task = Task("name_1ea", print, [abc_dn], [], parent_id="parent_id")
    assert task.config_id == "name_1ea"
    assert task.id is not None
    assert task.parent_id == "parent_id"
    assert task.name_1ea == abc_dn
    assert task.name_1ea.path == path
    with pytest.raises(AttributeError):
        task.bar


def test_can_not_change_task_output(output):
    task = Task("name_1", print, output=output)

    with pytest.raises(Exception):
        task.output = {}

    assert list(task.output.values()) == output
    output.append(output[0])
    assert list(task.output.values()) != output


def test_can_not_change_task_input(input):
    task = Task("name_1", print, input=input)

    with pytest.raises(Exception):
        task.input = {}

    assert list(task.input.values()) == input
    input.append(input[0])
    assert list(task.input.values()) != input


def test_can_not_change_task_config_output(output_config):
    task_config = Config._add_task("name_1", print, [], output=output_config)

    assert task_config.output_configs == output_config
    with pytest.raises(Exception):
        task_config.output_configs = []

    output_config.append(output_config[0])
    assert task_config._output != output_config


def test_can_not_update_task_output_values(output_config):
    data_node_cfg = Config._add_data_node("data_node_cfg")
    task_config = Config._add_task("name_1", print, [], output=output_config)

    task_config.output_configs.append(data_node_cfg)
    assert task_config.output_configs == output_config

    task_config.output_configs[0] = data_node_cfg
    assert task_config.output_configs[0] != data_node_cfg


def test_can_not_update_task_input_values(input_config):
    data_node_config = DataNodeConfig("data_node")
    task_config = Config._add_task("name_1", print, input=input_config, output=[])

    task_config.input_configs.append(data_node_config)
    assert task_config.input_configs == input_config

    task_config.input_configs[0] = data_node_config
    assert task_config.input_configs[0] != data_node_config


def mock_func():
    pass


def test_auto_set_and_reload(data_node):
    task_1 = Task(config_id="foo", function=print, input=None, output=None, parent_id=None)

    _DataManager._set(data_node)
    _TaskManager._set(task_1)

    task_2 = _TaskManager._get(task_1)

    assert task_1.config_id == "foo"
    task_1.config_id = "fgh"
    assert task_1.config_id == "fgh"
    assert task_2.config_id == "fgh"

    assert task_1.function == print
    task_1.function = mock_func
    assert task_1.function == mock_func
    assert task_2.function == mock_func

    assert task_1.parent_id is None
    task_1.parent_id = "parent_id"
    assert task_1.parent_id == "parent_id"
    assert task_2.parent_id == "parent_id"

    with task_1 as task:
        assert task.config_id == "fgh"
        assert task.parent_id == "parent_id"
        assert task.function == mock_func
        assert task._is_in_context

        task.config_id = "abc"
        task.parent_id = None
        task.function = print

        assert task._config_id == "abc"
        assert task.config_id == "fgh"
        assert task.parent_id == "parent_id"
        assert task.function == mock_func
        assert task._is_in_context

    assert task_1.config_id == "abc"
    assert task_1.parent_id is None
    assert task_1.function == print
    assert not task_1._is_in_context
