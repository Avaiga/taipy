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

import pytest

from taipy.config import _inject_section
from taipy.config._config import _Config
from taipy.config._config_comparator._config_comparator import _ConfigComparator
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.checker._checker import _Checker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config
from taipy.core.config import CoreSection, DataNodeConfig, JobConfig, MigrationConfig, ScenarioConfig, TaskConfig


def pytest_addoption(parser):
    parser.addoption("--e2e-base-url", action="store", default="/", help="base url for e2e testing")
    parser.addoption("--e2e-port", action="store", default="5000", help="port for e2e testing")


@pytest.fixture(scope="session")
def e2e_base_url(request):
    return request.config.getoption("--e2e-base-url")


@pytest.fixture(scope="session")
def e2e_port(request):
    return request.config.getoption("--e2e-port")


@pytest.fixture
def reset_configuration_singleton():
    def _reset_configuration_singleton():
        Config.unblock_update()

        Config._default_config = _Config()._default_config()
        Config._python_config = _Config()
        Config._file_config = _Config()
        Config._env_file_config = _Config()
        Config._applied_config = _Config()
        Config._collector = IssueCollector()
        Config._serializer = _TomlSerializer()
        Config._comparator = _ConfigComparator()
        _Checker._checkers = []

    return _reset_configuration_singleton


@pytest.fixture
def inject_core_sections():
    def _inject_core_sections():
        _inject_section(
            JobConfig,
            "job_config",
            JobConfig("development"),
            [("configure_job_executions", JobConfig._configure)],
            True,
        )
        _inject_section(
            CoreSection,
            "core",
            CoreSection.default_config(),
            [("configure_core", CoreSection._configure)],
            add_to_unconflicted_sections=True,
        )
        _inject_section(
            DataNodeConfig,
            "data_nodes",
            DataNodeConfig.default_config(),
            [
                ("configure_data_node", DataNodeConfig._configure),
                ("configure_data_node_from", DataNodeConfig._configure_from),
                ("set_default_data_node_configuration", DataNodeConfig._set_default_configuration),
                ("configure_csv_data_node", DataNodeConfig._configure_csv),
                ("configure_json_data_node", DataNodeConfig._configure_json),
                ("configure_sql_table_data_node", DataNodeConfig._configure_sql_table),
                ("configure_sql_data_node", DataNodeConfig._configure_sql),
                ("configure_mongo_collection_data_node", DataNodeConfig._configure_mongo_collection),
                ("configure_in_memory_data_node", DataNodeConfig._configure_in_memory),
                ("configure_pickle_data_node", DataNodeConfig._configure_pickle),
                ("configure_excel_data_node", DataNodeConfig._configure_excel),
                ("configure_generic_data_node", DataNodeConfig._configure_generic),
                ("configure_s3_object_data_node", DataNodeConfig._configure_s3_object),
            ],
        )
        _inject_section(
            TaskConfig,
            "tasks",
            TaskConfig.default_config(),
            [
                ("configure_task", TaskConfig._configure),
                ("set_default_task_configuration", TaskConfig._set_default_configuration),
            ],
        )
        _inject_section(
            ScenarioConfig,
            "scenarios",
            ScenarioConfig.default_config(),
            [
                ("configure_scenario", ScenarioConfig._configure),
                ("set_default_scenario_configuration", ScenarioConfig._set_default_configuration),
            ],
        )
        _inject_section(
            MigrationConfig,
            "migration_functions",
            MigrationConfig.default_config(),
            [("add_migration_function", MigrationConfig._add_migration_function)],
            True,
        )

    return _inject_core_sections
