import datetime

import pytest

from taipy.common.alias import DataSourceId, JobId, TaskId
from taipy.data import CSVDataSource, Scope
from taipy.data.manager import DataManager
from taipy.exceptions import ModelNotFound
from taipy.job import Job, JobManager, Status
from taipy.job.job_model import JobModel
from taipy.task import Task
from taipy.task.manager import TaskManager

data_source = CSVDataSource(
    "test_data_source",
    Scope.PIPELINE,
    DataSourceId("ds_id"),
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

task = Task("config_name", [data_source], print, [], TaskId("task_id"), parent_id="parent_id")

job = Job(JobId("id"), task)

job_model = JobModel(
    id=JobId("id"),
    task_id=task.id,
    status=Status.SUBMITTED,
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
        DataManager().set(data_source)
        TaskManager().set(task)
        j = repository.load("id")
        assert j.id == job.id

    def test_from_and_to_model(self):
        repository = JobManager().repository
        assert repository.to_model(job) == job_model
        with pytest.raises(ModelNotFound):
            repository.from_model(job_model)
        DataManager().set(data_source)
        TaskManager().set(task)
        assert repository.from_model(job_model).id == job.id
