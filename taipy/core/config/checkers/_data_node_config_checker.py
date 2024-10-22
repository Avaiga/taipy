# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import timedelta
from typing import Dict, List, cast

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector
from taipy.common.config.common.scope import Scope

from ...scenario.scenario import Scenario
from ...task.task import Task
from ..data_node_config import DataNodeConfig


class _DataNodeConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        data_node_configs: Dict[str, DataNodeConfig] = cast(
            Dict[str, DataNodeConfig],
            self._config._sections[DataNodeConfig.name],
        )
        task_attributes = [attr for attr in dir(Task) if not callable(getattr(Task, attr)) and not attr.startswith("_")]
        scenario_attributes = [
            attr for attr in dir(Scenario) if not callable(getattr(Scenario, attr)) and not attr.startswith("_")
        ]

        for data_node_config_id, data_node_config in data_node_configs.items():
            self._check_existing_config_id(data_node_config)
            self._check_if_entity_property_key_used_is_predefined(data_node_config)
            self._check_if_config_id_is_overlapping_with_task_and_scenario_attributes(
                data_node_config_id, data_node_config, task_attributes, scenario_attributes
            )
            self._check_storage_type(data_node_config_id, data_node_config)
            self._check_scope(data_node_config_id, data_node_config)
            self._check_validity_period(data_node_config_id, data_node_config)
            self._check_required_properties(data_node_config_id, data_node_config)
            self._check_callable(data_node_config_id, data_node_config)
            self._check_generic_read_write_fct_and_args(data_node_config_id, data_node_config)
            self._check_exposed_type(data_node_config_id, data_node_config)
        return self._collector

    def _check_if_config_id_is_overlapping_with_task_and_scenario_attributes(
        self,
        data_node_config_id: str,
        data_node_config: DataNodeConfig,
        task_attributes: List[str],
        scenario_attributes: List[str],
    ):
        if data_node_config.id in task_attributes:
            self._error(
                data_node_config._ID_KEY,
                data_node_config.id,
                f"The id of the DataNodeConfig `{data_node_config_id}` is overlapping with the "
                f"attribute `{data_node_config.id}` of a Task entity.",
            )
        elif data_node_config.id in scenario_attributes:
            self._error(
                data_node_config._ID_KEY,
                data_node_config.id,
                f"The id of the DataNodeConfig `{data_node_config_id}` is overlapping with the "
                f"attribute `{data_node_config.id}` of a Scenario entity.",
            )

    def _check_storage_type(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type not in DataNodeConfig._ALL_STORAGE_TYPES:
            self._error(
                data_node_config._STORAGE_TYPE_KEY,
                data_node_config.storage_type,
                f"`{data_node_config._STORAGE_TYPE_KEY}` field of DataNodeConfig `{data_node_config_id}` must be"
                f" either csv, sql_table, sql, mongo_collection, pickle, excel, generic, json, parquet, s3_object,"
                f" or in_memory.",
            )

    def _check_scope(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if not isinstance(data_node_config.scope, Scope):
            self._error(
                data_node_config._SCOPE_KEY,
                data_node_config.scope,
                f"`{data_node_config._SCOPE_KEY}` field of DataNodeConfig `{data_node_config_id}` must be"
                f" populated with a Scope value.",
            )

    def _check_validity_period(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.validity_period and not isinstance(data_node_config.validity_period, timedelta):
            self._error(
                data_node_config._VALIDITY_PERIOD_KEY,
                data_node_config.validity_period,
                f"`{data_node_config._VALIDITY_PERIOD_KEY}` field of DataNodeConfig `{data_node_config_id}` must be"
                f" None or populated with a timedelta value.",
            )

    def _check_required_properties(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        storage_type = data_node_config.storage_type
        if not storage_type or storage_type not in DataNodeConfig._REQUIRED_PROPERTIES:
            return

        required_properties = DataNodeConfig._REQUIRED_PROPERTIES[storage_type]
        if storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_SQL:
            if data_node_config.properties:
                if engine := data_node_config.properties.get(DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY):
                    if engine == DataNodeConfig._DB_ENGINE_SQLITE:
                        required_properties = [
                            DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_READ_QUERY_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_WRITE_QUERY_BUILDER_SQL_PROPERTY,
                        ]
                    else:
                        required_properties = [
                            DataNodeConfig._OPTIONAL_DB_USERNAME_SQL_PROPERTY,
                            DataNodeConfig._OPTIONAL_DB_PASSWORD_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_READ_QUERY_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_WRITE_QUERY_BUILDER_SQL_PROPERTY,
                        ]
        if storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_SQL_TABLE:
            if data_node_config.properties:
                if engine := data_node_config.properties.get(DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY):
                    if engine == DataNodeConfig._DB_ENGINE_SQLITE:
                        required_properties = [
                            DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_TABLE_NAME_SQL_TABLE_PROPERTY,
                        ]
                    else:
                        required_properties = [
                            DataNodeConfig._OPTIONAL_DB_USERNAME_SQL_PROPERTY,
                            DataNodeConfig._OPTIONAL_DB_PASSWORD_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_NAME_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_DB_ENGINE_SQL_PROPERTY,
                            DataNodeConfig._REQUIRED_TABLE_NAME_SQL_TABLE_PROPERTY,
                        ]
        for required_property in required_properties:
            if not data_node_config.properties or required_property not in data_node_config.properties:
                if data_node_config_id == DataNodeConfig._DEFAULT_KEY:
                    self._warning(
                        required_property,
                        None,
                        f"DataNodeConfig `{data_node_config_id}` is missing the required "
                        f"property `{required_property}` for type `{storage_type}`.",
                    )
                else:
                    self._error(
                        required_property,
                        None,
                        f"DataNodeConfig `{data_node_config_id}` is missing the required "
                        f"property `{required_property}` for type `{storage_type}`.",
                    )

    def _check_generic_read_write_fct_and_args(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if data_node_config.storage_type != DataNodeConfig._STORAGE_TYPE_VALUE_GENERIC:
            return

        properties_to_check = [
            DataNodeConfig._OPTIONAL_READ_FUNCTION_ARGS_GENERIC_PROPERTY,
            DataNodeConfig._OPTIONAL_WRITE_FUNCTION_ARGS_GENERIC_PROPERTY,
        ]
        for prop_key in properties_to_check:
            if data_node_config.properties and prop_key in data_node_config.properties:
                prop_value = data_node_config.properties[prop_key]
                if not isinstance(prop_value, list):
                    self._error(
                        prop_key,
                        prop_value,
                        f"`{prop_key}` field of DataNodeConfig"
                        f" `{data_node_config_id}` must be populated with a List value.",
                    )
        if data_node_config_id != DataNodeConfig._DEFAULT_KEY:
            properties_to_check_at_least_one = [
                DataNodeConfig._OPTIONAL_READ_FUNCTION_GENERIC_PROPERTY,
                DataNodeConfig._OPTIONAL_WRITE_FUNCTION_GENERIC_PROPERTY,
            ]
            has_at_least_one = False
            for prop_key in properties_to_check_at_least_one:
                if data_node_config.properties and prop_key in data_node_config.properties:
                    has_at_least_one = True
            if not has_at_least_one:
                self._error(
                    ", ".join(properties_to_check_at_least_one),
                    None,
                    f"Either `{DataNodeConfig._OPTIONAL_READ_FUNCTION_GENERIC_PROPERTY}` field or "
                    f"`{DataNodeConfig._OPTIONAL_WRITE_FUNCTION_GENERIC_PROPERTY}` field of "
                    f"DataNodeConfig `{data_node_config_id}` must be populated with a Callable function.",
                )

    def _check_callable(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        properties_to_check = {
            DataNodeConfig._STORAGE_TYPE_VALUE_GENERIC: [
                DataNodeConfig._OPTIONAL_READ_FUNCTION_GENERIC_PROPERTY,
                DataNodeConfig._OPTIONAL_WRITE_FUNCTION_GENERIC_PROPERTY,
            ],
            DataNodeConfig._STORAGE_TYPE_VALUE_SQL: [
                DataNodeConfig._REQUIRED_WRITE_QUERY_BUILDER_SQL_PROPERTY,
                DataNodeConfig._OPTIONAL_APPEND_QUERY_BUILDER_SQL_PROPERTY,
            ],
        }

        if data_node_config.storage_type in properties_to_check.keys():
            for prop_key in properties_to_check[data_node_config.storage_type]:
                prop_value = data_node_config.properties.get(prop_key) if data_node_config.properties else None
                if prop_value and not callable(prop_value):
                    self._error(
                        prop_key,
                        prop_value,
                        f"`{prop_key}` of DataNodeConfig `{data_node_config_id}` must be"
                        f" populated with a Callable function.",
                    )

    def _check_exposed_type(self, data_node_config_id: str, data_node_config: DataNodeConfig):
        if not isinstance(data_node_config.exposed_type, str):
            return
        if data_node_config.exposed_type not in DataNodeConfig._ALL_EXPOSED_TYPES:
            self._error(
                data_node_config._EXPOSED_TYPE_KEY,
                data_node_config.exposed_type,
                f"The `{data_node_config._EXPOSED_TYPE_KEY}` of DataNodeConfig `{data_node_config_id}` "
                f'must be either "pandas", "numpy", or a custom type.',
            )
