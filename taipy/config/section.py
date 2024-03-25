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

from abc import abstractmethod
from typing import Any, Dict, Optional

from .common._config_blocker import _ConfigBlocker
from .common._template_handler import _TemplateHandler as _tpl
from .common._validate_id import _validate_id


class Section:
    """A Section as a consistent part of the Config.

    A section is defined by the section name (representing the type of objects that are configured) and a section id.
    """

    _DEFAULT_KEY = "default"
    _ID_KEY = "id"

    def __init__(self, id, **properties):
        self.id = _validate_id(id)
        self._properties = properties or dict()

    @abstractmethod
    def __copy__(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def _clean(self):
        raise NotImplementedError

    @abstractmethod
    def _to_dict(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any], id, config):
        raise NotImplementedError

    @abstractmethod
    def _update(self, config_as_dict, default_section=None):
        raise NotImplementedError

    def __getattr__(self, item: str) -> Optional[Any]:
        return self._replace_templates(self._properties.get(item, None))

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    @_ConfigBlocker._check()
    def properties(self, val):
        self._properties = val

    def _replace_templates(self, value):
        return _tpl._replace_templates(value)
