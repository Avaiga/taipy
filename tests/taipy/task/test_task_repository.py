import datetime

import pytest

from taipy.common.alias import JobId, TaskId
from taipy.data import CSVDataSource, Scope
from taipy.data.manager import DataManager
from taipy.exceptions import ModelNotFound
from taipy.task import Task, TaskManager
from taipy.task.task_model import TaskModel

data_source = CSVDataSource(
    "test_data_source",
    Scope.PIPELINE,
    "ds_id",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    False,
    {"path": "/path", "has_header": True},
)

task = Task("config_name", [data_source], print, [], TaskId("id"))

task_model = TaskModel(
    id="id",
    config_name="config_name",
    input_ids=["ds_id"],
    function_name=print.__name__,
    function_module=print.__module__,
    output_ids=[],
)


class TestDataRepository:
    def test_save_and_load(self, tmpdir):
        repository = TaskManager().repository
        repository.base_path = tmpdir
        repository.save(task)
        with pytest.raises(ModelNotFound):
            repository.load("id")
        DataManager().set(data_source)
        t = repository.load("id")
        assert t.id == task.id

    def test_from_and_to_model(self):
        repository = TaskManager().repository
        assert repository.to_model(task) == task_model
        with pytest.raises(ModelNotFound):
            repository.from_model(task_model)
        DataManager().set(data_source)
        assert repository.from_model(task_model).id == task.id
