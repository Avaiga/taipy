import itertools
import logging
from typing import Dict, Optional, Iterable

from taipy.data import DataSource
from taipy.data.data_source_config import DataSourceConfig
from taipy.data.manager import DataManager
from taipy.exceptions import NonExistingTask
from taipy.exceptions.task import NonExistingTaskConfig
from taipy.task.task import Task, TaskId
from taipy.task.task_config import TaskConfig


class TaskManager:
    # This represents the task database.
    tasks: Dict[(TaskId, Task)] = {}
    __TASK_CONFIGS: Dict[(str, TaskConfig)] = {}
    data_manager = DataManager()

    def delete_all(self):
        self.tasks: Dict[(TaskId, Task)] = {}
        self.__TASK_CONFIGS: Dict[(str, TaskConfig)] = {}

    def register(self, task_config: TaskConfig):
        [self.data_manager.register(data_source_config) for data_source_config in task_config.input]
        [self.data_manager.register(data_source_config) for data_source_config in task_config.output]
        self.__TASK_CONFIGS[task_config.name] = task_config

    def get_task_config(self, name: str) -> TaskConfig:
        try:
            return self.__TASK_CONFIGS[name]
        except KeyError:
            logging.error(f"Task config : {name} does not exist.")
            raise NonExistingTaskConfig(name)

    def get_task_configs(self) -> Iterable[TaskConfig]:
        return self.__TASK_CONFIGS.values()

    def save(self, task: Task):
        logging.info(f"Task : {task.id} created or updated.")
        self.tasks[task.id] = task

    def create(
        self, task_config: TaskConfig, data_sources: Optional[Dict[DataSourceConfig, DataSource]] = None
    ) -> Task:
        if data_sources is None:
            data_sources = {
                ds_config: self.data_manager.get_or_create(ds_config) for ds_config in set(itertools.chain(task_config.input, task_config.output))
            }
        inputs = [data_sources[input_config] for input_config in task_config.input]
        outputs = [data_sources[output_config] for output_config in task_config.output]
        task = Task(task_config.name, inputs, task_config.function, outputs)
        self.save(task)
        return task

    def get_task(self, task_id: TaskId) -> Task:
        try:
            return self.tasks[task_id]
        except KeyError:
            logging.error(f"Task : {task_id} does not exist.")
            raise NonExistingTask(task_id)
