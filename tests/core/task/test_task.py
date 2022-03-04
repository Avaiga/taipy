import pytest

from taipy.core.config.config import Config
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node import DataNode
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
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

    name_1 = "name_1//ξ"
    task_1 = Task(name_1, print, [], [])
    assert task_1.config_id == "name_1-x"

    path = "my/csv/path"
    foo_dn = CSVDataNode("foo", Scope.PIPELINE, properties={"path": path, "has_header": True})
    task = Task("namE 1", print, [foo_dn], [])
    assert task.config_id == "name_1"
    assert task.id is not None
    assert task.parent_id is None
    assert task.foo == foo_dn
    assert task.foo.path == path
    with pytest.raises(AttributeError):
        task.bar

    path = "my/csv/path"
    abc_dn = InMemoryDataNode("abc_dsξyₓéà", Scope.SCENARIO, properties={"path": path})
    task = Task("namE 1éà", print, [abc_dn], [], parent_id="parent_id")
    assert task.config_id == "name_1ea"
    assert task.id is not None
    assert task.parent_id == "parent_id"
    assert task.abc_dsxyxea == abc_dn
    assert task.abc_dsxyxea.path == path
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
    task_config = Config.add_task("name_1", print, [], output=output_config)

    assert task_config.output == output_config
    with pytest.raises(Exception):
        task_config.output = []

    output_config.append(output_config[0])
    assert task_config.output != output_config


def test_can_not_update_task_output_values(output_config):
    data_node = DataNode("data_node")
    task_config = Config.add_task("name_1", print, [], output=output_config)

    task_config.output.append(data_node)
    assert task_config.output == output_config

    task_config.output[0] = data_node
    assert task_config.output[0] != data_node


def test_can_not_update_task_input_values(input_config):
    data_node_config = DataNodeConfig("data_node")
    task_config = Config.add_task("name_1", print, input_config, [])

    task_config.input.append(data_node_config)
    assert task_config.input == input_config

    task_config.input[0] = data_node_config
    assert task_config.input[0] != data_node_config
