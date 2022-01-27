import pathlib

from taipy.common.alias import TaskId
from taipy.common.utils import load_fct
from taipy.config import Config
from taipy.data.manager import DataManager
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
            input=self.__to_data_node(model.input_ids),
            function=load_fct(model.function_module, model.function_name),
            output=self.__to_data_node(model.output_ids),
        )

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config().storage_folder)  # type: ignore

    @staticmethod
    def __to_ids(data_nodes):
        return [i.id for i in data_nodes]

    @staticmethod
    def __to_data_node(data_nodes_ids):
        return [DataManager().get(i) for i in data_nodes_ids]
