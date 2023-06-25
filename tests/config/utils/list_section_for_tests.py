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


class ListSectionForTest(Section):

    name = "list_section_name"
    _SECTIONS_LIST_KEY = "sections_list"

    def __init__(self, id: str, sections_list: List = None, **properties):
        self._sections_list = sections_list if sections_list else []
        super().__init__(id, **properties)

    def __copy__(self):
        return ListSectionForTest(self.id, copy(self._sections_list), **copy(self._properties))

    @property
    def sections_list(self):
        return list(self._sections_list)

    @sections_list.setter  # type: ignore
    @_ConfigBlocker._check()
    def sections_list(self, val):
        self._sections_list = val

    def _clean(self):
        self._sections_list = []
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        if self._sections_list:
            as_dict[self._SECTIONS_LIST_KEY] = self._sections_list
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config] = None):
        as_dict.pop(cls._ID_KEY, id)
        section_configs = config._sections.get(SectionForTest.name, None) or []  # type: ignore
        sections_list = []
        if inputs_as_str := as_dict.pop(cls._SECTIONS_LIST_KEY, None):
            sections_list = [
                section_configs[section_id] for section_id in inputs_as_str if section_id in section_configs
            ]
        return ListSectionForTest(id=id, sections_list=sections_list, **as_dict)

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        self._sections_list = as_dict.pop(self._SECTIONS_LIST_KEY, self._sections_list)
        if self._sections_list is None and default_section:
            self._sections_list = default_section._sections_list
        self._properties.update(as_dict)
        if default_section:
            self._properties = {**default_section.properties, **self._properties}

    @staticmethod
    def _configure(id: str, sections_list: List = None, **properties):
        section = ListSectionForTest(id, sections_list, **properties)
        Config._register(section)
        return Config.sections[ListSectionForTest.name][id]
