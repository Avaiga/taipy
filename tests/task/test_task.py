import pytest

from taipy.data import Scope
from taipy.data.entity import CSVDataSourceEntity
from taipy.task import TaskEntity, Task


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


def test_create_task():
    task = Task("namE 1 ", [], print, [])
    assert task.name == "name_1"
