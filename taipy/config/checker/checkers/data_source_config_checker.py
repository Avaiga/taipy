from taipy.config._config import _Config
from taipy.config.checker.checkers.config_checker import ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.data_source_config import DataSourceConfig
from taipy.data.csv import CSVDataSource
from taipy.data.excel import ExcelDataSource
from taipy.data.scope import Scope
from taipy.data.sql import SQLDataSource


class DataSourceConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)
        self.required_properties = {
            "csv": CSVDataSource.REQUIRED_PROPERTIES,
            "sql": SQLDataSource.REQUIRED_PROPERTIES,
            "excel": ExcelDataSource.REQUIRED_PROPERTIES,
        }

    def check(self) -> IssueCollector:
        data_source_configs = self.config.data_sources
        for data_source_config_name, data_source_config in data_source_configs.items():
            self._check_storage_type(data_source_config_name, data_source_config)
            self._check_scope(data_source_config_name, data_source_config)
            self._check_required_properties(data_source_config_name, data_source_config)
        return self.collector

    def _check_storage_type(self, data_source_config_name: str, data_source_config: DataSourceConfig):
        if data_source_config.storage_type not in ["csv", "pickle", "in_memory", "sql", "excel"]:
            self._error(
                data_source_config.STORAGE_TYPE_KEY,
                data_source_config.storage_type,
                f"{data_source_config.STORAGE_TYPE_KEY} field of DataSource {data_source_config_name} must be either csv, sql, pickle, excel or in_memory.",
            )

    def _check_scope(self, data_source_config_name: str, data_source_config: DataSourceConfig):
        if not isinstance(data_source_config.scope, Scope):
            self._error(
                data_source_config.SCOPE_KEY,
                data_source_config.scope,
                f"{data_source_config.SCOPE_KEY} field of DataSource {data_source_config_name} must be populated with a Scope value.",
            )

    def _check_required_properties(self, data_source_config_name: str, data_source_config: DataSourceConfig):
        if storage_type := data_source_config.storage_type:
            if storage_type in self.required_properties.keys():
                for required_property in self.required_properties[storage_type]:
                    if required_property not in data_source_config.properties.keys():
                        self._error(
                            "properties",
                            required_property,
                            f"properties field of DataSource {data_source_config_name} is missing the required property {required_property} for type {storage_type}",
                        )
