import itertools
import logging
from typing import Dict, Optional

from taipy.config import DataSourceConfig, TaskConfig
from taipy.data import DataSource
from taipy.data.manager import DataManager
from taipy.exceptions import NonExistingTask
from taipy.task.task import Task
from taipy.common.alias import TaskId


class TaskManager:
    # This represents the task database.
    tasks: Dict[(TaskId, Task)] = {}
    data_manager = DataManager()

    def delete_all(self):
        self.tasks: Dict[(TaskId, Task)] = {}

    def save(self, task: Task):
        logging.info(f"Task : {task.id} created or updated.")
        self.tasks[task.id] = task

    def create(self,
               config: TaskConfig,
               scenario_id: Optional[str] = None,
               pipeline_id: Optional[str] = None) -> Task:
        data_sources = {
            ds_config: self.data_manager.get_or_create(ds_config, scenario_id, pipeline_id)
            for ds_config in set(itertools.chain(config.input, config.output))
        }
        inputs = [data_sources[input_config] for input_config in config.input]
        outputs = [data_sources[output_config] for output_config in config.output]
        task = Task(config.name, inputs, config.function, outputs)
        self.save(task)
        return task

    def get(self, task_id: TaskId) -> Task:
        try:
            return self.tasks[task_id]
        except KeyError:
            logging.error(f"Task : {task_id} does not exist.")
            raise NonExistingTask(task_id)
