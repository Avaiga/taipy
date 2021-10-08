__all__ = ["ConfigurationManager"]

import logging
import os

from .data_manager_configuration import DataManagerConfiguration
from .task_scheduler_configuration import TaskSchedulerConfiguration
from .toml_serializer import TomlSerializer


class ConfigurationManager:
    ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH = "TAIPY_CONFIG_PATH"

    TASK_SCHEDULER_CONFIGURATION_NODE_NAME = "TASK"
    DATA_MANAGER_CONFIGURATION_NODE_NAME = "DATA_MANAGER"

    serializer = TomlSerializer()
    data_manager_configuration = DataManagerConfiguration()
    task_scheduler_configuration = TaskSchedulerConfiguration()

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
            cls.DATA_MANAGER_CONFIGURATION_NODE_NAME: cls.data_manager_configuration.export(),
            cls.TASK_SCHEDULER_CONFIGURATION_NODE_NAME: cls.task_scheduler_configuration.export(),
        }
        cls.serializer.write(config, filename)

    @classmethod
    def _load_from_environment(cls):
        if config_filename := os.environ.get(ConfigurationManager.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH):
            logging.info(f"Filename '{config_filename}' provided by environment variable")
            cls.__load(config_filename)

    @classmethod
    def __load(cls, filename):
        logging.info(f"Loading configuration filename '{filename}'")
        config = cls.serializer.read(filename)
        cls.data_manager_configuration.update(config.get(cls.DATA_MANAGER_CONFIGURATION_NODE_NAME, {}))
        cls.task_scheduler_configuration.update(config.get(cls.TASK_SCHEDULER_CONFIGURATION_NODE_NAME, {}))
        logging.info(f"Successful loaded configuration filename '{filename}'")


ConfigurationManager._load_from_environment()
