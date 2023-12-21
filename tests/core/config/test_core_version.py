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

from unittest.mock import patch

import pytest

from taipy.config.config import Config
from taipy.core._init_version import _read_version
from taipy.core.config.core_section import CoreSection
from taipy.core.exceptions import ConfigCoreVersionMismatched
from tests.core.utils.named_temporary_file import NamedTemporaryFile

_MOCK_CORE_VERSION = "3.1.1"


@pytest.fixture(scope="function", autouse=True)
def mock_core_version():
    with patch("taipy.core.config.core_section._read_version") as mock_read_version:
        mock_read_version.return_value = _MOCK_CORE_VERSION
        CoreSection._CURRENT_CORE_VERSION = _MOCK_CORE_VERSION
        Config.unique_sections[CoreSection.name] = CoreSection.default_config()
        Config._default_config._unique_sections[CoreSection.name] = CoreSection.default_config()

        yield


@pytest.fixture(scope="session", autouse=True)
def reset_core_version():
    yield
    CoreSection._CURRENT_CORE_VERSION = _read_version()


class TestCoreVersionInCoreSectionConfig:
    major, minor, patch = _MOCK_CORE_VERSION.split(".")

    current_version = f"{major}.{minor}.{patch}"
    current_dev_version = f"{major}.{minor}.{patch}.dev0"
    compatible_future_version = f"{major}.{minor}.{int(patch) + 1}"
    compatible_future_dev_version = f"{major}.{minor}.{int(patch) + 1}.dev0"

    core_version_is_compatible = [
        # Current version and dev version should be compatible
        (f"{major}.{minor}.{patch}", True),
        (f"{major}.{minor}.{patch}.dev0", True),
        # Future versions with same major and minor should be compatible
        (f"{major}.{minor}.{int(patch) + 1}", True),
        (f"{major}.{minor}.{int(patch) + 1}.dev0", True),
        # Past versions with same major and minor should be compatible
        (f"{major}.{minor}.{int(patch) - 1}", True),
        (f"{major}.{minor}.{int(patch) - 1}.dev0", True),
        # Future versions with different minor number should be incompatible
        (f"{major}.{int(minor) + 1}.{patch}", False),
        (f"{major}.{int(minor) + 1}.{patch}.dev0", False),
        # Past versions with different minor number should be incompatible
        (f"{major}.{int(minor) - 1}.{patch}", False),
        (f"{major}.{int(minor) - 1}.{patch}.dev0", False),
    ]

    @pytest.mark.parametrize("core_version, is_compatible", core_version_is_compatible)
    def test_load_configuration_file(self, core_version, is_compatible):
        file_config = NamedTemporaryFile(
            f"""
            [TAIPY]

            [JOB]
            mode = "standalone"
            max_nb_of_workers = "2:int"

            [CORE]
            root_folder = "./taipy/"
            storage_folder = ".data/"
            repository_type = "filesystem"
            read_entity_retry = "0:int"
            mode = "development"
            version_number = ""
            force = "False:bool"
            core_version = "{core_version}"

            [VERSION_MIGRATION.migration_fcts]
            """
        )
        if is_compatible:
            Config.load(file_config.filename)
            assert Config.unique_sections[CoreSection.name]._core_version == _MOCK_CORE_VERSION
        else:
            with pytest.raises(ConfigCoreVersionMismatched):
                Config.load(file_config.filename)

    @pytest.mark.parametrize("core_version,is_compatible", core_version_is_compatible)
    def test_override_configuration_file(self, core_version, is_compatible):
        file_config = NamedTemporaryFile(
            f"""
            [TAIPY]

            [JOB]
            mode = "standalone"
            max_nb_of_workers = "2:int"

            [CORE]
            root_folder = "./taipy/"
            storage_folder = ".data/"
            repository_type = "filesystem"
            read_entity_retry = "0:int"
            mode = "development"
            version_number = ""
            force = "False:bool"
            core_version = "{core_version}"

            [VERSION_MIGRATION.migration_fcts]
            """
        )
        if is_compatible:
            Config.override(file_config.filename)
            assert Config.unique_sections[CoreSection.name]._core_version == _MOCK_CORE_VERSION
        else:
            with pytest.raises(ConfigCoreVersionMismatched):
                Config.override(file_config.filename)

    def test_load_configuration_file_without_core_section(self):
        file_config = NamedTemporaryFile(
            """
            [TAIPY]
            [JOB]
            mode = "standalone"
            max_nb_of_workers = "2:int"
            [CORE]
            root_folder = "./taipy/"
            storage_folder = ".data/"
            repository_type = "filesystem"
            read_entity_retry = "0:int"
            mode = "development"
            version_number = ""
            force = "False:bool"
            [VERSION_MIGRATION.migration_fcts]
            """
        )
        Config.load(file_config.filename)
        assert Config.unique_sections[CoreSection.name]._core_version == _MOCK_CORE_VERSION
