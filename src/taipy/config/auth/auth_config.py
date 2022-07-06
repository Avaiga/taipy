# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from copy import copy
from typing import Any, Dict, Optional
from ..common._template_handler import _TemplateHandler as _tpl


class AuthConfig:
    """
    Configuration fields needed to use authentication feature.

    Attributes:
        protocol (str):  identifier of the authentication protocol. Taipy already implements three predefined
            protocols:
                - None: ...
                - taipy: ...
                - ldap: ...
        **properties: A dictionary of additional properties.
    """

    _PROTOCOL_KEY = "protocol"

    _PROTOCOL_LDAP = "ldap"
    _LDAP_SERVER = "ldap_server"
    _LDAP_BASE_DN = "ldap_base_dn"

    _PROTOCOL_TAIPY = "taipy"
    _TAIPY_ROLES = "roles"
    _TAIPY_PWD = "passwords"

    def __init__(self, protocol: str = None, **properties):
        self._protocol = protocol
        self._properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    def __copy__(self):
        return AuthConfig(self._protocol, **copy(self._properties))

    @property
    def protocol(self):
        return _tpl._replace_templates(self._protocol)

    @protocol.setter  # type: ignore
    def protocol(self, val):
        self._protocol = val

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    def properties(self, val):
        self._properties = val

    @classmethod
    def default_config(cls):
        return AuthConfig()

    def _to_dict(self):
        as_dict = {}
        if self._protocol is not None:
            as_dict[self._PROTOCOL_KEY] = self._protocol
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        config = AuthConfig()
        config._protocol = config_as_dict.pop(cls._PROTOCOL_KEY, None)
        config._properties = config_as_dict
        return config

    def _update(self, config_as_dict):
        self._protocol = config_as_dict.pop(self._PROTOCOL_KEY, self._protocol)
        self._properties.update(config_as_dict)
