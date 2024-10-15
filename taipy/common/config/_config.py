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
from typing import Dict

from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection


class _Config:
    DEFAULT_KEY = "default"

    def __init__(self) -> None:
        self._sections: Dict[str, Dict[str, Section]] = {}
        self._unique_sections: Dict[str, UniqueSection] = {}
        self._global_config: GlobalAppConfig = GlobalAppConfig()

    def _clean(self) -> None:
        self._global_config._clean()
        for unique_section in self._unique_sections.values():
            unique_section._clean()
        for sections in self._sections.values():
            for section in sections.values():
                section._clean()

    @classmethod
    def _default_config(cls):
        config = _Config()
        config._global_config = GlobalAppConfig.default_config()
        return config

    def _update(self, other_config) -> None:
        self._global_config._update(other_config._global_config._to_dict())
        if other_config._unique_sections:
            for section_name, other_section in other_config._unique_sections.items():
                if section := self._unique_sections.get(section_name, None):
                    section._update(other_section._to_dict())
                else:
                    self._unique_sections[section_name] = copy(other_config._unique_sections[section_name])
        if other_config._sections:
            for section_name, other_non_unique_sections in other_config._sections.items():
                if non_unique_sections := self._sections.get(section_name, None):
                    self.__update_sections(non_unique_sections, other_non_unique_sections)
                else:
                    self._sections[section_name] = {}
                    self.__add_sections(self._sections[section_name], other_non_unique_sections)

    def __add_sections(self, entity_config, other_entity_configs) -> None:
        for cfg_id, sub_config in other_entity_configs.items():
            entity_config[cfg_id] = copy(sub_config)
            self.__point_nested_section_to_self(sub_config)

    def __update_sections(self, entity_config, other_entity_configs) -> None:
        if self.DEFAULT_KEY in other_entity_configs:
            if self.DEFAULT_KEY in entity_config:
                entity_config[self.DEFAULT_KEY]._update(other_entity_configs[self.DEFAULT_KEY]._to_dict())
            else:
                entity_config[self.DEFAULT_KEY] = other_entity_configs[self.DEFAULT_KEY]
        for cfg_id, sub_config in other_entity_configs.items():
            if cfg_id != self.DEFAULT_KEY:
                if cfg_id not in entity_config:
                    entity_config[cfg_id] = copy(sub_config)
                entity_config[cfg_id]._update(sub_config._to_dict(), entity_config.get(self.DEFAULT_KEY))
            self.__point_nested_section_to_self(sub_config)

    def __point_nested_section_to_self(self, section) -> None:
        """Loop through attributes of a Section to find if any attribute has a list of Section as value.
        If there is, update each nested Section by the corresponding instance in self.

        Args:
            section (Section): The Section to search for nested sections.
        """
        for _, attr_value in vars(section).items():
            # ! This will fail if an attribute is a dictionary, or nested list of Sections.
            if not isinstance(attr_value, list):
                continue

            for index, item in enumerate(attr_value):
                if not isinstance(item, Section):
                    continue

                if sub_item := self._sections.get(item.name, {}).get(item.id, None):
                    attr_value[index] = sub_item
