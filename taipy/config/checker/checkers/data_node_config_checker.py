from taipy.config._config import _Config
from taipy.config.checker.checkers.config_checker import ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.data_node_config import DataNodeConfig
from taipy.data.csv import CSVDataNode
from taipy.data.excel import ExcelDataNode
from taipy.data.scope import Scope
from taipy.data.sql import SQLDataNode


class DataNodeConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)
        self.required_properties = {
            "csv": CSVDataNode.REQUIRED_PROPERTIES,
            "sql": SQLDataNode.REQUIRED_PROPERTIES,
            "excel": ExcelDataNode.REQUIRED_PROPERTIES,
        }

    def check(self) -> IssueCollector:
        data_node_configs = self.config.data_nodes
        for data_node_config_name, data_node_config in data_node_configs.items():
            self._check_storage_type(data_node_config_name, data_node_config)
            self._check_scope(data_node_config_name, data_node_config)
            self._check_required_properties(data_node_config_name, data_node_config)
        return self.collector

    def _check_storage_type(self, data_node_config_name: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type not in ["csv", "pickle", "in_memory", "sql", "excel"]:
            self._error(
                data_node_config.STORAGE_TYPE_KEY,
                data_node_config.storage_type,
                f"{data_node_config.STORAGE_TYPE_KEY} field of DataNode {data_node_config_name} must be either csv, sql, pickle, excel or in_memory.",
            )

    def _check_scope(self, data_node_config_name: str, data_node_config: DataNodeConfig):
        if not isinstance(data_node_config.scope, Scope):
            self._error(
                data_node_config.SCOPE_KEY,
                data_node_config.scope,
                f"{data_node_config.SCOPE_KEY} field of DataNode {data_node_config_name} must be populated with a Scope value.",
            )

    def _check_required_properties(self, data_node_config_name: str, data_node_config: DataNodeConfig):
        if storage_type := data_node_config.storage_type:
            if storage_type in self.required_properties.keys():
                for required_property in self.required_properties[storage_type]:
                    if required_property not in data_node_config.properties.keys():
                        self._error(
                            "properties",
                            required_property,
                            f"properties field of DataNode {data_node_config_name} is missing the required property {required_property} for type {storage_type}",
                        )
