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

from typing import Dict, List

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector


class _ConfigIdChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        existing_config_ids: Dict[str, List[str]] = {}
        for entity_type, section_dictionary in self._config._sections.items():
            for config_id in section_dictionary.keys():
                if config_id in existing_config_ids:
                    existing_config_ids[config_id].append(entity_type)
                else:
                    existing_config_ids[config_id] = [entity_type]

        for config_id, entity_types in existing_config_ids.items():
            if config_id != "default" and len(entity_types) > 1:
                self._error(
                    "config_id",
                    config_id,
                    f"`{config_id}` is used as the config_id of multiple configurations {str(entity_types)}",
                )
        return self._collector
