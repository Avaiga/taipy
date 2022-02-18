import pathlib

from taipy.common.alias import TaskId
from taipy.common.utils import load_fct
from taipy.config.config import Config
from taipy.data.data_manager import DataManager
from taipy.data.data_node import DataNode
from taipy.exceptions.data_node import NonExistingDataNode
from taipy.repository import FileSystemRepository
from taipy.task.task import Task
from taipy.task.task_model import TaskModel


class TaskRepository(FileSystemRepository[TaskModel, Task]):
    def __init__(self):
        super().__init__(model=TaskModel, dir_name="tasks")

    def to_model(self, task: Task) -> TaskModel:
        return TaskModel(
            id=task.id,
            parent_id=task.parent_id,
            config_name=task.config_name,
            input_ids=self.__to_ids(task.input.values()),
            function_name=task.function.__name__,
            function_module=task.function.__module__,
            output_ids=self.__to_ids(task.output.values()),
        )

    def from_model(self, model: TaskModel) -> Task:
        return Task(
            id=TaskId(model.id),
            parent_id=model.parent_id,
            config_name=model.config_name,
            function=load_fct(model.function_module, model.function_name),
            input=self.__to_data_nodes(model.input_ids),
            output=self.__to_data_nodes(model.output_ids),
        )

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config().storage_folder)  # type: ignore

    @staticmethod
    def __to_ids(data_nodes):
        return [i.id for i in data_nodes]

    @staticmethod
    def __to_data_nodes(data_nodes_ids):
        data_nodes = []
        for _id in data_nodes_ids:
            if data_node := DataManager.get(_id):
                data_nodes.append(data_node)
            else:
                raise NonExistingDataNode(_id)
        return data_nodes
