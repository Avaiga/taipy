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

from ..._config import _Config
from ..issue_collector import IssueCollector
from ._config_checker import _ConfigChecker


class _AuthConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        auth_config = self._config._auth_config  # type: ignore
        self._check_predefined_protocol(auth_config)
        return self._collector

    def _check_predefined_protocol(self, auth_config):
        if auth_config.protocol == auth_config._PROTOCOL_LDAP:
            self.__check_ldap(auth_config)
        if auth_config.protocol == auth_config._PROTOCOL_TAIPY:
            self.__check_taipy(auth_config)

    def __check_taipy(self, auth_config):
        if auth_config._TAIPY_ROLES not in auth_config.properties:
            self._error(
                "properties",
                auth_config._LDAP_SERVER,
                f"`{auth_config._LDAP_SERVER}` property must be populated when {auth_config._PROTOCOL_LDAP} is used.",
            )
        if auth_config._TAIPY_PWD not in auth_config.properties:
            self._warning(
                "properties",
                auth_config._TAIPY_PWD,
                f"`In order to protect authentication with passwords using {auth_config._PROTOCOL_TAIPY} protocol,"
                f" {auth_config._TAIPY_PWD}` property can be populated.",
            )

    def __check_ldap(self, auth_config):
        if auth_config._LDAP_SERVER not in auth_config.properties:
            self._error(
                "properties",
                auth_config._LDAP_SERVER,
                f"`{auth_config._LDAP_SERVER}` attribute must be populated when {auth_config._PROTOCOL_LDAP} is used.",
            )
        if auth_config._LDAP_BASE_DN not in auth_config.properties:
            self._error(
                "properties",
                auth_config._LDAP_BASE_DN,
                f"`{auth_config._LDAP_BASE_DN}` field must be populated when {auth_config._PROTOCOL_LDAP} is used.",
            )
