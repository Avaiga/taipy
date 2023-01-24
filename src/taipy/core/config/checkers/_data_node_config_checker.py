# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Dict

from taipy.config._config import _Config
from taipy.config.checker._checker import _ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.scope import Scope

from ..data_node_config import DataNodeConfig


class _DataNodeConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        data_node_configs: Dict[str, DataNodeConfig] = self._config._sections[DataNodeConfig.name]
        for data_node_config_id, data_node_config in data_node_configs.items():
            self._check_existing_config_id(data_node_config)
            self._check_storage_type(data_node_config_id, data_node_config)
            self._check_scope(data_node_config_id, data_node_config)
            self._check_required_properties(data_node_config_id, data_node_config)
            self._check_generic_read_write_fct(data_node_config_id, data_node_config)
            self._check_generic_read_write_fct_params(data_node_config_id, data_node_config)
            self._check_exposed_type(data_node_config_id, data_node_config)
        return self._collector

    def _check_storage_type(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type not in DataNodeConfig._ALL_STORAGE_TYPES:
            self._error(
                data_node_config._STORAGE_TYPE_KEY,
                data_node_config.storage_type,
                f"`{data_node_config._STORAGE_TYPE_KEY}` field of DataNode `{data_node_config_id}` must be either csv, "
                f"sql_table, sql, mongo_collection, pickle, excel, generic, json, parquet or in_memory.",
            )

    def _check_scope(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if not isinstance(data_node_config.scope, Scope):
            self._error(
                data_node_config._SCOPE_KEY,
                data_node_config.scope,
                f"`{data_node_config._SCOPE_KEY}` field of DataNode `{data_node_config_id}` must be populated with a "
                f"Scope value.",
            )

    def _check_required_properties(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if storage_type := data_node_config.storage_type:
            if storage_type in DataNodeConfig._REQUIRED_PROPERTIES:
                required_properties = DataNodeConfig._REQUIRED_PROPERTIES[storage_type]
                if storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_SQL:
                    if data_node_config.properties:
                        if engine := data_node_config.properties.get(DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY):
                            if engine == DataNodeConfig._REQUIRED_DB_ENGINE_SQLITE:
                                required_properties = [
                                    DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                                    DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                                    DataNodeConfig._REQUIRED_READ_QUERY_SQL_PROPERTY,
                                    DataNodeConfig._REQUIRED_WRITE_QUERY_BUILDER_SQL_PROPERTY,
                                ]
                if storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_SQL_TABLE:
                    if data_node_config.properties:
                        if engine := data_node_config.properties.get(DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY):
                            if engine == DataNodeConfig._REQUIRED_DB_ENGINE_SQLITE:
                                required_properties = [
                                    DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                                    DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                                    DataNodeConfig._REQUIRED_TABLE_NAME_PROPERTY,
                                ]
                for required_property in required_properties:
                    if not data_node_config.properties or required_property not in data_node_config.properties:
                        self._error(
                            "properties",
                            required_property,
                            f"`{data_node_config_id}` DataNode is missing the required "
                            f"property `{required_property}` for type `{storage_type}`",
                        )

    def _check_generic_read_write_fct_params(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_GENERIC:
            properties_to_check = [
                DataNodeConfig._OPTIONAL_READ_FUNCTION_PARAMS_GENERIC_PROPERTY,
                DataNodeConfig._OPTIONAL_WRITE_FUNCTION_PARAMS_GENERIC_PROPERTY,
            ]
            for prop_key in properties_to_check:
                if data_node_config.properties and prop_key in data_node_config.properties:
                    prop_value = data_node_config.properties[prop_key]
                    if not isinstance(prop_value, tuple):  # type: ignore
                        self._error(
                            prop_key,
                            prop_value,
                            f"`{prop_key}` field of DataNode"
                            f" `{data_node_config_id}` must be populated with a Tuple value.",
                        )

    def _check_generic_read_write_fct(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_GENERIC:
            properties_to_check = [
                DataNodeConfig._REQUIRED_READ_FUNCTION_GENERIC_PROPERTY,
                DataNodeConfig._REQUIRED_WRITE_FUNCTION_GENERIC_PROPERTY,
            ]
            for prop_key in properties_to_check:
                prop_value = data_node_config.properties.get(prop_key) if data_node_config.properties else None
                if prop_value and not callable(prop_value):
                    self._error(
                        prop_key,
                        prop_value,
                        f"`{prop_key}` of DataNode `{data_node_config_id}` must be populated with a Callable function.",
                    )

    def _check_exposed_type(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if not isinstance(data_node_config.exposed_type, str):
            return
        if data_node_config.exposed_type not in DataNodeConfig._ALL_EXPOSED_TYPES:
            self._error(
                data_node_config._EXPOSED_TYPE_KEY,
                data_node_config.exposed_type,
                f"The `{data_node_config._EXPOSED_TYPE_KEY}` of the DataNodeConfig `{data_node_config_id}` "
                f'must be either "pandas", "modin", "numpy" or a custom type.',
            )
