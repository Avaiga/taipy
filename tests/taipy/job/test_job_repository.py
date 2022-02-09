import datetime

import pytest

from taipy.common.alias import DataNodeId, JobId, TaskId
from taipy.data.csv import CSVDataNode
from taipy.data.data_manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions import ModelNotFound
from taipy.job.job import Job
from taipy.job.job_manager import JobManager
from taipy.job.job_model import JobModel
from taipy.job.status import Status
from taipy.task.task import Task
from taipy.task.task_manager import TaskManager

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

task = Task("config_name", [data_node], print, [], TaskId("task_id"), parent_id="parent_id")

job = Job(JobId("id"), task)

job_model = JobModel(
    id=JobId("id"),
    task_id=task.id,
    status=Status(Status.SUBMITTED),
    creation_date=job.creation_date.isoformat(),
    subscribers=[],
    exceptions=[],
)


class TestJobRepository:
    def test_save_and_load(self, tmpdir):
        repository = JobManager().repository
        repository.base_path = tmpdir
        repository.save(job)
        with pytest.raises(ModelNotFound):
            repository.load("id")
        DataManager().set(data_node)
        TaskManager().set(task)
        j = repository.load("id")
        assert j.id == job.id

    def test_from_and_to_model(self):
        repository = JobManager().repository
        assert repository.to_model(job) == job_model
        with pytest.raises(ModelNotFound):
            repository.from_model(job_model)
        DataManager().set(data_node)
        TaskManager().set(task)
        assert repository.from_model(job_model).id == job.id
