import abc
from typing import Any

from taipy.config._config import _Config
from taipy.config.checker.issue_collector import IssueCollector


class ConfigChecker:
    def __init__(self, config: _Config, collector):
        self.collector = collector
        self.config = config

    @abc.abstractmethod
    def check(self) -> IssueCollector:
        raise NotImplementedError

    def _error(self, field: str, value: Any, message: str):
        self.collector.add_error(field, value, message, self.__class__.__name__)

    def _warning(self, field: str, value: Any, message: str):
        self.collector.add_warning(field, value, message, self.__class__.__name__)

    def _info(self, field: str, value: Any, message: str):
        self.collector.add_info(field, value, message, self.__class__.__name__)
