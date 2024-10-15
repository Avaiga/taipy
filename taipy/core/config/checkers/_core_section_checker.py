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

from typing import Set, cast

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector

from ..core_section import CoreSection


class _CoreSectionChecker(_ConfigChecker):
    _ACCEPTED_REPOSITORY_TYPES: Set[str] = {"filesystem", "sql"}

    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        if core_section := self._config._unique_sections.get(CoreSection.name):
            core_section = cast(CoreSection, core_section)
            self._check_repository_type(core_section)
        return self._collector

    def _check_repository_type(self, core_section: CoreSection):
        value = core_section.repository_type
        if value not in self._ACCEPTED_REPOSITORY_TYPES:
            self._warning(
                core_section._REPOSITORY_TYPE_KEY,
                value,
                f'Value "{value}" for field {core_section._REPOSITORY_TYPE_KEY} of the CoreSection is not supported. '
                f'Default value "filesystem" is applied.',
            )
