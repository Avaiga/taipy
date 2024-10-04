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

import re
from typing import Dict, List, Set

from .._serializer._json_serializer import _JsonSerializer


class _ComparatorResult(dict):
    ADDED_ITEMS_KEY = "added_items"
    REMOVED_ITEMS_KEY = "removed_items"
    MODIFIED_ITEMS_KEY = "modified_items"

    CONFLICTED_SECTION_KEY = "conflicted_sections"
    UNCONFLICTED_SECTION_KEY = "unconflicted_sections"

    def __init__(self, unconflicted_sections: Set[str]):
        super().__init__()

        self._unconflicted_sections = unconflicted_sections

    def _sort_by_section(self):
        if self.get(self.CONFLICTED_SECTION_KEY):
            for key in self[self.CONFLICTED_SECTION_KEY].keys():
                self[self.CONFLICTED_SECTION_KEY][key].sort(key=lambda x: x[0][0])

        if self.get(self.UNCONFLICTED_SECTION_KEY):
            for key in self[self.UNCONFLICTED_SECTION_KEY].keys():
                self[self.UNCONFLICTED_SECTION_KEY][key].sort(key=lambda x: x[0][0])

    def _check_added_items(self, config_deepdiff, new_json_config):
        if dictionary_item_added := config_deepdiff.get("dictionary_item_added"):
            for item_added in dictionary_item_added:
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_added)
                diff_sections = self.__get_section(section_name)

                if attribute:
                    value_added = new_json_config[section_name][config_id][attribute]
                elif config_id:
                    value_added = new_json_config[section_name][config_id]
                else:
                    value_added = new_json_config[section_name]

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self.ADDED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_added)),
                )

    def _check_removed_items(self, config_deepdiff, old_json_config):
        if dictionary_item_removed := config_deepdiff.get("dictionary_item_removed"):
            for item_removed in dictionary_item_removed:
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_removed)
                diff_sections = self.__get_section(section_name)

                if attribute:
                    value_removed = old_json_config[section_name][config_id][attribute]
                elif config_id:
                    value_removed = old_json_config[section_name][config_id]
                else:
                    value_removed = old_json_config[section_name]

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self.REMOVED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_removed)),
                )

    def _check_modified_items(self, config_deepdiff, old_json_config, new_json_config):
        if values_changed := config_deepdiff.get("values_changed"):
            for item_changed, value_changed in values_changed.items():
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_changed)
                diff_sections = self.__get_section(section_name)

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self.MODIFIED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_changed["old_value"], value_changed["new_value"])),
                )

        # Iterable item added will be considered a modified item
        if iterable_item_added := config_deepdiff.get("iterable_item_added"):
            self.__check_modified_iterable(iterable_item_added, old_json_config, new_json_config)

        # Iterable item removed will be considered a modified item
        if iterable_item_removed := config_deepdiff.get("iterable_item_removed"):
            self.__check_modified_iterable(iterable_item_removed, old_json_config, new_json_config)

    def __check_modified_iterable(self, iterable_items, old_json_config, new_json_config):
        for item in iterable_items:
            section_name, config_id, attribute = self.__get_changed_entity_attribute(item)
            diff_sections = self.__get_section(section_name)

            if attribute:
                new_value = new_json_config[section_name][config_id][attribute]
                old_value = old_json_config[section_name][config_id][attribute]
            else:
                new_value = new_json_config[section_name][config_id]
                old_value = old_json_config[section_name][config_id]

            section_name = self.__rename_global_node_name(section_name)
            modified_value = ((section_name, config_id, attribute), (old_value, new_value))

            if (
                not diff_sections.get(self.MODIFIED_ITEMS_KEY)
                or modified_value not in diff_sections[self.MODIFIED_ITEMS_KEY]
            ):
                self.__create_or_append_list(
                    diff_sections,
                    self.MODIFIED_ITEMS_KEY,
                    modified_value,
                )

    def __get_section(self, section_name: str) -> Dict[str, List]:
        if section_name in self._unconflicted_sections:
            if not self.get(self.UNCONFLICTED_SECTION_KEY):
                self[self.UNCONFLICTED_SECTION_KEY] = {}
            return self[self.UNCONFLICTED_SECTION_KEY]

        if not self.get(self.CONFLICTED_SECTION_KEY):
            self[self.CONFLICTED_SECTION_KEY] = {}
        return self[self.CONFLICTED_SECTION_KEY]

    def __create_or_append_list(self, diff_dict, key, value):
        if diff_dict.get(key):
            diff_dict[key].append(value)
        else:
            diff_dict[key] = [value]

    def __get_changed_entity_attribute(self, attribute_bracket_notation):
        """Split the section name, the config id (if exists), and the attribute name (if exists)
        from JSON bracket notation.
        """
        try:
            section_name, config_id, attribute = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
        except ValueError:
            try:
                section_name, config_id = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
                attribute = None
            except ValueError:
                section_name = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)[0]
                config_id = None
                attribute = None

        return section_name, config_id, attribute

    def __rename_global_node_name(self, node_name):
        if node_name == _JsonSerializer._GLOBAL_NODE_NAME:
            return "Global Configuration"
        return node_name
