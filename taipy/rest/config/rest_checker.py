# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import cast

from taipy.common.config._config import _Config
from taipy.common.config.checker._checkers._config_checker import _ConfigChecker
from taipy.common.config.checker.issue_collector import IssueCollector

from .rest_config import RestConfig


class _RestConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        rest_configs = cast(dict, self._config._sections.get(RestConfig.name, {}))

        for rest_config_id, rest_config in rest_configs.items():
            if rest_config_id != _Config.DEFAULT_KEY:
                self._check_port(rest_config_id, rest_config)
                self._check_host(rest_config_id, rest_config)
                self._check_https_settings(rest_config_id, rest_config)

        return self._collector

    def _check_port(self, rest_config_id: str, rest_config: RestConfig):
        if not isinstance(rest_config.port, int) or not (1 <= rest_config.port <= 65535):
            self._error(
                "port",
                rest_config.port,
                f"The port of RestConfig `{rest_config_id}` must be an integer between 1 and 65535.",
            )

    def _check_host(self, rest_config_id: str, rest_config: RestConfig):
        if not isinstance(rest_config.host, str) or not rest_config.host:
            self._error(
                "host", rest_config.host, f"The host of RestConfig `{rest_config_id}` must be a non-empty string."
            )

    def _check_https_settings(self, rest_config_id: str, rest_config: RestConfig):
        if rest_config.use_https:
            if not rest_config.ssl_cert or not rest_config.ssl_key:
                self._error(
                    "ssl_cert/ssl_key",
                    (rest_config.ssl_cert, rest_config.ssl_key),
                    f"When HTTPS is enabled in RestConfig `{rest_config_id}`, both ssl_cert and ssl_key must be set.",
                )
            elif not isinstance(rest_config.ssl_cert, str) or not isinstance(rest_config.ssl_key, str):
                self._error(
                    "ssl_cert/ssl_key",
                    (rest_config.ssl_cert, rest_config.ssl_key),
                    f"The ssl_cert and ssl_key of RestConfig `{rest_config_id}` must be valid strings.",
                )
