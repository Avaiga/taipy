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

import json
import re

from deepdiff import DeepDiff

from ._base_serializer import _BaseSerializer
from ._config import _Config
from .config import Config


class _ConfigComparator(dict):
    """Compare between 2 _Config object to check for compatibility.

    Return a dictionary with the following format:
    ```python
    {
        "added_items": [
            ((entity_name_1, entity_id_1, attribute_1), added_object_1),
            ((entity_name_2, entity_id_2, attribute_2), added_object_2),
        ],
        "removed_items": [
            ((entity_name_1, entity_id_1, attribute_1), removed_object_1),
            ((entity_name_2, entity_id_2, attribute_2), removed_object_2),
        ],
        "modified_items": [
            ((entity_name_1, entity_id_1, attribute_1), (old_value_1, new_value_1)),
            ((entity_name_2, entity_id_2, attribute_2), (old_value_2, new_value_2)),
        ],
    }
    ```
    """

    def __init__(self, old_conf: _Config, new_conf: _Config):
        super().__init__()

        self.old_conf_json = json.loads(Config._to_json(old_conf))  # type: ignore
        self.new_conf_json = json.loads(Config._to_json(new_conf))  # type: ignore

        self.deepdiff_result = DeepDiff(self.old_conf_json, self.new_conf_json)

        self.__setitem__("added_items", [])
        self.__setitem__("removed_items", [])
        self.__setitem__("modified_items", [])

        self._check_added_items()

        self._check_removed_items()

        self._check_modified_items()

        # Sort by entity name
        self["added_items"].sort(key=lambda x: x[0][0])
        self["removed_items"].sort(key=lambda x: x[0][0])
        self["modified_items"].sort(key=lambda x: x[0][0])

    def _check_added_items(self):
        if dictionary_item_added := self.deepdiff_result.get("dictionary_item_added"):
            for item_added in dictionary_item_added:
                entity_name, entity_id, attribute = self.__get_changed_entity_attribute(item_added)

                if attribute:
                    value_added = self.new_conf_json[entity_name][entity_id][attribute]
                else:
                    value_added = self.new_conf_json[entity_name][entity_id]

                entity_name = self.__rename_global_node_name(entity_name)

                self["added_items"].append(((entity_name, entity_id, attribute), (value_added)))

    def _check_removed_items(self):
        if dictionary_item_removed := self.deepdiff_result.get("dictionary_item_removed"):
            for item_removed in dictionary_item_removed:
                entity_name, entity_id, attribute = self.__get_changed_entity_attribute(item_removed)

                if attribute:
                    value_removed = self.old_conf_json[entity_name][entity_id][attribute]
                else:
                    value_removed = self.old_conf_json[entity_name][entity_id]

                entity_name = self.__rename_global_node_name(entity_name)

                self["removed_items"].append(((entity_name, entity_id, attribute), (value_removed)))

    def _check_modified_items(self):
        if values_changed := self.deepdiff_result.get("values_changed"):
            for item_changed, value_changed in values_changed.items():
                entity_name, entity_id, attribute = self.__get_changed_entity_attribute(item_changed)
                entity_name = self.__rename_global_node_name(entity_name)

                self["modified_items"].append(
                    ((entity_name, entity_id, attribute), (value_changed["old_value"], value_changed["new_value"]))
                )

        # Iterable item added will be considered a modified item
        if iterable_item_added := self.deepdiff_result.get("iterable_item_added"):
            self.__check_modified_iterable(iterable_item_added)

        # Iterable item removed will be considered a modified item
        if iterable_item_removed := self.deepdiff_result.get("iterable_item_removed"):
            self.__check_modified_iterable(iterable_item_removed)

    def __check_modified_iterable(self, iterable_items):
        for item in iterable_items:
            entity_name, entity_id, attribute = self.__get_changed_entity_attribute(item)

            if attribute:
                new_value = self.new_conf_json[entity_name][entity_id][attribute]
                old_value = self.old_conf_json[entity_name][entity_id][attribute]
            else:
                new_value = self.new_conf_json[entity_name][entity_id]
                old_value = self.old_conf_json[entity_name][entity_id]

            entity_name = self.__rename_global_node_name(entity_name)

            if not ((entity_name, entity_id, attribute), (old_value, new_value)) in self["modified_items"]:
                self["modified_items"].append(((entity_name, entity_id, attribute), (old_value, new_value)))

    def __get_changed_entity_attribute(self, attribute_bracket_notation):
        """Split the entity name, entity id (if exists), and the attribute name from JSON bracket notation."""
        try:
            entity_name, entity_id, attribute = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
        except ValueError:
            entity_name, entity_id = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
            attribute = None

        return entity_name, entity_id, attribute

    def __rename_global_node_name(self, node_name):
        if node_name == _BaseSerializer._GLOBAL_NODE_NAME:
            return "Global Configuration"
        return node_name
