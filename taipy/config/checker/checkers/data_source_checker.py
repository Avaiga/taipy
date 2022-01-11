from typing import Any

from taipy.config._config import _Config
from taipy.config.checker.checkers.config_checker import ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.data_source_config import DataSourceConfig
from taipy.data.scope import Scope


class DataSourceConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        # data_source_configs = self.config.data_sources
        # for loop?
        # self._check_storage_type(data_source_configs.values[1][1])
        # self._check_scope(data_source_configs.values[1][1])
        return self.collector

    def _check_storage_type(self, data_source_config: DataSourceConfig):
        if data_source_config.storage_type not in ["csv", "pickle", "in_memory", "sql"]:
            self._error(
                "storage_type",
                data_source_config.storage_type,
                "storage_type field must be either csv, sql, pickle or in_memory.",
            )

    def _check_scope(self, data_source_config: DataSourceConfig):
        if not isinstance(data_source_config.scope, Scope):
            self._error("scope", data_source_config.scope, "scope field must be populated with a Scope value.")
