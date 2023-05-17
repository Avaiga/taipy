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

from taipy.config import _inject_section
from taipy.config.checker._checker import _Checker
from taipy.config.common.frequency import Frequency  # type: ignore
from taipy.config.common.scope import Scope  # type: ignore
from taipy.config.config import Config  # type: ignore
from taipy.config.global_app.global_app_config import GlobalAppConfig  # type: ignore

from ._core_section import CoreSection
from .checkers._config_id_checker import _ConfigIdChecker
from .checkers._data_node_config_checker import _DataNodeConfigChecker
from .checkers._job_config_checker import _JobConfigChecker
from .checkers._pipeline_config_checker import _PipelineConfigChecker
from .checkers._scenario_config_checker import _ScenarioConfigChecker
from .checkers._task_config_checker import _TaskConfigChecker
from .data_node_config import DataNodeConfig
from .job_config import JobConfig
from .pipeline_config import PipelineConfig
from .scenario_config import ScenarioConfig
from .task_config import TaskConfig

_inject_section(
    JobConfig,
    "job_config",
    JobConfig("development"),
    [("configure_job_executions", JobConfig._configure)],
    add_to_unconflicted_sections=True,
)
_inject_section(
    DataNodeConfig,
    "data_nodes",
    DataNodeConfig.default_config(),
    [
        ("configure_data_node", DataNodeConfig._configure),
        ("configure_default_data_node", DataNodeConfig._configure_default),
        ("configure_csv_data_node", DataNodeConfig._configure_csv),
        ("configure_json_data_node", DataNodeConfig._configure_json),
        ("configure_parquet_data_node", DataNodeConfig._configure_parquet),
        ("configure_sql_table_data_node", DataNodeConfig._configure_sql_table),
        ("configure_sql_data_node", DataNodeConfig._configure_sql),
        ("configure_mongo_collection_data_node", DataNodeConfig._configure_mongo_collection),
        ("configure_in_memory_data_node", DataNodeConfig._configure_in_memory),
        ("configure_pickle_data_node", DataNodeConfig._configure_pickle),
        ("configure_excel_data_node", DataNodeConfig._configure_excel),
        ("configure_generic_data_node", DataNodeConfig._configure_generic),
    ],
)
_inject_section(
    TaskConfig,
    "tasks",
    TaskConfig.default_config(),
    [("configure_task", TaskConfig._configure), ("configure_default_task", TaskConfig._configure_default)],
)
_inject_section(
    PipelineConfig,
    "pipelines",
    PipelineConfig.default_config(),
    [
        ("configure_pipeline", PipelineConfig._configure),
        ("configure_default_pipeline", PipelineConfig._configure_default),
    ],
)
_inject_section(
    ScenarioConfig,
    "scenarios",
    ScenarioConfig.default_config(),
    [
        ("configure_scenario", ScenarioConfig._configure),
        ("configure_default_scenario", ScenarioConfig._configure_default),
        ("configure_scenario_from_tasks", ScenarioConfig._configure_from_tasks),
    ],
)
_inject_section(
    CoreSection,
    "core",
    CoreSection.default_config(),
    [("configure_core", CoreSection._configure)],
    add_to_unconflicted_sections=True,
)

_Checker.add_checker(_ConfigIdChecker)
_Checker.add_checker(_JobConfigChecker)
_Checker.add_checker(_DataNodeConfigChecker)
_Checker.add_checker(_TaskConfigChecker)
_Checker.add_checker(_PipelineConfigChecker)
_Checker.add_checker(_ScenarioConfigChecker)
