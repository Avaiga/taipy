__all__ = ["ConfigurationManager"]

from .task_scheduler_configuration import TaskSchedulerConfiguration
from .toml_serializer import TomlSerializer


class ConfigurationManager:
    serializer = TomlSerializer()
    task_scheduler_configuration = TaskSchedulerConfiguration()

    @classmethod
    def load(cls, filename):
        """
        Load default configuration and merge it with present configurations in filename
        """
        cls.task_scheduler_configuration.update(cls.serializer.read(filename))

    @classmethod
    def export(cls, filename: str):
        """
        Load the current configuration and write it in the filename passed in parameter

        Note: If the file already exists, it is overwritten
        """
        cls.serializer.write(cls.task_scheduler_configuration.export(), filename)
