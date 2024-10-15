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

from typing import Dict, cast

from taipy.common.config import Config
from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector
from taipy.common.config.common.frequency import Frequency

from ..data_node_config import DataNodeConfig
from ..scenario_config import ScenarioConfig
from ..task_config import TaskConfig


class _ScenarioConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        scenario_configs = cast(Dict[str, ScenarioConfig], self._config._sections[ScenarioConfig.name])

        for scenario_config_id, scenario_config in scenario_configs.items():
            if scenario_config_id != _Config.DEFAULT_KEY:
                self._check_if_entity_property_key_used_is_predefined(scenario_config)
                self._check_existing_config_id(scenario_config)
                self._check_frequency(scenario_config_id, scenario_config)
                self._check_task_configs(scenario_config_id, scenario_config)
                self._check_addition_data_node_configs(scenario_config_id, scenario_config)
                self._check_additional_dns_not_overlapping_tasks_dns(scenario_config_id, scenario_config)
                self._check_tasks_in_sequences_exist_in_scenario_tasks(scenario_config_id, scenario_config)
                self._check_if_children_config_id_is_overlapping_with_properties(scenario_config_id, scenario_config)
                self._check_comparators(scenario_config_id, scenario_config)

        return self._collector

    def _check_if_children_config_id_is_overlapping_with_properties(
        self, scenario_config_id: str, scenario_config: ScenarioConfig
    ):
        if scenario_config.sequences:
            for sequence in scenario_config.sequences:
                if sequence in scenario_config.properties:
                    self._error(
                        sequence,
                        scenario_config.sequences[sequence],
                        f"The sequence name `{sequence}` is overlapping with the "
                        f"property `{sequence}` of ScenarioConfig `{scenario_config_id}`.",
                    )
                if scenario_config.data_nodes:
                    if sequence in [dn.id for dn in scenario_config.data_nodes if isinstance(dn, DataNodeConfig)]:
                        self._error(
                            sequence,
                            scenario_config.sequences[sequence],
                            f"The sequence name `{sequence}` is overlapping with the "
                            f"data node `{sequence}` of ScenarioConfig `{scenario_config_id}`.",
                        )
                if scenario_config.tasks:
                    if sequence in [task.id for task in scenario_config.tasks if isinstance(task, TaskConfig)]:
                        self._error(
                            sequence,
                            scenario_config.sequences[sequence],
                            f"The sequence name `{sequence}` is overlapping with the "
                            f"task `{sequence}` of ScenarioConfig `{scenario_config_id}`.",
                        )
        if scenario_config.tasks:
            for task in scenario_config.tasks:
                if isinstance(task, TaskConfig) and task.id in scenario_config.properties:
                    self._error(
                        TaskConfig._ID_KEY,
                        task.id,
                        f"The id of the TaskConfig `{task.id}` is overlapping with the "
                        f"property `{task.id}` of ScenarioConfig `{scenario_config_id}`.",
                    )
                if scenario_config.data_nodes:
                    if isinstance(task, TaskConfig) and task.id in [
                        dn.id for dn in scenario_config.data_nodes if isinstance(dn, DataNodeConfig)
                    ]:
                        self._error(
                            TaskConfig._ID_KEY,
                            task.id,
                            f"The id of the TaskConfig `{task.id}` is overlapping with the "
                            f"data node `{task.id}` of ScenarioConfig `{scenario_config_id}`.",
                        )
        if scenario_config.data_nodes:
            for data_node in scenario_config.data_nodes:
                if isinstance(data_node, DataNodeConfig) and data_node.id in scenario_config.properties:
                    self._error(
                        DataNodeConfig._ID_KEY,
                        data_node.id,
                        f"The id of the DataNodeConfig `{data_node.id}` is overlapping with the "
                        f"property `{data_node.id}` of ScenarioConfig `{scenario_config_id}`.",
                    )

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
        if scenario_config.comparators is not None and not isinstance(scenario_config.comparators, dict):
            self._error(
                ScenarioConfig._COMPARATOR_KEY,
                scenario_config.comparators,
                f"{ScenarioConfig._COMPARATOR_KEY} field of ScenarioConfig"
                f" `{scenario_config_id}` must be populated with a dictionary value.",
            )
        elif scenario_config.comparators is not None:
            for data_node_id, comparator in scenario_config.comparators.items():
                if data_node_id not in Config.data_nodes:
                    self._error(
                        ScenarioConfig._COMPARATOR_KEY,
                        scenario_config.comparators,
                        f"The key `{data_node_id}` in {ScenarioConfig._COMPARATOR_KEY} field of ScenarioConfig"
                        f" `{scenario_config_id}` must be populated with a valid data node configuration id.",
                    )
                if not callable(comparator):
                    if not isinstance(comparator, list) or not all(callable(comp) for comp in comparator):
                        self._error(
                            ScenarioConfig._COMPARATOR_KEY,
                            scenario_config.comparators,
                            f"The value of `{data_node_id}` in {ScenarioConfig._COMPARATOR_KEY} field of ScenarioConfig"
                            f" `{scenario_config_id}` must be populated with a list of Callable values.",
                        )

    def _check_additional_dns_not_overlapping_tasks_dns(self, scenario_config_id: str, scenario_config: ScenarioConfig):
        data_node_configs = set()
        for task_config in scenario_config.task_configs:
            if isinstance(task_config, TaskConfig):
                input_dn_configs = task_config.input_configs if task_config.input_configs else []
                output_dn_configs = task_config.output_configs if task_config.output_configs else []
                data_node_configs.update({*input_dn_configs, *output_dn_configs})

        for additional_data_node_config in scenario_config.additional_data_node_configs:
            if additional_data_node_config in data_node_configs:
                self._warning(
                    ScenarioConfig._ADDITIONAL_DATA_NODES_KEY,
                    scenario_config.additional_data_node_configs,
                    f"The additional data node `{additional_data_node_config.id}` in"
                    f" {ScenarioConfig._ADDITIONAL_DATA_NODES_KEY} field of ScenarioConfig"
                    f" `{scenario_config_id}` has already existed as an input or output data node of"
                    f" ScenarioConfig `{scenario_config_id}` tasks.",
                )

    def _check_tasks_in_sequences_exist_in_scenario_tasks(
        self, scenario_config_id: str, scenario_config: ScenarioConfig
    ):
        scenario_task_ids = {
            task_config.id for task_config in scenario_config.tasks if isinstance(task_config, TaskConfig)
        }
        for sequence_tasks in scenario_config.sequences.values():
            self._check_children(
                ScenarioConfig,
                scenario_config_id,
                scenario_config._SEQUENCES_KEY,
                sequence_tasks,
                TaskConfig,
                can_be_empty=True,
            )
            for task in sequence_tasks:
                if isinstance(task, TaskConfig) and task.id not in scenario_task_ids:
                    self._error(
                        ScenarioConfig._SEQUENCES_KEY,
                        scenario_config.sequences,
                        f"The task `{task.id}` in {ScenarioConfig._SEQUENCES_KEY} field of ScenarioConfig"
                        f" `{scenario_config_id}` must exist in {ScenarioConfig._TASKS_KEY} field of ScenarioConfig"
                        f" `{scenario_config_id}`.",
                    )
