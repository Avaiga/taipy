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

from src.taipy.core.config.core_section import CoreSection
from src.taipy.core.exceptions import ConfigCoreVersionMismatched
from taipy.config.config import Config
from tests.core.utils.named_temporary_file import NamedTemporaryFile


class TestCoreVersionInCoreSectionConfig:
    CoreSection._CURRENT_CORE_VERSION = "3.0.1"

    @pytest.mark.parametrize(
        "core_version,is_compatible",
        [
            ("3.0.1", True),  # current version
            ("3.0.1.dev0", True),  # current dev version
            ("3.0.2", True),  # future but compatible
            ("3.0.2.dev0", True),  # dev future but compatible
            ("3.0.0", True),  # past but compatible
            ("3.0.0.dev0", True),  # dev past but compatible
            ("3.1.0", False),  # future but incompatible
            ("3.1.0.dev0", False),  # dev future but incompatible
            ("2.1.0", False),  # past but incompatible
            ("2.1.0.dev0", False),  # dev past but incompatible
        ],
    )
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
            assert Config.unique_sections[CoreSection.name]._core_version == "3.0.1"
        else:
            with pytest.raises(ConfigCoreVersionMismatched):
                Config.load(file_config.filename)

    @pytest.mark.parametrize(
        "core_version,is_compatible",
        [
            ("3.0.1", True),  # current version
            ("3.0.1.dev0", True),  # current dev version
            ("3.0.2", True),  # future but compatible
            ("3.0.2.dev0", True),  # dev future but compatible
            ("3.0.0", True),  # past but compatible
            ("3.0.0.dev0", True),  # dev past but compatible
            ("3.1.0", False),  # future but incompatible
            ("3.1.0.dev0", False),  # dev future but incompatible
            ("2.1.0", False),  # past but incompatible
            ("2.1.0.dev0", False),  # dev past but incompatible
        ],
    )
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
            assert Config.unique_sections[CoreSection.name]._core_version == "3.0.1"
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
        assert Config.unique_sections[CoreSection.name]._core_version == "3.0.1"
