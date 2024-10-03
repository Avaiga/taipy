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
from unittest.mock import patch

import pytest

from taipy.common.config import Config
from taipy.common.config.exceptions.exceptions import MissingEnvVariableError
from taipy.core import Orchestrator
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.config import CoreSection
from tests.core.utils.named_temporary_file import NamedTemporaryFile


def test_core_section():
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
    assert Config.core.mode == "development"
    assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_development_version()
    assert not Config.core.force
    orchestrator.stop()

    with patch("sys.argv", ["prog"]):
        Config.configure_core(mode="experiment", version_number="test_num", force=True)
        orchestrator = Orchestrator()
        orchestrator.run()
    assert Config.core.mode == "experiment"
    assert Config.core.version_number == "test_num"
    assert Config.core.force
    orchestrator.stop()

    toml_config = NamedTemporaryFile(
        content="""
[TAIPY]

[CORE]
mode = "experiment"
version_number = "test_num_2"
force = "true:bool"
        """
    )
    Config.load(toml_config.filename)
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
    assert Config.core.mode == "experiment"
    assert Config.core.version_number == "test_num_2"
    assert Config.core.force
    orchestrator.stop()

    with patch("sys.argv", ["prog", "--experiment", "test_num_3", "--no-taipy-force"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == "test_num_3"
        assert not Config.core.force
        orchestrator.stop()


def test_config_attribute_overiden_by_code_config_including_env_variable_values():
    assert Config.core.root_folder == CoreSection._DEFAULT_ROOT_FOLDER
    assert Config.core.storage_folder == CoreSection._DEFAULT_STORAGE_FOLDER
    Config.configure_core(root_folder="ENV[ROOT_FOLDER]", storage_folder="ENV[STORAGE_FOLDER]")

    with pytest.raises(MissingEnvVariableError):
        _ = Config.core.root_folder
    with pytest.raises(MissingEnvVariableError):
        _ = Config.core.storage_folder

    with patch.dict(os.environ, {"ROOT_FOLDER": "foo", "STORAGE_FOLDER": "bar"}):
        assert Config.core.root_folder == "foo"
        assert Config.core.storage_folder == "bar"

    with patch.dict(os.environ, {"ROOT_FOLDER": "baz", "STORAGE_FOLDER": "qux"}):
        assert Config.core.root_folder == "baz"
        assert Config.core.storage_folder == "qux"


def test_clean_config():
    core_config = Config.configure_core(mode="experiment", version_number="test_num", force=True)

    assert Config.core is core_config

    core_config._clean()

    # Check if the instance before and after _clean() is the same
    assert Config.core is core_config

    assert core_config.mode == "development"
    assert core_config.version_number == ""

    assert core_config.force is False
    assert core_config.properties == {}
