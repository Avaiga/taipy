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
from taipy.config._config import _Config
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.global_app.global_app_config import GlobalAppConfig
from taipy.core.config import CoreSection
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.config.task_config import TaskConfig


def _test_default_job_config(job_config: JobConfig):
    assert job_config is not None
    assert job_config.mode == JobConfig._DEFAULT_MODE


def _test_default_core_section(core_section: CoreSection):
    assert core_section is not None
    assert core_section.mode == CoreSection._DEFAULT_MODE
    assert core_section.version_number == ""
    assert not core_section.force
    assert core_section.root_folder == "./taipy/"
    assert core_section.storage_folder == "user_data/"
    assert core_section.taipy_storage_folder == ".taipy/"
    assert core_section.repository_type == "filesystem"
    assert core_section.repository_properties == {}
    assert len(core_section.properties) == 0


def _test_default_data_node_config(dn_config: DataNodeConfig):
    assert dn_config is not None
    assert dn_config.id is not None
    assert dn_config.storage_type == "pickle"
    assert dn_config.scope == Scope.SCENARIO
    assert dn_config.validity_period is None
    assert len(dn_config.properties) == 0  # type: ignore


def _test_default_task_config(task_config: TaskConfig):
    assert task_config is not None
    assert task_config.id is not None
    assert task_config.input_configs == []
    assert task_config.output_configs == []
    assert task_config.function is None
    assert not task_config.skippable
    assert len(task_config.properties) == 0  # type: ignore


def _test_default_scenario_config(scenario_config: ScenarioConfig):
    assert scenario_config is not None
    assert scenario_config.id is not None
    assert scenario_config.tasks == []
    assert scenario_config.task_configs == []
    assert scenario_config.additional_data_nodes == []
    assert scenario_config.additional_data_node_configs == []
    assert scenario_config.data_nodes == []
    assert scenario_config.data_node_configs == []
    assert scenario_config.sequences == {}
    assert len(scenario_config.properties) == 0  # type: ignore


def _test_default_global_app_config(global_config: GlobalAppConfig):
    assert global_config is not None
    assert not global_config.notification
    assert len(global_config.properties) == 0


def test_default_configuration():
    default_config = Config._default_config
    assert default_config._global_config is not None
    _test_default_global_app_config(default_config._global_config)
    _test_default_global_app_config(Config.global_config)
    _test_default_global_app_config(GlobalAppConfig().default_config())

    assert default_config._unique_sections is not None
    assert len(default_config._unique_sections) == 2
    assert len(default_config._sections) == 3

    _test_default_job_config(default_config._unique_sections[JobConfig.name])
    _test_default_job_config(Config.job_config)
    _test_default_job_config(JobConfig().default_config())

    _test_default_core_section(default_config._unique_sections[CoreSection.name])
    _test_default_core_section(Config.core)
    _test_default_core_section(CoreSection().default_config())

    _test_default_data_node_config(default_config._sections[DataNodeConfig.name][_Config.DEFAULT_KEY])
    _test_default_data_node_config(Config.data_nodes[_Config.DEFAULT_KEY])
    _test_default_data_node_config(DataNodeConfig.default_config())
    assert len(default_config._sections[DataNodeConfig.name]) == 1
    assert len(Config.data_nodes) == 1

    _test_default_task_config(default_config._sections[TaskConfig.name][_Config.DEFAULT_KEY])
    _test_default_task_config(Config.tasks[_Config.DEFAULT_KEY])
    _test_default_task_config(TaskConfig.default_config())
    assert len(default_config._sections[TaskConfig.name]) == 1
    assert len(Config.tasks) == 1

    _test_default_scenario_config(default_config._sections[ScenarioConfig.name][_Config.DEFAULT_KEY])
    Config.scenarios[_Config.DEFAULT_KEY]
    _test_default_scenario_config(Config.scenarios[_Config.DEFAULT_KEY])
    _test_default_scenario_config(ScenarioConfig.default_config())
    assert len(default_config._sections[ScenarioConfig.name]) == 1
    assert len(Config.scenarios) == 1
