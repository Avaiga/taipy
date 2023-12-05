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

import pytest
from taipy.config import Config
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def test_unique_section_registration_and_usage():
    assert Config.unique_sections is not None
    assert Config.unique_sections[UniqueSectionForTest.name] is not None
    assert Config.unique_sections[UniqueSectionForTest.name].attribute == "default_attribute"
    assert Config.unique_sections[UniqueSectionForTest.name].prop is None

    mySection = Config.configure_unique_section_for_tests(attribute="my_attribute", prop="my_prop")

    assert Config.unique_sections is not None
    assert Config.unique_sections[UniqueSectionForTest.name] is not None
    assert mySection is not None
    assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_attribute"
    assert mySection.attribute == "my_attribute"
    assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_prop"
    assert mySection.prop == "my_prop"

    myNewSection = Config.configure_unique_section_for_tests(attribute="my_new_attribute", prop="my_new_prop")

    assert Config.unique_sections is not None
    assert Config.unique_sections[UniqueSectionForTest.name] is not None
    assert myNewSection is not None
    assert mySection is not None
    assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_new_attribute"
    assert myNewSection.attribute == "my_new_attribute"
    assert mySection.attribute == "my_new_attribute"
    assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_new_prop"
    assert myNewSection.prop == "my_new_prop"
    assert mySection.prop == "my_new_prop"


def test_sections_exposed_as_attribute():
    assert Config.unique_section_name.attribute == "default_attribute"
    Config.configure_unique_section_for_tests("my_attribute")
    assert Config.unique_section_name.attribute == "my_attribute"

    assert Config.section_name["default"].attribute == "default_attribute"
    Config.configure_section_for_tests(id="my_id", attribute="my_attribute")
    assert Config.section_name["my_id"].attribute == "my_attribute"


def test_section_registration_and_usage():
    assert Config.sections is not None
    assert len(Config.sections) == 1
    assert Config.sections[SectionForTest.name] is not None
    assert len(Config.sections[SectionForTest.name]) == 1
    assert Config.sections[SectionForTest.name]["default"] is not None
    assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["default"].foo is None

    myFirstSection = Config.configure_section_for_tests(id="first", attribute="my_attribute", prop="my_prop", foo="bar")
    assert Config.sections is not None
    assert len(Config.sections) == 1
    assert Config.sections[SectionForTest.name] is not None
    assert len(Config.sections[SectionForTest.name]) == 2
    assert Config.sections[SectionForTest.name]["default"] is not None
    assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["default"].foo is None
    assert Config.sections[SectionForTest.name]["first"] is not None
    assert Config.sections[SectionForTest.name]["first"].attribute == "my_attribute"
    assert Config.sections[SectionForTest.name]["first"].prop == "my_prop"
    assert Config.sections[SectionForTest.name]["first"].foo == "bar"
    assert myFirstSection.attribute == "my_attribute"
    assert myFirstSection.prop == "my_prop"
    assert myFirstSection.foo == "bar"

    myNewSection = Config.configure_section_for_tests(id="second", attribute="my_new_attribute", prop="my_new_prop")
    assert Config.sections is not None
    assert len(Config.sections) == 1
    assert Config.sections[SectionForTest.name] is not None
    assert len(Config.sections[SectionForTest.name]) == 3
    assert Config.sections[SectionForTest.name]["default"] is not None
    assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["default"].foo is None
    assert Config.sections[SectionForTest.name]["first"] is not None
    assert Config.sections[SectionForTest.name]["first"].attribute == "my_attribute"
    assert Config.sections[SectionForTest.name]["first"].prop == "my_prop"
    assert Config.sections[SectionForTest.name]["first"].foo == "bar"
    assert Config.sections[SectionForTest.name]["second"] is not None
    assert Config.sections[SectionForTest.name]["second"].attribute == "my_new_attribute"
    assert Config.sections[SectionForTest.name]["second"].prop == "my_new_prop"
    assert Config.sections[SectionForTest.name]["second"].foo is None
    assert myFirstSection.attribute == "my_attribute"
    assert myFirstSection.prop == "my_prop"
    assert myFirstSection.foo == "bar"
    assert myNewSection.attribute == "my_new_attribute"
    assert myNewSection.prop == "my_new_prop"
    assert myNewSection.foo is None

    my2ndSection = Config.configure_section_for_tests(id="second", attribute="my_2nd_attribute", prop="my_2nd_prop")
    assert Config.sections is not None
    assert len(Config.sections) == 1
    assert Config.sections[SectionForTest.name] is not None
    assert len(Config.sections[SectionForTest.name]) == 3
    assert Config.sections[SectionForTest.name]["default"] is not None
    assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["default"].foo is None
    assert Config.sections[SectionForTest.name]["first"] is not None
    assert Config.sections[SectionForTest.name]["first"].attribute == "my_attribute"
    assert Config.sections[SectionForTest.name]["first"].prop == "my_prop"
    assert Config.sections[SectionForTest.name]["first"].foo == "bar"
    assert Config.sections[SectionForTest.name]["second"] is not None
    assert Config.sections[SectionForTest.name]["second"].attribute == "my_2nd_attribute"
    assert Config.sections[SectionForTest.name]["second"].prop == "my_2nd_prop"
    assert Config.sections[SectionForTest.name]["second"].foo is None
    assert myFirstSection.attribute == "my_attribute"
    assert myFirstSection.prop == "my_prop"
    assert myFirstSection.foo == "bar"
    assert myNewSection.attribute == "my_2nd_attribute"
    assert myNewSection.prop == "my_2nd_prop"
    assert myNewSection.foo is None
    assert my2ndSection.attribute == "my_2nd_attribute"
    assert my2ndSection.prop == "my_2nd_prop"
    assert my2ndSection.foo is None


def test_block_registration():
    myUniqueSection = Config.configure_unique_section_for_tests(attribute="my_unique_attribute", prop="my_unique_prop")
    mySection = Config.configure_section_for_tests(id="section_id", attribute="my_attribute", prop="my_prop", foo="bar")

    Config.block_update()

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.configure_unique_section_for_tests(attribute="my_new_unique_attribute", prop="my_new_unique_prop")

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.configure_section_for_tests(id="new", attribute="my_attribute", prop="my_prop", foo="bar")

    with pytest.raises(ConfigurationUpdateBlocked):
        myUniqueSection.attribute = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        myUniqueSection.properties = {"foo": "bar"}

    # myUniqueSection stay the same
    assert myUniqueSection.attribute == "my_unique_attribute"
    assert myUniqueSection.properties == {"prop": "my_unique_prop"}

    with pytest.raises(ConfigurationUpdateBlocked):
        mySection.attribute = "foo"

    with pytest.raises(ConfigurationUpdateBlocked):
        mySection.properties = {"foo": "foo"}

    # mySection stay the same
    assert mySection.attribute == "my_attribute"
    assert mySection.properties == {"prop": "my_prop", "foo": "bar", "prop_int": 0}
