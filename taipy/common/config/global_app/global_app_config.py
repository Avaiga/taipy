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

from __future__ import annotations

from typing import Any, Dict, Optional

from ..common._config_blocker import _ConfigBlocker
from ..common._template_handler import _TemplateHandler as _tpl


class GlobalAppConfig:
    """Configuration attributes related to the global application."""

    def __init__(self, **properties):
        self._properties = properties

    @property
    def properties(self) -> Dict[str, Any]:
        """A dictionary of additional properties."""
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    @_ConfigBlocker._check()
    def properties(self, val) -> None:
        self._properties = val

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @classmethod
    def default_config(cls) -> GlobalAppConfig:
        """Return the GlobalAppConfig section used by default.

        Returns:
            The default configuration.
        """
        return GlobalAppConfig()

    def _clean(self):
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        config = GlobalAppConfig()
        config._properties = config_as_dict
        return config

    def _update(self, config_as_dict):
        self._properties.update(config_as_dict)
