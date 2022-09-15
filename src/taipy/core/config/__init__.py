# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from taipy.config.checker._checker import _Checker
from taipy.config.config import Config

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

Config._register_default(JobConfig("development"))
Config.job_config = Config.unique_sections[JobConfig.name]
_Checker.add_checker(_JobConfigChecker)
Config.configure_job_executions = JobConfig._configure

Config._register_default(DataNodeConfig.default_config())
Config.data_nodes = Config.sections[DataNodeConfig.name]
_Checker.add_checker(_DataNodeConfigChecker)
Config.configure_data_node = DataNodeConfig._configure
Config.configure_default_data_node = DataNodeConfig._configure_default
Config.configure_csv_data_node = DataNodeConfig._configure_csv
Config.configure_json_data_node = DataNodeConfig._configure_json
Config.configure_sql_table_data_node = DataNodeConfig._configure_sql_table
Config.configure_sql_data_node = DataNodeConfig._configure_sql
Config.configure_in_memory_data_node = DataNodeConfig._configure_in_memory
Config.configure_pickle_data_node = DataNodeConfig._configure_pickle
Config.configure_excel_data_node = DataNodeConfig._configure_excel
Config.configure_generic_data_node = DataNodeConfig._configure_generic

Config._register_default(TaskConfig.default_config())
Config.tasks = Config.sections[TaskConfig.name]
_Checker.add_checker(_TaskConfigChecker)
Config.configure_task = TaskConfig._configure
Config.configure_default_task = TaskConfig._configure_default

Config._register_default(PipelineConfig.default_config())
_Checker.add_checker(_PipelineConfigChecker)
Config.pipelines = Config.sections[PipelineConfig.name]
Config.configure_pipeline = PipelineConfig._configure
Config.configure_default_pipeline = PipelineConfig._configure_default

Config._register_default(ScenarioConfig.default_config())
Config.scenarios = Config.sections[ScenarioConfig.name]
_Checker.add_checker(_ScenarioConfigChecker)
Config.configure_scenario = ScenarioConfig._configure
Config.configure_default_scenario = ScenarioConfig._configure_default
Config.configure_scenario_from_tasks = ScenarioConfig._configure_from_tasks
