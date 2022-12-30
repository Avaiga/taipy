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

import json
import re
from typing import Dict, List, Tuple

from deepdiff import DeepDiff

from ._base_serializer import _BaseSerializer
from ._config import _Config
from .config import Config


class _ConfigComparator:
    @classmethod
    def _compare(cls, old_conf: _Config, new_conf: _Config) -> Dict[str, List[Tuple[Tuple[str]]]]:
        """Compare between 2 _Config object to check for compatibility.

        Return a dictionary with the following format:
        {
            "item_added": [
                ((entity_name_1, entity_id_1, attribute_1), added_object_1),
                ((entity_name_2, entity_id_2, attribute_2), added_object_2),
            ],
            "item_changed": [
                ((entity_name_1, entity_id_1, attribute_1), (old_value_1, new_value_1)),
                ((entity_name_2, entity_id_2, attribute_2), (old_value_2, new_value_2)),
            ],
            "item_removed": [
                ((entity_name_1, entity_id_1, attribute_1), removed_object_1),
                ((entity_name_2, entity_id_2, attribute_2), removed_object_2),
            ],
        }
        """
        old_conf_json = json.loads(Config._to_json(old_conf))  # type: ignore
        new_conf_json = json.loads(Config._to_json(new_conf))  # type: ignore

        deepdiff_result = DeepDiff(old_conf_json, new_conf_json)

        config_diff: Dict[str, List] = {
            "added_items": [],
            "removed_items": [],
            "modified_items": [],
        }

        if dictionary_item_added := deepdiff_result.get("dictionary_item_added"):
            for item_added in dictionary_item_added:
                entity_name, entity_id, attribute = cls.__get_changed_entity_attribute(item_added)

                if attribute:
                    value_added = new_conf_json[entity_name][entity_id][attribute]
                else:
                    value_added = new_conf_json[entity_name][entity_id]

                entity_name = cls.__rename_global_node_name(entity_name)

                config_diff["added_items"].append(((entity_name, entity_id, attribute), (value_added)))

        if dictionary_item_removed := deepdiff_result.get("dictionary_item_removed"):
            for item_removed in dictionary_item_removed:
                entity_name, entity_id, attribute = cls.__get_changed_entity_attribute(item_removed)

                if attribute:
                    value_removed = old_conf_json[entity_name][entity_id][attribute]
                else:
                    value_removed = old_conf_json[entity_name][entity_id]

                entity_name = cls.__rename_global_node_name(entity_name)

                config_diff["removed_items"].append(((entity_name, entity_id, attribute), (value_removed)))

        if values_changed := deepdiff_result.get("values_changed"):
            for item_changed, value_changed in values_changed.items():
                entity_name, entity_id, attribute = cls.__get_changed_entity_attribute(item_changed)
                entity_name = cls.__rename_global_node_name(entity_name)

                config_diff["modified_items"].append(
                    ((entity_name, entity_id, attribute), (value_changed["old_value"], value_changed["new_value"]))
                )

        # Sort by entity name
        config_diff["added_items"].sort(key=lambda x: x[0][0])
        config_diff["removed_items"].sort(key=lambda x: x[0][0])
        config_diff["modified_items"].sort(key=lambda x: x[0][0])

        return config_diff

    @classmethod
    def __get_changed_entity_attribute(cls, attribute_bracket_notation):
        """Split the entity name, entity id (if exists), and the attribute name from JSON bracket notation."""
        try:
            entity_name, entity_id, attribute = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
        except ValueError:
            entity_name, entity_id = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
            attribute = None

        return entity_name, entity_id, attribute

    @classmethod
    def __rename_global_node_name(cls, node_name):
        if node_name == _BaseSerializer._GLOBAL_NODE_NAME:
            return "Global Configuration"
        return node_name
