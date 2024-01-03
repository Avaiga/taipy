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

from unittest import mock

from taipy.config import Config
from taipy.config._config import _Config
from taipy.config._config_comparator._comparator_result import _ComparatorResult
from taipy.config.global_app.global_app_config import GlobalAppConfig
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


class TestConfigComparator:
    unique_section_1 = UniqueSectionForTest(attribute="unique_attribute_1", prop="unique_prop_1")
    unique_section_1b = UniqueSectionForTest(attribute="unique_attribute_1", prop="unique_prop_1b")
    section_1 = SectionForTest("section_1", attribute="attribute_1", prop="prop_1")
    section_2 = SectionForTest("section_2", attribute=2, prop="prop_2")
    section_2b = SectionForTest("section_2", attribute="attribute_2", prop="prop_2b")
    section_3 = SectionForTest("section_3", attribute=[1, 2, 3, 4], prop=["prop_1"])
    section_3b = SectionForTest("section_3", attribute=[1, 2], prop=["prop_1", "prop_2", "prop_3"])
    section_3c = SectionForTest("section_3", attribute=[2, 1], prop=["prop_3", "prop_1", "prop_2"])

    def test_comparator_compare_method_call(self):
        _config_1 = _Config._default_config()
        _config_2 = _Config._default_config()

        with mock.patch(
            "taipy.config._config_comparator._config_comparator._ConfigComparator._find_conflict_config"
        ) as mck:
            Config._comparator._find_conflict_config(_config_1, _config_2)
            mck.assert_called_once_with(_config_1, _config_2)

    def test_comparator_without_diff(self):
        _config_1 = _Config._default_config()
        _config_2 = _Config._default_config()

        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)
        assert isinstance(config_diff, _ComparatorResult)
        assert config_diff == {}

    def test_comparator_with_updated_global_config(self):
        _config_1 = _Config._default_config()
        _config_1._global_config = GlobalAppConfig(foo="bar")

        _config_2 = _Config._default_config()
        _config_2._global_config = GlobalAppConfig(foo="baz", bar="foo")

        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        assert config_diff.get("unconflicted_sections") is None
        assert config_diff.get("conflicted_sections") is not None

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["modified_items"]) == 1
        assert conflicted_config_diff["modified_items"][0] == (
            ("Global Configuration", "foo", None),
            ("bar", "baz"),
        )
        assert len(conflicted_config_diff["added_items"]) == 1
        assert conflicted_config_diff["added_items"][0] == (
            ("Global Configuration", "bar", None),
            "foo",
        )

    def test_comparator_with_new_section(self):
        _config_1 = _Config._default_config()

        # The first "section_name" is added to the Config
        _config_2 = _Config._default_config()
        _config_2._sections[SectionForTest.name] = {"section_1": self.section_1}
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["added_items"]) == 1
        assert conflicted_config_diff["added_items"][0] == (
            ("section_name", None, None),
            {"section_1": {"attribute": "attribute_1", "prop": "prop_1"}},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("removed_items") is None

        # A new "section_name" is added to the Config
        _config_3 = _Config._default_config()
        _config_3._sections[SectionForTest.name] = {"section_1": self.section_1, "section_2": self.section_2}
        config_diff = Config._comparator._find_conflict_config(_config_2, _config_3)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["added_items"]) == 1
        assert conflicted_config_diff["added_items"][0] == (
            ("section_name", "section_2", None),
            {"attribute": "2:int", "prop": "prop_2"},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("removed_items") is None

    def test_comparator_with_removed_section(self):
        _config_1 = _Config._default_config()

        # All "section_name" sections are removed from the Config
        _config_2 = _Config._default_config()
        _config_2._sections[SectionForTest.name] = {"section_1": self.section_1}
        config_diff = Config._comparator._find_conflict_config(_config_2, _config_1)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["removed_items"]) == 1
        assert conflicted_config_diff["removed_items"][0] == (
            ("section_name", None, None),
            {"section_1": {"attribute": "attribute_1", "prop": "prop_1"}},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("added_items") is None

        # Section "section_1" is removed from the Config
        _config_3 = _Config._default_config()
        _config_3._sections[SectionForTest.name] = {"section_1": self.section_1, "section_2": self.section_2}
        config_diff = Config._comparator._find_conflict_config(_config_3, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["removed_items"]) == 1
        assert conflicted_config_diff["removed_items"][0] == (
            ("section_name", "section_2", None),
            {"attribute": "2:int", "prop": "prop_2"},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("added_items") is None

    def test_comparator_with_modified_section(self):
        _config_1 = _Config._default_config()
        _config_1._sections[SectionForTest.name] = {"section_2": self.section_2}

        # All "section_name" sections are removed from the Config
        _config_2 = _Config._default_config()
        _config_2._sections[SectionForTest.name] = {"section_2": self.section_2b}
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["modified_items"]) == 2
        assert conflicted_config_diff["modified_items"][0] == (
            ("section_name", "section_2", "attribute"),
            ("2:int", "attribute_2"),
        )
        assert conflicted_config_diff["modified_items"][1] == (
            ("section_name", "section_2", "prop"),
            ("prop_2", "prop_2b"),
        )
        assert conflicted_config_diff.get("removed_items") is None
        assert conflicted_config_diff.get("added_items") is None

    def test_comparator_with_modified_list_attribute(self):
        _config_1 = _Config._default_config()
        _config_1._sections[SectionForTest.name] = {"section_3": self.section_3}

        # All "section_name" sections are removed from the Config
        _config_2 = _Config._default_config()
        _config_2._sections[SectionForTest.name] = {"section_3": self.section_3b}
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["modified_items"]) == 2
        assert conflicted_config_diff["modified_items"][0] == (
            ("section_name", "section_3", "prop"),
            (["prop_1"], ["prop_1", "prop_2", "prop_3"]),
        )
        assert conflicted_config_diff["modified_items"][1] == (
            ("section_name", "section_3", "attribute"),
            (["1:int", "2:int", "3:int", "4:int"], ["1:int", "2:int"]),
        )
        assert conflicted_config_diff.get("removed_items") is None
        assert conflicted_config_diff.get("added_items") is None

    def test_comparator_with_different_order_list_attributes(self):
        _config_1 = _Config._default_config()
        _config_1._unique_sections
        _config_1._sections[SectionForTest.name] = {"section_3": self.section_3b}

        # Create _config_2 with different order of list attributes
        _config_2 = _Config._default_config()
        _config_2._sections[SectionForTest.name] = {"section_3": self.section_3c}
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        # There should be no difference since the order of list attributes is ignored
        assert config_diff == {}

    def test_comparator_with_new_unique_section(self):
        _config_1 = _Config._default_config()

        _config_2 = _Config._default_config()
        _config_2._unique_sections[UniqueSectionForTest.name] = self.unique_section_1
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["added_items"]) == 1
        assert conflicted_config_diff["added_items"][0] == (
            ("unique_section_name", None, None),
            {"attribute": "unique_attribute_1", "prop": "unique_prop_1"},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("removed_items") is None

    def test_comparator_with_removed_unique_section(self):
        _config_1 = _Config._default_config()

        _config_2 = _Config._default_config()
        _config_2._unique_sections[UniqueSectionForTest.name] = self.unique_section_1
        config_diff = Config._comparator._find_conflict_config(_config_2, _config_1)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["removed_items"]) == 1
        assert conflicted_config_diff["removed_items"][0] == (
            ("unique_section_name", None, None),
            {"attribute": "unique_attribute_1", "prop": "unique_prop_1"},
        )
        assert conflicted_config_diff.get("modified_items") is None
        assert conflicted_config_diff.get("added_items") is None

    def test_comparator_with_modified_unique_section(self):
        _config_1 = _Config._default_config()
        _config_1._unique_sections[UniqueSectionForTest.name] = self.unique_section_1

        # All "section_name" sections are removed from the Config
        _config_2 = _Config._default_config()
        _config_2._unique_sections[UniqueSectionForTest.name] = self.unique_section_1b
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        conflicted_config_diff = config_diff["conflicted_sections"]
        assert len(conflicted_config_diff["modified_items"]) == 1
        assert conflicted_config_diff["modified_items"][0] == (
            ("unique_section_name", "prop", None),
            ("unique_prop_1", "unique_prop_1b"),
        )
        assert conflicted_config_diff.get("removed_items") is None
        assert conflicted_config_diff.get("added_items") is None

    def test_unconflicted_section_name_store_statically(self):
        Config._comparator._add_unconflicted_section("section_name_1")
        assert Config._comparator._unconflicted_sections == {"section_name_1"}

        Config._comparator._add_unconflicted_section("section_name_2")
        assert Config._comparator._unconflicted_sections == {"section_name_1", "section_name_2"}

        Config._comparator._add_unconflicted_section("section_name_1")
        assert Config._comparator._unconflicted_sections == {"section_name_1", "section_name_2"}

    def test_unconflicted_diff_is_stored_separated_from_conflicted_ones(self):
        _config_1 = _Config._default_config()
        _config_1._unique_sections[UniqueSectionForTest.name] = self.unique_section_1
        _config_1._sections[SectionForTest.name] = {"section_2": self.section_2}

        _config_2 = _Config._default_config()
        _config_2._unique_sections[UniqueSectionForTest.name] = self.unique_section_1b
        _config_2._sections[SectionForTest.name] = {"section_2": self.section_2b}

        # Compare 2 Configuration
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)

        assert config_diff.get("unconflicted_sections") is None
        assert config_diff.get("conflicted_sections") is not None
        assert len(config_diff["conflicted_sections"]["modified_items"]) == 3

        # Ignore any diff of "section_name" and compare
        Config._comparator._add_unconflicted_section("section_name")
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)
        assert config_diff.get("unconflicted_sections") is not None
        assert len(config_diff["unconflicted_sections"]["modified_items"]) == 2
        assert config_diff.get("conflicted_sections") is not None
        assert len(config_diff["conflicted_sections"]["modified_items"]) == 1

        # Ignore any diff of Global Config and compare
        Config._comparator._add_unconflicted_section(["unique_section_name"])
        config_diff = Config._comparator._find_conflict_config(_config_1, _config_2)
        assert config_diff.get("unconflicted_sections") is not None
        assert len(config_diff["unconflicted_sections"]["modified_items"]) == 3
        assert config_diff.get("conflicted_sections") is None

    def test_comparator_log_message(self, caplog):
        _config_1 = _Config._default_config()
        _config_1._unique_sections[UniqueSectionForTest.name] = self.unique_section_1
        _config_1._sections[SectionForTest.name] = {"section_2": self.section_2}

        _config_2 = _Config._default_config()
        _config_2._unique_sections[UniqueSectionForTest.name] = self.unique_section_1b
        _config_2._sections[SectionForTest.name] = {"section_2": self.section_2b}

        # Ignore any diff of "section_name" and compare
        Config._comparator._add_unconflicted_section("section_name")
        Config._comparator._find_conflict_config(_config_1, _config_2)

        error_messages = caplog.text.strip().split("\n")
        assert len(error_messages) == 5
        assert all(
            t in error_messages[0]
            for t in [
                "INFO",
                "There are non-conflicting changes between the current configuration and the current configuration:",
            ]
        )
        assert 'section_name "section_2" has attribute "attribute" modified: 2:int -> attribute_2' in error_messages[1]
        assert 'section_name "section_2" has attribute "prop" modified: prop_2 -> prop_2b' in error_messages[2]
        assert all(
            t in error_messages[3]
            for t in [
                "ERROR",
                "The current configuration conflicts with the current configuration:",
            ]
        )
        assert 'unique_section_name "prop" was modified: unique_prop_1 -> unique_prop_1b' in error_messages[4]

        caplog.clear()

        Config._comparator._find_conflict_config(_config_1, _config_2, old_version_number="1.0")

        error_messages = caplog.text.strip().split("\n")
        assert len(error_messages) == 5
        assert all(
            t in error_messages[0]
            for t in [
                "INFO",
                "There are non-conflicting changes between the configuration for version 1.0 and the current "
                "configuration:",
            ]
        )
        assert all(
            t in error_messages[3]
            for t in [
                "ERROR",
                "The configuration for version 1.0 conflicts with the current configuration:",
            ]
        )

        caplog.clear()

        Config._comparator._compare(
            _config_1,
            _config_2,
            version_number_1="1.0",
            version_number_2="2.0",
        )

        error_messages = caplog.text.strip().split("\n")
        assert len(error_messages) == 3
        assert all(
            t in error_messages[0]
            for t in ["INFO", "Differences between version 1.0 Configuration and version 2.0 Configuration:"]
        )

        caplog.clear()
