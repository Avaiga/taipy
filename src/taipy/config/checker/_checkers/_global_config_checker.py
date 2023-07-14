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

from typing import Set

from ..._config import _Config
from ...common._template_handler import _TemplateHandler as tpl
from ...exceptions.exceptions import InconsistentEnvVariableError
from ...global_app.global_app_config import GlobalAppConfig
from ..issue_collector import IssueCollector
from ._config_checker import _ConfigChecker


class _GlobalConfigChecker(_ConfigChecker):

    _ACCEPTED_REPOSITORY_TYPES: Set[str] = {"filesystem"}

    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        global_config = self._config._global_config
        self._check_repository_type(global_config)
        return self._collector

    def _check_repository_type(self, global_config: GlobalAppConfig):
        value = global_config.repository_type
        if value not in self._ACCEPTED_REPOSITORY_TYPES:
            self._warning(
                global_config._REPOSITORY_TYPE_KEY,
                value,
                f'Unknown value "{value}" for field {global_config._REPOSITORY_TYPE_KEY} of GlobalAppConfig. '
                f'Default value "filesystem" is applied.',
            )
