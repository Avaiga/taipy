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

from ..pipeline_config import PipelineConfig
from ..task_config import TaskConfig


class _PipelineConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        pipeline_configs = self._config._sections[PipelineConfig.name]
        for pipeline_config_id, pipeline_config in pipeline_configs.items():
            if pipeline_config_id != _Config.DEFAULT_KEY:
                self._check_if_entity_property_key_used_is_predefined(pipeline_config)
                self._check_existing_config_id(pipeline_config)
                self._check_tasks(pipeline_config_id, pipeline_config)
        return self._collector

    def _check_tasks(self, pipeline_config_id: str, pipeline_config: PipelineConfig):
        self._check_children(
            PipelineConfig, pipeline_config_id, pipeline_config._TASK_KEY, pipeline_config.tasks, TaskConfig
        )
