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

import json
from copy import copy
from typing import Optional, Set, Union

from deepdiff import DeepDiff

from ...logger._taipy_logger import _TaipyLogger
from .._config import _Config
from .._serializer._json_serializer import _JsonSerializer
from ._comparator_result import _ComparatorResult


class _ConfigComparator:
    def __init__(self):
        self._unconflicted_sections: Set[str] = set()
        self.__logger = _TaipyLogger._get_logger()

    def _add_unconflicted_section(self, section_name: Union[str, Set[str]]):
        if isinstance(section_name, str):
            section_name = {section_name}

        self._unconflicted_sections.update(section_name)

    def _find_conflict_config(
        self,
        old_config: _Config,
        new_config: _Config,
        old_version_number: Optional[str] = None,
        new_version_number: Optional[str] = None,
    ):
        """Compare between 2 _Config object to check for compatibility.

        Args:
            old_config (_Config): The old _Config.
            new_config (_Config): The new _Config.
            old_version_number (str, optional): The old version number for logging. Defaults to None.
            new_version_number (str, optional): The new version number for logging. Defaults to None.

        Returns:
            _ComparatorResult: Return a _ComparatorResult dictionary with the following format:
        ```python
        {
            "added_items": [
                ((section_name_1, config_id_1, attribute_1), added_object_1),
                ((section_name_2, config_id_2, attribute_2), added_object_2),
            ],
            "removed_items": [
                ((section_name_1, config_id_1, attribute_1), removed_object_1),
                ((section_name_2, config_id_2, attribute_2), removed_object_2),
            ],
            "modified_items": [
                ((section_name_1, config_id_1, attribute_1), (old_value_1, new_value_1)),
                ((section_name_2, config_id_2, attribute_2), (old_value_2, new_value_2)),
            ],
        }
        ```
        """
        comparator_result = self.__get_config_diff(old_config, new_config)
        self.__log_find_conflict_message(comparator_result, old_version_number, new_version_number)
        return comparator_result

    def _compare(
        self,
        config_1: _Config,
        config_2: _Config,
        version_number_1: str,
        version_number_2: str,
    ):
        """Compare between 2 _Config object to check for compatibility.

        Args:
            config_1 (_Config): The old _Config.
            config_2 (_Config): The new _Config.
            version_number_1 (str): The old version number for logging.
            version_number_2 (str): The new version number for logging.
        """
        comparator_result = self.__get_config_diff(config_1, config_2)
        self.__log_comparison_message(comparator_result, version_number_1, version_number_2)

        return comparator_result

    def __get_config_diff(self, config_1, config_2):
        json_config_1 = json.loads(_JsonSerializer._serialize(config_1))
        json_config_2 = json.loads(_JsonSerializer._serialize(config_2))

        config_deepdiff = DeepDiff(json_config_1, json_config_2, ignore_order=True)

        comparator_result = _ComparatorResult(copy(self._unconflicted_sections))

        comparator_result._check_added_items(config_deepdiff, json_config_2)
        comparator_result._check_removed_items(config_deepdiff, json_config_1)
        comparator_result._check_modified_items(config_deepdiff, json_config_1, json_config_2)
        comparator_result._sort_by_section()

        return comparator_result

    def __log_comparison_message(
        self,
        comparator_result: _ComparatorResult,
        version_number_1: str,
        version_number_2: str,
    ):
        config_str_1 = f"version {version_number_1} Configuration"
        config_str_2 = f"version {version_number_2} Configuration"

        diff_messages = []
        for _, sections in comparator_result.items():
            diff_messages = self.__get_messages(sections)

        if diff_messages:
            self.__logger.info(
                f"Differences between {config_str_1} and {config_str_2}:\n\t" + "\n\t".join(diff_messages)
            )
        else:
            self.__logger.info(f"There is no difference between {config_str_1} and {config_str_2}.")

    def __log_find_conflict_message(
        self,
        comparator_result: _ComparatorResult,
        old_version_number: Optional[str] = None,
        new_version_number: Optional[str] = None,
    ):
        old_config_str = (
            f"configuration for version {old_version_number}" if old_version_number else "current configuration"
        )
        new_config_str = (
            f"configuration for version {new_version_number}" if new_version_number else "current configuration"
        )

        if unconflicted_sections := comparator_result.get(_ComparatorResult.UNCONFLICTED_SECTION_KEY):
            unconflicted_messages = self.__get_messages(unconflicted_sections)
            self.__logger.info(
                f"There are non-conflicting changes between the {old_config_str}"
                f" and the {new_config_str}:\n\t" + "\n\t".join(unconflicted_messages)
            )

        if conflicted_sections := comparator_result.get(_ComparatorResult.CONFLICTED_SECTION_KEY):
            conflicted_messages = self.__get_messages(conflicted_sections)
            self.__logger.error(
                f"The {old_config_str} conflicts with the {new_config_str}:\n\t" + "\n\t".join(conflicted_messages)
            )

    def __get_messages(self, diff_sections):
        dq = '"'
        messages = []

        if added_items := diff_sections.get(_ComparatorResult.ADDED_ITEMS_KEY):
            for diff in added_items:
                ((section_name, config_id, attribute), added_object) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} added: {added_object}"
                )

        if removed_items := diff_sections.get(_ComparatorResult.REMOVED_ITEMS_KEY):
            for diff in removed_items:
                ((section_name, config_id, attribute), removed_object) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} removed"
                )

        if modified_items := diff_sections.get(_ComparatorResult.MODIFIED_ITEMS_KEY):
            for diff in modified_items:
                ((section_name, config_id, attribute), (old_value, new_value)) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} modified: "
                    f"{old_value} -> {new_value}"
                )

        return messages
