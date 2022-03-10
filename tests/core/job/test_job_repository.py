import datetime

import pytest

from taipy.core.common.alias import DataNodeId, JobId, TaskId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.exceptions import ModelNotFound
from taipy.core.job._job_manager import _JobManager
from taipy.core.job._job_model import _JobModel
from taipy.core.job.job import Job
from taipy.core.job.status import Status
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task

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

task = Task("config_id", print, [data_node], [], TaskId("task_id"), parent_id="parent_id")

job = Job(JobId("id"), task)

job_model = _JobModel(
    id=JobId("id"),
    task_id=task.id,
    status=Status(Status.SUBMITTED),
    force=False,
    creation_date=job._creation_date.isoformat(),
    subscribers=[],
    exceptions=[],
)


class TestJobRepository:
    def test_save_and_load(self, tmpdir):
        repository = _JobManager._repository
        repository.base_path = tmpdir
        repository._save(job)
        with pytest.raises(ModelNotFound):
            repository.load("id")
        _DataManager._set(data_node)
        _TaskManager._set(task)
        j = repository.load("id")
        assert j.id == job.id

    def test_from_and_to_model(self):
        repository = _JobManager._repository
        assert repository._to_model(job) == job_model
        with pytest.raises(ModelNotFound):
            repository._from_model(job_model)
        _DataManager._set(data_node)
        _TaskManager._set(task)
        assert repository._from_model(job_model).id == job.id
