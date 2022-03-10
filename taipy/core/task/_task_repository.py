import pathlib

from taipy.core._repository import _FileSystemRepository
from taipy.core.common._utils import _load_fct
from taipy.core.common.alias import TaskId
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.exceptions.exceptions import NonExistingDataNode
from taipy.core.task._task_model import _TaskModel
from taipy.core.task.task import Task


class _TaskRepository(_FileSystemRepository[_TaskModel, Task]):
    def __init__(self):
        super().__init__(model=_TaskModel, dir_name="tasks")

    def _to_model(self, task: Task) -> _TaskModel:
        return _TaskModel(
            id=task.id,
            parent_id=task._parent_id,
            config_id=task._config_id,
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
        for _id in data_nodes_ids:
            if data_node := _DataManager._get(_id):
                data_nodes.append(data_node)
            else:
                raise NonExistingDataNode(_id)
        return data_nodes
