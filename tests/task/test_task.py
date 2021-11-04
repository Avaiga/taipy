import pytest

from taipy.config import DataSourceConfig, TaskConfig
from taipy.data import CSVDataSource, DataSource, Scope
from taipy.task import Task


@pytest.fixture
def output():
    return [DataSource("name_1"), DataSource("name_2"), DataSource("name_3")]


@pytest.fixture
def input():
    return [DataSource("input_name_1"), DataSource("input_name_2"), DataSource("input_name_3")]


def test_create_task():
    name = "name_1"
    task = Task(name, [], print, [])
    assert f"TASK_{name}_" in task.id
    assert task.config_name == "name_1"
    
    name_1 = "name_1//ξ"
    task_1 = Task(name_1, [], print, [])
    assert task_1.config_name == "name_1-x"


def test_can_not_change_task_output(output):
    task = Task("name_1", [], print, output=output)

    with pytest.raises(Exception):
        task.output = {}

    assert list(task.output.values()) == output
    output.append(output[0])
    assert list(task.output.values()) != output


def test_can_not_change_task_input(input):
    task = Task("name_1", input, print)

    with pytest.raises(Exception):
        task.input = {}

    assert list(task.input.values()) == input
    input.append(input[0])
    assert list(task.input.values()) != input


def test_can_not_change_task_config_output(output):
    task_config = TaskConfig("name_1", [], print, output=output)

    assert task_config.output == output
    with pytest.raises(Exception):
        task_config.output = []

    output.append(output[0])
    assert task_config.output != output


def test_can_not_update_task_output_values(output):
    data_source = DataSource("data_source")
    task = TaskConfig("name_1", [], print, output=output)

    task.output.append(data_source)
    assert task.output == output

    task.output[0] = data_source
    assert task.output[0] != data_source


def test_can_not_update_task_input_values(input):
    data_source = DataSource("data_source")
    task = TaskConfig("name_1", input, print, [])

    task.input.append(data_source)
    assert task.input == input

    task.input[0] = data_source
    assert task.input[0] != data_source


def test_create_task_from_task_config():
    path = "my/csv/path"
    foo_ds = CSVDataSource.create("foo", Scope.PIPELINE, None, path=path)
    task = Task("namE 1", [foo_ds], print, [])
    assert task.config_name == "name_1"
    assert task.id is not None
    assert task.foo == foo_ds
    assert task.foo.path == path
    with pytest.raises(AttributeError):
        task.bar
