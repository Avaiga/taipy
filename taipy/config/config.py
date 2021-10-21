__all__ = ["Config"]

import logging
import os

from .data_source import DataSourcesRepository
from .data_source_serializer import DataSourceSerializer
from .pipeline import PipelinesRepository
from .scenario import ScenariosRepository
from .task import TasksRepository
from .task_scheduler import TaskScheduler
from .toml_serializer import TomlSerializer


class Config:
    ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH = "TAIPY_CONFIG_PATH"

    TASK_SCHEDULER_CONFIGURATION_NODE_NAME = "TASK"
    DATA_SOURCE_CONFIGURATION_NODE_NAME = "DATA_SOURCE"

    _data_source_serializer = DataSourceSerializer()

    task_scheduler_configs = TaskScheduler()
    scenario_configs = ScenariosRepository()
    pipeline_configs = PipelinesRepository()
    data_source_configs = DataSourcesRepository(_data_source_serializer)
    task_configs = TasksRepository()

    __serializer = TomlSerializer()

    @classmethod
    def load(cls, filename):
        """
        Load default configuration and merge it with present configurations in filename
        """
        cls.__load(filename)
        cls._load_from_environment()

    @classmethod
    def export(cls, filename: str):
        """
        Load the current configuration and write it in the filename passed in parameter

        Note: If the file already exists, it is overwritten
        """
        config = {
            cls.DATA_SOURCE_CONFIGURATION_NODE_NAME: cls._data_source_serializer.export(),
            cls.TASK_SCHEDULER_CONFIGURATION_NODE_NAME: cls.task_scheduler_configs.export(),
        }
        cls.__serializer.write(config, filename)

    @classmethod
    def _load_from_environment(cls):
        if config_filename := os.environ.get(Config.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH):
            logging.info(f"Filename '{config_filename}' provided by environment variable")
            cls.__load(config_filename)

    @classmethod
    def __load(cls, filename):
        logging.info(f"Loading configuration filename '{filename}'")
        config = cls.__serializer.read(filename)
        cls._data_source_serializer.update(config.get(cls.DATA_SOURCE_CONFIGURATION_NODE_NAME, {}))
        cls.task_scheduler_configs.update(config.get(cls.TASK_SCHEDULER_CONFIGURATION_NODE_NAME, {}))
        logging.info(f"Successful loaded configuration filename '{filename}'")


Config._load_from_environment()
