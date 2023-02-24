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

from ..data_node_config import DataNodeConfig
from ..task_config import TaskConfig


class _TaskConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        task_configs = self._config._sections[TaskConfig.name]
        for task_config_id, task_config in task_configs.items():
            if task_config_id != _Config.DEFAULT_KEY:
                self._check_existing_config_id(task_config)
                self._check_if_entity_property_key_used_is_predefined(task_config)
                self._check_existing_function(task_config_id, task_config)
                self._check_inputs(task_config_id, task_config)
                self._check_outputs(task_config_id, task_config)
        return self._collector

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
        else:
            if not callable(task_config.function):
                self._error(
                    task_config._FUNCTION,
                    task_config.function,
                    f"{task_config._FUNCTION} field of TaskConfig `{task_config_id}` must be"
                    f" populated with Callable value.",
                )
