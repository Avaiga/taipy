import abc
from typing import Any, List

from taipy.core.config._config import _Config
from taipy.core.config.checker.issue_collector import IssueCollector


class _ConfigChecker:
    def __init__(self, config: _Config, collector):
        self._collector = collector
        self._config = config

    @abc.abstractmethod
    def _check(self) -> IssueCollector:
        raise NotImplementedError

    def _error(self, field: str, value: Any, message: str):
        self._collector._add_error(field, value, message, self.__class__.__name__)

    def _warning(self, field: str, value: Any, message: str):
        self._collector._add_warning(field, value, message, self.__class__.__name__)

    def _info(self, field: str, value: Any, message: str):
        self._collector._add_info(field, value, message, self.__class__.__name__)

    def _check_children(self, parent_config_class, config_id: str, config_key: str, config_value, child_config_class):
        if not config_value:
            self._warning(
                config_key,
                config_value,
                f"{config_key} field of {parent_config_class.__name__} {config_id} is empty.",
            )
        else:
            if not (
                isinstance(config_value, List) and all(map(lambda x: isinstance(x, child_config_class), config_value))
            ):
                self._error(
                    config_key,
                    config_value,
                    f"{config_key} field of {parent_config_class.__name__} {config_id} must be populated with a list of {child_config_class.__name__} objects.",
                )

    def _check_existing_config_id(self, config):
        if not config.id:
            self._error(
                "config_id",
                config.id,
                f"config_id of {config.__name__} {config.id} is empty.",
            )
