import datetime

import pytest

from taipy.common.alias import DataNodeId, JobId, TaskId
from taipy.data import CSVDataNode, Scope
from taipy.data.manager import DataManager
from taipy.exceptions import ModelNotFound
from taipy.exceptions.data_node import NonExistingDataNode
from taipy.task import Task
from taipy.task.manager import TaskManager
from taipy.task.task_model import TaskModel

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("ds_id"),
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    None,
    None,
    None,
    False,
    {"path": "/path", "has_header": True},
)

task = Task("config_name", [data_node], print, [], TaskId("id"), parent_id="parent_id")

task_model = TaskModel(
    id="id",
    parent_id="parent_id",
    config_name="config_name",
    input_ids=["ds_id"],
    function_name=print.__name__,
    function_module=print.__module__,
    output_ids=[],
)


class TestTaskRepository:
    def test_save_and_load(self, tmpdir):
        repository = TaskManager().repository
        repository.base_path = tmpdir
        repository.save(task)
        with pytest.raises(NonExistingDataNode):
            repository.load("id")
        DataManager().set(data_node)
        t = repository.load("id")
        assert t.id == task.id

    def test_from_and_to_model(self):
        repository = TaskManager().repository
        assert repository.to_model(task) == task_model
        with pytest.raises(NonExistingDataNode):
            repository.from_model(task_model)
        DataManager().set(data_node)
        assert repository.from_model(task_model).id == task.id
