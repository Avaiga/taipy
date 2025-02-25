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
        if rest_configs := self._config._unique_sections.get(RestConfig.name):
            rest_config = cast(RestConfig, rest_configs)
            self._check_port(rest_config)
            self._check_host(rest_config)
            self._check_https_settings(rest_config)
        return self._collector

    def _check_port(self, rest_config: RestConfig):
        if not isinstance(rest_config.port, int) or not (1 <= rest_config.port <= 65535):
            self._error(
                "port",
                rest_config.port,
                "The port of the RestConfig must be an integer between 1 and 65535.",
            )

    def _check_host(self, rest_config: RestConfig):
        if not isinstance(rest_config.host, str) or not rest_config.host:
            self._error(
                "host", rest_config.host, "The host of the RestConfig must be a non-empty string."
            )

    def _check_https_settings(self, rest_config: RestConfig):
        if rest_config.use_https:
            if not rest_config.ssl_cert:
                self._error(
                    "ssl_cert",
                    rest_config.ssl_cert,
                    "When HTTPS is enabled in the RestConfig ssl_cert must be set.",
                )
            elif not isinstance(rest_config.ssl_cert, str):
                self._error(
                    "ssl_cert",
                    rest_config.ssl_cert,
                    "The ssl_cert of the RestConfig must be valid string.",
                )
            if not rest_config.ssl_key:
                self._error(
                    "ssl_key",
                    rest_config.ssl_key,
                    "When HTTPS is enabled in the RestConfig ssl_key must be set.",
                )
            elif not isinstance(rest_config.ssl_key, str):
                self._error(
                    "ssl_key",
                    rest_config.ssl_key,
                    "The ssl_key of the RestConfig must be valid string.",
                )
