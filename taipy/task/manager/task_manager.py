import itertools
import logging
from importlib import import_module
from typing import Dict, Optional

from taipy.common.alias import TaskId
from taipy.config import TaskConfig
from taipy.data.manager import DataManager
from taipy.exceptions import ModelNotFound, NonExistingTask
from taipy.task.repository import TaskRepository
from taipy.task.task import Task
from taipy.task.task_model import TaskModel


class TaskManager:
    # This represents the task database.
    tasks: Dict[(TaskId, Task)] = {}
    data_manager = DataManager()

    def __init__(self):
        self.repository = TaskRepository(dir_name="tasks_models")

    def delete_all(self):
        self.repository.delete_all()

    def get_all(self):
        return self.repository.load_all()

    def set(self, task: Task):
        logging.info(f"Task : {task.id} created or updated.")
        self.__save_data_sources(task.input.values())
        self.__save_data_sources(task.output.values())
        self.repository.save(task)

    def create(self, config: TaskConfig, scenario_id: Optional[str] = None, pipeline_id: Optional[str] = None) -> Task:
        data_sources = {
            ds_config: self.data_manager.get_or_create(ds_config, scenario_id, pipeline_id)
            for ds_config in set(itertools.chain(config.input, config.output))
        }
        inputs = [data_sources[input_config] for input_config in config.input]
        outputs = [data_sources[output_config] for output_config in config.output]
        task = Task(config.name, inputs, config.function, outputs)
        self.set(task)
        return task

    def get(self, task_id: TaskId) -> Task:
        try:
            return self.repository.load(task_id)
        except ModelNotFound:
            logging.error(f"Task : {task_id} does not exist.")
            raise NonExistingTask(task_id)

    @staticmethod
    def __save_data_sources(data_sources):
        for i in data_sources:
            DataManager().set(i)
