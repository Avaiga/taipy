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

import pathlib

from taipy.config.config import Config

from ._task_model import _TaskModel
from .task import Task
from .._repository import _FileSystemRepository
from ..common._utils import _load_fct
from ..common.alias import TaskId
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions.exceptions import NonExistingDataNode


class _TaskRepository(_FileSystemRepository[_TaskModel, Task]):
    def __init__(self):
        super().__init__(model=_TaskModel, dir_name="tasks")

    def _to_model(self, task: Task) -> _TaskModel:
        return _TaskModel(
            id=task.id,
            parent_id=task.parent_id,
            config_id=task.config_id,
            input_ids=self.__to_ids(task.input.values()),
            function_name=task._function.__name__,
            function_module=task._function.__module__,
            output_ids=self.__to_ids(task.output.values()),
        )

    def _from_model(self, model: _TaskModel) -> Task:
        return Task(
            id=TaskId(model.id),
            parent_id=model.parent_id,
            config_id=model.config_id,
            function=_load_fct(model.function_module, model.function_name),
            input=self.__to_data_nodes(model.input_ids),
            output=self.__to_data_nodes(model.output_ids),
        )

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __to_ids(data_nodes):
        return [i.id for i in data_nodes]

    @staticmethod
    def __to_data_nodes(data_nodes_ids):
        data_nodes = []
        data_manager = _DataManagerFactory._build_manager()
        for _id in data_nodes_ids:
            if data_node := data_manager._get(_id):
                data_nodes.append(data_node)
            else:
                raise NonExistingDataNode(_id)
        return data_nodes
