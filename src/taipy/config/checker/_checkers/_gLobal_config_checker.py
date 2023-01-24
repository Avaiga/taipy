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

from ..._config import _Config
from ._config_checker import _ConfigChecker
from ..issue_collector import IssueCollector
from ...global_app.global_app_config import GlobalAppConfig
from ...exceptions.exceptions import InconsistentEnvVariableError
from ...common._template_handler import _TemplateHandler as tpl


class _GlobalConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        global_config = self._config._global_config
        self._check_clean_entities_enabled_type(global_config)
        return self._collector

    def _check_clean_entities_enabled_type(self, global_config: GlobalAppConfig):
        value = global_config._clean_entities_enabled

        if isinstance(global_config._clean_entities_enabled, str):
            try:
                value = tpl._replace_templates(
                    global_config._clean_entities_enabled,
                    type=bool,
                    required=False,
                    default=GlobalAppConfig._DEFAULT_CLEAN_ENTITIES_ENABLED,
                )
            except InconsistentEnvVariableError:
                pass
        if isinstance(value, bool):
            return
        self._error(
            global_config._CLEAN_ENTITIES_ENABLED_KEY,
            value,
            f"{global_config._CLEAN_ENTITIES_ENABLED_KEY} field must be populated with a boolean value.",
        )
