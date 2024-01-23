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

from taipy.config.config import Config
from taipy.config.section import Section
from tests.config.utils.named_temporary_file import NamedTemporaryFile
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.section_of_sections_list_for_tests import SectionOfSectionsListForTest


@pytest.fixture
def _init_list_section_for_test():
    Config._register_default(SectionOfSectionsListForTest(Section._DEFAULT_KEY, [], prop="default_prop", prop_int=0))
    Config.configure_list_section_for_tests = SectionOfSectionsListForTest._configure
    Config.list_section_name = Config.sections[SectionOfSectionsListForTest.name]


def test_applied_config_compilation_does_not_change_other_configs():
    assert len(Config._default_config._unique_sections) == 1
    assert Config._default_config._unique_sections["unique_section_name"] is not None
    assert Config._default_config._unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config._default_config._unique_sections["unique_section_name"].prop is None
    assert len(Config._python_config._unique_sections) == 0
    assert len(Config._file_config._unique_sections) == 0
    assert len(Config._env_file_config._unique_sections) == 0
    assert len(Config._applied_config._unique_sections) == 1
    assert Config._applied_config._unique_sections["unique_section_name"] is not None
    assert Config._applied_config._unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config._applied_config._unique_sections["unique_section_name"].prop is None
    assert len(Config.unique_sections) == 1
    assert Config.unique_sections["unique_section_name"] is not None
    assert Config.unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config.unique_sections["unique_section_name"].prop is None
    assert (
        Config._applied_config._unique_sections["unique_section_name"]
        is not Config._default_config._unique_sections["unique_section_name"]
    )

    Config.configure_unique_section_for_tests("qwe", prop="rty")

    assert len(Config._default_config._unique_sections) == 1
    assert Config._default_config._unique_sections["unique_section_name"] is not None
    assert Config._default_config._unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config._default_config._unique_sections["unique_section_name"].prop is None
    assert len(Config._python_config._unique_sections) == 1
    assert Config._python_config._unique_sections["unique_section_name"] is not None
    assert Config._python_config._unique_sections["unique_section_name"].attribute == "qwe"
    assert Config._python_config._unique_sections["unique_section_name"].prop == "rty"
    assert (
        Config._python_config._unique_sections["unique_section_name"]
        != Config._default_config._unique_sections["unique_section_name"]
    )
    assert len(Config._file_config._unique_sections) == 0
    assert len(Config._env_file_config._unique_sections) == 0
    assert len(Config._applied_config._unique_sections) == 1
    assert Config._applied_config._unique_sections["unique_section_name"] is not None
    assert Config._applied_config._unique_sections["unique_section_name"].attribute == "qwe"
    assert Config._applied_config._unique_sections["unique_section_name"].prop == "rty"
    assert (
        Config._python_config._unique_sections["unique_section_name"]
        != Config._applied_config._unique_sections["unique_section_name"]
    )
    assert (
        Config._default_config._unique_sections["unique_section_name"]
        != Config._applied_config._unique_sections["unique_section_name"]
    )
    assert len(Config.unique_sections) == 1
    assert Config.unique_sections["unique_section_name"] is not None
    assert Config.unique_sections["unique_section_name"].attribute == "qwe"
    assert Config.unique_sections["unique_section_name"].prop == "rty"


def test_nested_section_instance_in_python(_init_list_section_for_test):
    s1_cfg = Config.configure_section_for_tests("s1", attribute="foo")
    s2_cfg = Config.configure_section_for_tests("s2", attribute="bar")
    ss_cfg = Config.configure_list_section_for_tests("ss", attribute="foo", sections_list=[s1_cfg, s2_cfg])

    s1_config_applied_instance = Config.section_name["s1"]
    s1_config_python_instance = Config._python_config._sections[SectionForTest.name]["s1"]

    s2_config_applied_instance = Config.section_name["s2"]
    s2_config_python_instance = Config._python_config._sections[SectionForTest.name]["s2"]

    assert ss_cfg.sections_list[0] is s1_config_applied_instance
    assert ss_cfg.sections_list[0] is not s1_config_python_instance
    assert ss_cfg.sections_list[1] is s2_config_applied_instance
    assert ss_cfg.sections_list[1] is not s2_config_python_instance


def _configure_in_toml():
    return NamedTemporaryFile(
        content="""
[TAIPY]

[section_name.s1]
attribute = "foo"

[section_name.s2]
attribute = "bar"

[list_section_name.ss]
sections_list = [ "foo", "s1:SECTION", "s2:SECTION"]
    """
    )


def test_nested_section_instance_load_toml(_init_list_section_for_test):
    toml_config = _configure_in_toml()
    Config.load(toml_config)

    s1_config_applied_instance = Config.section_name["s1"]
    s1_config_python_instance = Config._python_config._sections[SectionForTest.name]["s1"]

    s2_config_applied_instance = Config.section_name["s2"]
    s2_config_python_instance = Config._python_config._sections[SectionForTest.name]["s2"]

    ss_cfg = Config.list_section_name["ss"]

    assert ss_cfg.sections_list[0] == "foo"
    assert ss_cfg.sections_list[1] is s1_config_applied_instance
    assert ss_cfg.sections_list[1] is not s1_config_python_instance
    assert ss_cfg.sections_list[2] is s2_config_applied_instance
    assert ss_cfg.sections_list[2] is not s2_config_python_instance


def test_nested_section_instance_override_toml(_init_list_section_for_test):
    toml_config = _configure_in_toml()
    Config.override(toml_config)

    s1_config_applied_instance = Config.section_name["s1"]
    s1_config_python_instance = Config._file_config._sections[SectionForTest.name]["s1"]

    s2_config_applied_instance = Config.section_name["s2"]
    s2_config_python_instance = Config._file_config._sections[SectionForTest.name]["s2"]

    ss_cfg = Config.list_section_name["ss"]

    assert ss_cfg.sections_list[0] == "foo"
    assert ss_cfg.sections_list[1] is s1_config_applied_instance
    assert ss_cfg.sections_list[1] is not s1_config_python_instance
    assert ss_cfg.sections_list[2] is s2_config_applied_instance
    assert ss_cfg.sections_list[1] is not s2_config_python_instance
