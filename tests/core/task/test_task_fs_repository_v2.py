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

import pytest

from src.taipy.core.common.alias import DataNodeId, TaskId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.exceptions.exceptions import NonExistingDataNode
from src.taipy.core.task._task_fs_repository_v2 import _TaskFSRepository
from src.taipy.core.task._task_model import _TaskModel
from src.taipy.core.task.task import Task
from taipy.config.common.scope import Scope
from taipy.config.config import Config

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("dn_id"),
    "name",
    "owner_id",
    {"task_id"},
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [dict(timestamp=datetime.datetime(1985, 10, 14, 2, 30, 0), job_id="job_id")],
    "latest",
    None,
    False,
    {"path": "/path", "has_header": True},
)

task = Task(
    "config_id",
    {},
    print,
    [data_node],
    [],
    TaskId("id"),
    owner_id="owner_id",
    parent_ids={"parent_id"},
    version="latest",
)


class TestTaskRepository:
    def test_save_and_load(self, tmpdir):
        repository = _TaskFSRepository()
        repository.base_path = tmpdir
        repository._save(task)
        with pytest.raises(NonExistingDataNode):
            repository._load("id")
        _DataManager._set(data_node)
        t = repository._load("id")
        assert t.id == task.id
        assert len(t.input) == 1
