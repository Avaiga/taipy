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

from taipy.config.config import Config
from taipy.config.global_app.global_app_config import GlobalAppConfig
from taipy.config.section import Section
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def _test_default_global_app_config(global_config: GlobalAppConfig):
    assert global_config is not None
    assert not global_config.notification
    assert len(global_config.properties) == 0


def test_default_configuration():
    default_config = Config._default_config
    assert default_config._unique_sections is not None
    assert len(default_config._unique_sections) == 1
    assert default_config._unique_sections[UniqueSectionForTest.name] is not None
    assert default_config._unique_sections[UniqueSectionForTest.name].attribute == "default_attribute"
    assert default_config._sections is not None
    assert len(default_config._sections) == 1

    _test_default_global_app_config(default_config._global_config)
    _test_default_global_app_config(Config.global_config)
    _test_default_global_app_config(GlobalAppConfig().default_config())


def test_register_default_configuration():
    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute", prop1="prop1"))

    # Replace the first default section
    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute", prop2="prop2"))

    default_section = Config.sections[SectionForTest.name][Section._DEFAULT_KEY]
    assert len(default_section.properties) == 1
    assert default_section.prop2 == "prop2"
    assert default_section.prop1 is None
