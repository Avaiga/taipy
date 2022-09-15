# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import datetime
import traceback

import pytest

from src.taipy.core.common.alias import DataNodeId, JobId, TaskId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.exceptions.exceptions import ModelNotFound
from src.taipy.core.job._job_model import _JobModel
from src.taipy.core.job._job_repository import _JobRepository
from src.taipy.core.job._job_repository_factory import _JobRepositoryFactory
from src.taipy.core.job.job import Job
from src.taipy.core.job.status import Status
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config.common.scope import Scope

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("dn_id"),
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    False,
    None,
    False,
    {"path": "/path", "has_header": True},
)

task = Task("config_id", print, [data_node], [], TaskId("task_id"), parent_id="parent_id")


def f():
    pass


class A:
    class B:
        def f(self):
            pass

    def f(self):
        pass

    @classmethod
    def g(cls):
        pass

    @staticmethod
    def h():
        pass


job = Job(JobId("id"), task, "submit_id")
job._subscribers = [f, A.f, A.g, A.h, A.B.f]
job._exceptions = [traceback.TracebackException.from_exception(Exception())]

job_model = _JobModel(
    id=JobId("id"),
    task_id=task.id,
    status=Status(Status.SUBMITTED),
    force=False,
    submit_id="submit_id",
    creation_date=job._creation_date.isoformat(),
    subscribers=_JobRepository._serialize_subscribers(job._subscribers),
    stacktrace=job._stacktrace,
)


class TestJobRepository:
    def test_save_and_load(self, tmpdir):
        repository = _JobRepositoryFactory._build_repository()
        repository.base_path = tmpdir
        repository._save(job)
        with pytest.raises(ModelNotFound):
            repository.load("id")
        _DataManager._set(data_node)
        _TaskManager._set(task)
        j = repository.load("id")
        assert j.id == job.id

    def test_from_and_to_model(self):
        repository = _JobRepositoryFactory._build_repository()
        assert repository._to_model(job) == job_model
        with pytest.raises(ModelNotFound):
            repository._from_model(job_model)
        _DataManager._set(data_node)
        _TaskManager._set(task)
        assert repository._from_model(job_model).id == job.id
