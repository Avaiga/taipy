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

import os
from unittest import mock

import pytest

from taipy.common.config.exceptions.exceptions import InvalidConfigurationId
from tests.common.config.utils.section_for_tests import SectionForTest
from tests.common.config.utils.unique_section_for_tests import UniqueSectionForTest


class WrongUniqueSection(UniqueSectionForTest):
    name = "1wrong_id"


class WrongSection(SectionForTest):
    name = "correct_name"


def test_section_uses_valid_id():
    with pytest.raises(InvalidConfigurationId):
        WrongUniqueSection(attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("wrong id", attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("1wrong_id", attribute="foo")
    with pytest.raises(InvalidConfigurationId):
        WrongSection("wrong_@id", attribute="foo")


def test_templated_properties_are_replaced():
    with mock.patch.dict(os.environ, {"foo": "bar", "baz": "1"}):
        u_sect = UniqueSectionForTest(attribute="attribute", tpl_property="ENV[foo]")
        assert u_sect.tpl_property == "bar"

        sect = SectionForTest(id="my_id", attribute="attribute", tpl_property="ENV[baz]:int")
        assert sect.tpl_property == 1
