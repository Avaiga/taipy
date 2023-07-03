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


from .._repository._abstract_converter import _AbstractConverter
from .._version._utils import _migrate_entity
from ..common._utils import _load_fct
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions import NonExistingDataNode
from ..task._task_model import _TaskModel
from ..task.task import Task
from .task import TaskId


class _TaskConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, task: Task) -> _TaskModel:
        return _TaskModel(
            id=task.id,
            owner_id=task.owner_id,
            parent_ids=list(task._parent_ids),
            config_id=task.config_id,
            input_ids=cls.__to_ids(task.input.values()),
            function_name=task._function.__name__,
            function_module=task._function.__module__,
            output_ids=cls.__to_ids(task.output.values()),
            version=task._version,
            skippable=task._skippable,
            properties=task._properties.data.copy(),
        )

    @classmethod
    def _model_to_entity(cls, model: _TaskModel) -> Task:
        task = Task(
            id=TaskId(model.id),
            owner_id=model.owner_id,
            parent_ids=set(model.parent_ids),
            config_id=model.config_id,
            function=_load_fct(model.function_module, model.function_name),
            input=cls.__to_data_nodes(model.input_ids),
            output=cls.__to_data_nodes(model.output_ids),
            version=model.version,
            skippable=model.skippable,
            properties=model.properties,
        )
        return _migrate_entity(task)

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
