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

from taipy.config._config import _Config
from taipy.config.checker._checkers._config_checker import _ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.common.frequency import Frequency

from ..data_node_config import DataNodeConfig
from ..scenario_config import ScenarioConfig
from ..task_config import TaskConfig


class _ScenarioConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        scenario_configs = self._config._sections[ScenarioConfig.name]
        for scenario_config_id, scenario_config in scenario_configs.items():
            if scenario_config_id != _Config.DEFAULT_KEY:
                self._check_if_entity_property_key_used_is_predefined(scenario_config)
                self._check_existing_config_id(scenario_config)
                self._check_frequency(scenario_config_id, scenario_config)
                self._check_task_configs(scenario_config_id, scenario_config)
                self._check_addition_data_node_configs(scenario_config_id, scenario_config)
                self._check_comparators(scenario_config_id, scenario_config)
        return self._collector

    def _check_task_configs(self, scenario_config_id: str, scenario_config: ScenarioConfig):
        self._check_children(
            ScenarioConfig,
            scenario_config_id,
            scenario_config._TASKS_KEY,
            scenario_config.tasks,
            TaskConfig,
        )

    def _check_addition_data_node_configs(self, scenario_config_id: str, scenario_config: ScenarioConfig):
        self._check_children(
            ScenarioConfig,
            scenario_config_id,
            scenario_config._ADDITIONAL_DATA_NODES_KEY,
            scenario_config.additional_data_nodes,
            DataNodeConfig,
            can_be_empty=True,
        )

    def _check_frequency(self, scenario_config_id: str, scenario_config: ScenarioConfig):
        if scenario_config.frequency and not isinstance(scenario_config.frequency, Frequency):
            self._error(
                scenario_config._FREQUENCY_KEY,
                scenario_config.frequency,
                f"{scenario_config._FREQUENCY_KEY} field of ScenarioConfig `{scenario_config_id}` must be"
                f" populated with a Frequency value.",
            )

    def _check_comparators(self, scenario_config_id: str, scenario_config: ScenarioConfig):
        if not scenario_config.comparators:
            self._info(
                scenario_config._COMPARATOR_KEY,
                scenario_config.comparators,
                f"No scenario {scenario_config._COMPARATOR_KEY} defined for ScenarioConfig `{scenario_config_id}`.",
            )
