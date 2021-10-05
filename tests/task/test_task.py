import pytest

from taipy.data import DataSource, DataSourceEntity, Scope
from taipy.data.entity import CSVDataSourceEntity
from taipy.task import Task, TaskEntity


@pytest.fixture
def output():
    return [DataSourceEntity("name_1"), DataSourceEntity("name_2"), DataSourceEntity("name_3")]


@pytest.fixture
def input():
    return [DataSourceEntity("input_name_1"), DataSourceEntity("input_name_2"), DataSourceEntity("input_name_3")]


def test_create_task():
    name = "name_1"
    task = TaskEntity(name, [], print, [])
    assert f"TASK_{name}_" in task.id
    assert task.name == "name_1"


def test_can_not_change_task_entity_output(output):
    task = TaskEntity("name_1", [], print, output=output)

    with pytest.raises(Exception):
        task.output = {}

    assert list(task.output.values()) == output
    output.append(output[0])
    assert list(task.output.values()) != output


def test_can_not_change_task_entity_input(input):
    task = TaskEntity("name_1", input, print)

    with pytest.raises(Exception):
        task.input = {}

    assert list(task.input.values()) == input
    input.append(input[0])
    assert list(task.input.values()) != input


def test_can_not_change_task_output(output):
    task = Task("name_1", [], print, output=output)

    assert task.output == output
    with pytest.raises(Exception):
        task.output = []

    output.append(output[0])
    assert task.output != output


def test_can_not_update_task_output_values(output):
    data_source = DataSourceEntity("data_source")
    task = Task("name_1", [], print, output=output)

    task.output.append(data_source)
    assert task.output == output

    task.output[0] = data_source
    assert task.output[0] != data_source


def test_can_not_update_task_input_values(input):
    data_source = DataSource("data_source", "embedded")
    task = Task("name_1", input, print, data_source)

    task.input.append(data_source)
    assert task.input == input

    task.input[0] = data_source
    assert task.input[0] != data_source


def test_create_task_entity():
    path = "my/csv/path"
    foo_ds = CSVDataSourceEntity.create("foo", scope=Scope.PIPELINE, path=path)
    task = TaskEntity("namE 1", [foo_ds], print, [])
    assert task.name == "name_1"
    assert task.id is not None
    assert task.foo == foo_ds
    assert task.foo.path == path
    with pytest.raises(AttributeError):
        task.bar
