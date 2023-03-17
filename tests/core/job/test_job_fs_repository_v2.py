# Copyright 2023 Avaiga Private Limited
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
from src.taipy.core.job._job_fs_repository_v2 import _JobFSRepository
from src.taipy.core.job.job import Job
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config.common.scope import Scope

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("dn_id"),
    "name",
    "owner_id",
    "task_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [dict(timestamp=datetime.datetime(1985, 10, 14, 2, 30, 0), job_id="job_id")],
    "latest",
    None,
    False,
    {"path": "/path", "has_header": True},
)

task = Task("config_id", {}, print, [data_node], [], TaskId("task_id"), owner_id="owner_id", version="latest")


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


job = Job(JobId("id"), task, "submit_id", version="latest")
job._subscribers = [f, A.f, A.g, A.h, A.B.f]
job._exceptions = [traceback.TracebackException.from_exception(Exception())]


class TestJobRepository:
    def test_save_and_load(self, tmpdir):
        repository = _JobFSRepository()
        repository.base_path = tmpdir
        repository._save(job)
        with pytest.raises(ModelNotFound):
            repository._load("id")
        _DataManager._set(data_node)
        _TaskManager._set(task)
        j = repository._load("id")
        assert j.id == job.id
