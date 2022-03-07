import datetime

import pytest

from taipy.core.common.alias import DataNodeId, JobId, TaskId
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_manager import DataManager
from taipy.core.data.scope import Scope
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.job.job import Job
from taipy.core.job.job_manager import JobManager
from taipy.core.job.job_model import JobModel
from taipy.core.job.status import Status
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager

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

job_model = JobModel(
    id=JobId("id"),
    task_id=task.id,
    status=Status(Status.SUBMITTED),
    force=False,
    creation_date=job.creation_date.isoformat(),
    subscribers=[],
    exceptions=[],
)


class TestJobRepository:
    def test_save_and_load(self, tmpdir):
        repository = JobManager._repository
        repository.base_path = tmpdir
        repository.save(job)
        with pytest.raises(ModelNotFound):
            repository.load("id")
        DataManager._set(data_node)
        TaskManager._set(task)
        j = repository.load("id")
        assert j.id == job.id

    def test_from_and_to_model(self):
        repository = JobManager._repository
        assert repository.to_model(job) == job_model
        with pytest.raises(ModelNotFound):
            repository.from_model(job_model)
        DataManager._set(data_node)
        TaskManager._set(task)
        assert repository.from_model(job_model).id == job.id
