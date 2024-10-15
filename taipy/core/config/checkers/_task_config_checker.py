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

from typing import Dict, List, cast

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector

from ...scenario.scenario import Scenario
from ..data_node_config import DataNodeConfig
from ..task_config import TaskConfig


class _TaskConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        task_configs = cast(Dict[str, TaskConfig], self._config._sections[TaskConfig.name])
        scenario_attributes = [
            attr for attr in dir(Scenario) if not callable(getattr(Scenario, attr)) and not attr.startswith("_")
        ]

        for task_config_id, task_config in task_configs.items():
            if task_config_id != _Config.DEFAULT_KEY:
                self._check_existing_config_id(task_config)
                self._check_if_entity_property_key_used_is_predefined(task_config)
                self._check_if_config_id_is_overlapping_with_scenario_attributes(
                    task_config_id, task_config, scenario_attributes
                )
                self._check_existing_function(task_config_id, task_config)
                self._check_inputs(task_config_id, task_config)
                self._check_outputs(task_config_id, task_config)
                self._check_if_children_config_id_is_overlapping_with_properties(task_config_id, task_config)
        return self._collector

    def _check_if_children_config_id_is_overlapping_with_properties(self, task_config_id: str, task_config: TaskConfig):
        for data_node in task_config.input_configs + task_config.output_configs:
            if isinstance(data_node, DataNodeConfig) and data_node.id in task_config.properties:
                self._error(
                    DataNodeConfig._ID_KEY,
                    data_node.id,
                    f"The id of the DataNodeConfig `{data_node.id}` is overlapping with the "
                    f"property `{data_node.id}` of TaskConfig `{task_config_id}`.",
                )

    def _check_if_config_id_is_overlapping_with_scenario_attributes(
        self, task_config_id: str, task_config: TaskConfig, scenario_attributes: List[str]
    ):
        if task_config.id in scenario_attributes:
            self._error(
                task_config._ID_KEY,
                task_config.id,
                f"The id of the TaskConfig `{task_config_id}` is overlapping with the "
                f"attribute `{task_config.id}` of a Scenario entity.",
            )

    def _check_inputs(self, task_config_id: str, task_config: TaskConfig):
        self._check_children(
            TaskConfig, task_config_id, task_config._INPUT_KEY, task_config.input_configs, DataNodeConfig
        )

    def _check_outputs(self, task_config_id: str, task_config: TaskConfig):
        self._check_children(
            TaskConfig, task_config_id, task_config._OUTPUT_KEY, task_config.output_configs, DataNodeConfig
        )

    def _check_existing_function(self, task_config_id: str, task_config: TaskConfig):
        if not task_config.function:
            self._error(
                task_config._FUNCTION,
                task_config.function,
                f"{task_config._FUNCTION} field of TaskConfig `{task_config_id}` is empty.",
            )
        elif not callable(task_config.function):
            self._error(
                task_config._FUNCTION,
                task_config.function,
                f"{task_config._FUNCTION} field of TaskConfig `{task_config_id}` must be"
                f" populated with Callable value.",
            )
