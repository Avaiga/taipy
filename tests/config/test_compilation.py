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
from src.taipy.config.config import Config


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
    assert Config._applied_config._unique_sections["unique_section_name"] is not Config._default_config._unique_sections["unique_section_name"]

    Config.configure_unique_section_for_tests("qwe", prop="rty")

    assert len(Config._default_config._unique_sections) == 1
    assert Config._default_config._unique_sections["unique_section_name"] is not None
    assert Config._default_config._unique_sections["unique_section_name"].attribute == "default_attribute"
    assert Config._default_config._unique_sections["unique_section_name"].prop is None
    assert len(Config._python_config._unique_sections) == 1
    assert Config._python_config._unique_sections["unique_section_name"] is not None
    assert Config._python_config._unique_sections["unique_section_name"].attribute == "qwe"
    assert Config._python_config._unique_sections["unique_section_name"].prop == "rty"
    assert Config._python_config._unique_sections["unique_section_name"] != Config._default_config._unique_sections["unique_section_name"]
    assert len(Config._file_config._unique_sections) == 0
    assert len(Config._env_file_config._unique_sections) == 0
    assert len(Config._applied_config._unique_sections) == 1
    assert Config._applied_config._unique_sections["unique_section_name"] is not None
    assert Config._applied_config._unique_sections["unique_section_name"].attribute == "qwe"
    assert Config._applied_config._unique_sections["unique_section_name"].prop == "rty"
    assert Config._python_config._unique_sections["unique_section_name"] != Config._applied_config._unique_sections["unique_section_name"]
    assert Config._default_config._unique_sections["unique_section_name"] != Config._applied_config._unique_sections["unique_section_name"]
    assert len(Config.unique_sections) == 1
    assert Config.unique_sections["unique_section_name"] is not None
    assert Config.unique_sections["unique_section_name"].attribute == "qwe"
    assert Config.unique_sections["unique_section_name"].prop == "rty"
