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
import pytest

from src.taipy.config import Config
from tests.config.sectionForTest import SectionForTest


def test_temporary():
    global_1 = Config.configure_global_app(root_folder="toto")
    assert global_1.root_folder == "toto"
    assert Config.global_config.root_folder == "toto"

    global_2 = Config.configure_global_app()
    assert global_1.root_folder == "toto"
    assert global_2.root_folder == "./taipy/"
    assert Config.global_config.root_folder == "./taipy/"


def test_section_registration():
    assert Config.sections is not None
    assert Config.sections[SectionForTest.name] is not None
    # assert Config.sub is not None
    assert Config.sections[SectionForTest.name].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name].prop is None

    mySection = Config.configure_section_for_test(attribute="my_attribute", prop="my_prop")

    assert Config.sections is not None
    assert Config.sections[SectionForTest.name] is not None
    assert Config.sections[SectionForTest.name].attribute == "my_attribute"
    assert Config.sections[SectionForTest.name].prop == "my_prop"
    assert mySection is not None
    assert mySection.attribute == "my_attribute"
    assert mySection.prop == "my_prop"

    myNewSection = Config.configure_section_for_test(attribute="my_new_attribute", prop="my_new_prop")

    assert Config.sections is not None
    assert Config.sections[SectionForTest.name] is not None
    assert Config.sections[SectionForTest.name].attribute == "my_new_attribute"
    assert Config.sections[SectionForTest.name].prop == "my_new_prop"

    assert myNewSection is not None
    assert myNewSection.attribute == "my_new_attribute"
    assert myNewSection.prop == "my_new_prop"

    assert mySection is not None
    assert mySection.attribute == "my_new_attribute"
    assert mySection.prop == "my_new_prop"
