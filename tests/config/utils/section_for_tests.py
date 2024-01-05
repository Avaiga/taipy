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

from copy import copy
from typing import Any, Dict, Optional

from taipy.config import Config, Section
from taipy.config._config import _Config
from taipy.config.common._config_blocker import _ConfigBlocker


class SectionForTest(Section):
    name = "section_name"
    _MY_ATTRIBUTE_KEY = "attribute"

    def __init__(self, id: str, attribute: Any = None, **properties):
        self._attribute = attribute
        super().__init__(id, **properties)

    def __copy__(self):
        return SectionForTest(self.id, self._attribute, **copy(self._properties))

    @property
    def attribute(self):
        return self._replace_templates(self._attribute)

    @attribute.setter  # type: ignore
    @_ConfigBlocker._check()
    def attribute(self, val):
        self._attribute = val

    def _clean(self):
        self._attribute = None
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        if self._attribute is not None:
            as_dict[self._MY_ATTRIBUTE_KEY] = self._attribute
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config] = None):
        as_dict.pop(cls._ID_KEY, id)
        attribute = as_dict.pop(cls._MY_ATTRIBUTE_KEY, None)
        return SectionForTest(id=id, attribute=attribute, **as_dict)

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        self._attribute = as_dict.pop(self._MY_ATTRIBUTE_KEY, self._attribute)
        if self._attribute is None and default_section:
            self._attribute = default_section._attribute
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(id: str, attribute: str, **properties):
        section = SectionForTest(id, attribute, **properties)
        Config._register(section)
        return Config.sections[SectionForTest.name][id]
