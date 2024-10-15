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

import pytest

from taipy.common.config import Config
from taipy.common.config.section import Section
from tests.common.config.utils.section_for_tests import SectionForTest
from tests.common.config.utils.unique_section_for_tests import UniqueSectionForTest


@pytest.fixture(scope="function", autouse=True)
def reset(reset_configuration_singleton):
    reset_configuration_singleton()
    register_test_sections()


def register_test_sections():
    Config._register_default(UniqueSectionForTest("default_attribute"))
    Config.configure_unique_section_for_tests = UniqueSectionForTest._configure
    Config.unique_section_name = Config.unique_sections[UniqueSectionForTest.name]

    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute", prop="default_prop", prop_int=0))
    Config.configure_section_for_tests = SectionForTest._configure
    Config.section_name = Config.sections[SectionForTest.name]
