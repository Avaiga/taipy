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

from copy import copy
from typing import Any, Dict, List, Optional

from src.taipy.config import Config, Section
from src.taipy.config._config import _Config
from src.taipy.config.common._config_blocker import _ConfigBlocker

from .section_for_tests import SectionForTest


class SectionOfSectionsListForTest(Section):

    name = "list_section_name"
    _MY_ATTRIBUTE_KEY = "attribute"
    _SECTIONS_LIST_KEY = "sections_list"

    def __init__(self, id: str, attribute: Any = None, sections_list: List = None, **properties):
        self._attribute = attribute
        self._sections_list = sections_list if sections_list else []
        super().__init__(id, **properties)

    def __copy__(self):
        return SectionOfSectionsListForTest(
            self.id, self._attribute, copy(self._sections_list), **copy(self._properties)
        )

    @property
    def attribute(self):
        return self._replace_templates(self._attribute)

    @attribute.setter  # type: ignore
    @_ConfigBlocker._check()
    def attribute(self, val):
        self._attribute = val

    @property
    def sections_list(self):
        return list(self._sections_list)

    @sections_list.setter  # type: ignore
    @_ConfigBlocker._check()
    def sections_list(self, val):
        self._sections_list = val

    def _clean(self):
        self._attribute = None
        self._sections_list = []
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        if self._attribute is not None:
            as_dict[self._MY_ATTRIBUTE_KEY] = self._attribute
        if self._sections_list:
            as_dict[self._SECTIONS_LIST_KEY] = self._sections_list
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config] = None):
        as_dict.pop(cls._ID_KEY, id)
        attribute = as_dict.pop(cls._MY_ATTRIBUTE_KEY, None)
        section_configs = config._sections.get(SectionForTest.name, None) or []  # type: ignore
        sections_list = []
        if inputs_as_str := as_dict.pop(cls._SECTIONS_LIST_KEY, None):
            for section_id in inputs_as_str:
                if section_id in section_configs:
                    sections_list.append(section_configs[section_id])
                else:
                    sections_list.append(section_id)
        return SectionOfSectionsListForTest(id=id, attribute=attribute, sections_list=sections_list, **as_dict)

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        self._attribute = as_dict.pop(self._MY_ATTRIBUTE_KEY, self._attribute)
        if self._attribute is None and default_section:
            self._attribute = default_section._attribute
        self._sections_list = as_dict.pop(self._SECTIONS_LIST_KEY, self._sections_list)
        if self._sections_list is None and default_section:
            self._sections_list = default_section._sections_list
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(id: str, attribute: str, sections_list: List = None, **properties):
        section = SectionOfSectionsListForTest(id, attribute, sections_list, **properties)
        Config._register(section)
        return Config.sections[SectionOfSectionsListForTest.name][id]
