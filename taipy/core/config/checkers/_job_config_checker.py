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

from typing import Dict

from taipy.config._config import _Config
from taipy.config.checker._checkers._config_checker import _ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector

from ..data_node_config import DataNodeConfig
from ..job_config import JobConfig


class _JobConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        if job_config := self._config._unique_sections.get(JobConfig.name):
            data_node_configs = self._config._sections[DataNodeConfig.name]
            self._check_multiprocess_mode(job_config, data_node_configs)
        return self._collector

    def _check_multiprocess_mode(self, job_config: JobConfig, data_node_configs: Dict[str, DataNodeConfig]):
        if job_config.is_standalone:
            for cfg_id, data_node_config in data_node_configs.items():
                if data_node_config.storage_type == DataNodeConfig._STORAGE_TYPE_VALUE_IN_MEMORY:
                    self._error(
                        DataNodeConfig._STORAGE_TYPE_KEY,
                        data_node_config.storage_type,
                        f"DataNode `{cfg_id}`: In-memory storage type can ONLY be used in "
                        f"{JobConfig._DEVELOPMENT_MODE} mode.",
                    )
