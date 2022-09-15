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

import pytest

from src.taipy.core.common.alias import DataNodeId, JobId, TaskId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.csv import CSVDataNode
from src.taipy.core.exceptions.exceptions import NonExistingDataNode
from src.taipy.core.task._task_model import _TaskModel
from src.taipy.core.task._task_repository_factory import _TaskRepositoryFactory
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

task = Task("config_id", print, [data_node], [], TaskId("id"), parent_id="parent_id")

task_model = _TaskModel(
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
        repository = _TaskRepositoryFactory._build_repository()  # type: ignore
        repository.base_path = tmpdir
        repository._save(task)
        with pytest.raises(NonExistingDataNode):
            repository.load("id")
        _DataManager._set(data_node)
        t = repository.load("id")
        assert t.id == task.id
        assert len(t.input) == 1

    def test_from_and_to_model(self):
        repository = _TaskRepositoryFactory._build_repository()  # type: ignore
        assert repository._to_model(task) == task_model
        with pytest.raises(NonExistingDataNode):
            repository._from_model(task_model)
        _DataManager._set(data_node)
        t = repository._from_model(task_model)
        assert isinstance(t, Task)
        assert len(t.input) == 1
