from importlib import import_module

from taipy.common.alias import TaskId
from taipy.data.manager import DataManager
from taipy.repository import FileSystemRepository
from taipy.task import Task
from taipy.task.task_model import TaskModel


class TaskRepository(FileSystemRepository[TaskModel, Task]):
    def __init__(self, dir_name="tasks"):
        super().__init__(model=TaskModel, dir_name=dir_name)

    def to_model(self, task):
        return TaskModel(
            id=task.id,
            config_name=task.config_name,
            input_ids=self.__to_ids(task.input.values()),
            function_name=task.function.__name__,
            function_module=task.function.__module__,
            output_ids=self.__to_ids(task.output.values()),
        )

    def from_model(self, model):
        return Task(
            id=TaskId(model.id),
            config_name=model.config_name,
            input=self.__to_data_source(model.input_ids),
            function=self.__load_fct(model.function_module, model.function_name),
            output=self.__to_data_source(model.output_ids),
        )

    @staticmethod
    def __to_ids(data_sources):
        return [i.id for i in data_sources]

    @staticmethod
    def __to_data_source(data_sources_ids):
        return [DataManager().get(i) for i in data_sources_ids]

    @staticmethod
    def __load_fct(module_name, fct_name):
        module = import_module(module_name)
        return getattr(module, fct_name)
