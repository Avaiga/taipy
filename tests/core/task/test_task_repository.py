import datetime

import pytest

from taipy.core.common.alias import DataNodeId, JobId, TaskId
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_manager import DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions.data_node import NonExistingDataNode
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager
from taipy.core.task.task_model import TaskModel

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("dn_id"),
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    None,
    False,
    {"path": "/path", "has_header": True},
)

task = Task("config_id", print, [data_node], [], TaskId("id"), parent_id="parent_id")

task_model = TaskModel(
    id="id",
    parent_id="parent_id",
    config_id="config_id",
    input_ids=["dn_id"],
    function_name=print.__name__,
    function_module=print.__module__,
    output_ids=[],
)


class TestTaskRepository:
    def test_save_and_load(self, tmpdir):
        repository = TaskManager._repository
        repository.base_path = tmpdir
        repository.save(task)
        with pytest.raises(NonExistingDataNode):
            repository.load("id")
        DataManager.set(data_node)
        t = repository.load("id")
        assert t.id == task.id
        assert len(t.input) == 1

    def test_from_and_to_model(self):
        repository = TaskManager._repository
        assert repository.to_model(task) == task_model
        with pytest.raises(NonExistingDataNode):
            repository.from_model(task_model)
        DataManager.set(data_node)
        t = repository.from_model(task_model)
        assert isinstance(t, Task)
        assert len(t.input) == 1
