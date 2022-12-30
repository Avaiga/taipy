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

from src.taipy.config._config import _Config
from src.taipy.config._config_comparator import _ConfigComparator
from src.taipy.config.global_app.global_app_config import GlobalAppConfig
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def test_config_comparator():
    unique_section_1 = UniqueSectionForTest(attribute="unique_attribute_1", prop="unique_prop_1")
    section_1 = SectionForTest("section_1", attribute="attribute_1", prop="prop_1")
    section_2 = SectionForTest("section_2", attribute=2, prop="prop_2")
    section_3 = SectionForTest("section_3", attribute=3, prop="prop_3")
    section_4 = SectionForTest("section_4", attribute=4, prop="prop_4")

    _config_1 = _Config._default_config()
    _config_1._sections[SectionForTest.name] = {"section_1": section_1, "section_2": section_2, "section_4": section_4}
    _config_1._unique_sections[UniqueSectionForTest.name] = unique_section_1

    _config_2 = _Config._default_config()

    # Update some global config
    _config_2._global_config = GlobalAppConfig(
        root_folder="foo",
        storage_folder="bar",
        repository_properties={"foo": "bar"},
        repository_type="baz",
        clean_entities_enabled=True,
    )
    # Update section_2, add section_3, and remove section 4
    _config_2._sections[SectionForTest.name] = {"section_1": section_1, "section_2": section_3, "section_3": section_2}
    _config_2._unique_sections[UniqueSectionForTest.name] = unique_section_1

    config_diff = _ConfigComparator._compare(_config_1, _config_2)

    # The result was sorted so test by indexing is fine.
    assert len(config_diff["added_items"]) == 2
    assert config_diff["added_items"][1] == (
        ("section_name", "section_3", None),
        {"attribute": "2:int", "prop": "prop_2"},
    )

    # TODO: This should not in ["added_items"] since it is a default value that was changed. This should be fixed soon.
    assert config_diff["added_items"][0] == (("Global Configuration", "repository_properties", None), {"foo": "bar"})

    assert len(config_diff["modified_items"]) == 6
    assert config_diff["modified_items"][0] == (("Global Configuration", "root_folder", None), ("./taipy/", "foo"))
    assert config_diff["modified_items"][1] == (("Global Configuration", "storage_folder", None), (".data/", "bar"))
    assert config_diff["modified_items"][2] == (
        ("Global Configuration", "clean_entities_enabled", None),
        ("ENV[TAIPY_CLEAN_ENTITIES_ENABLED]", "True:bool"),
    )
    assert config_diff["modified_items"][3] == (
        ("Global Configuration", "repository_type", None),
        ("filesystem", "baz"),
    )
    assert config_diff["modified_items"][4] == (("section_name", "section_2", "attribute"), ("2:int", "3:int"))
    assert config_diff["modified_items"][5] == (("section_name", "section_2", "prop"), ("prop_2", "prop_3"))

    assert len(config_diff["removed_items"]) == 1
    assert config_diff["removed_items"][0] == (
        ("section_name", "section_4", None),
        {"attribute": "4:int", "prop": "prop_4"},
    )
