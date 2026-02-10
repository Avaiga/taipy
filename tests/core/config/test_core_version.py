# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from unittest import mock

import pytest

from taipy.common.config import Config
from taipy.core import Orchestrator, taipy
from taipy.core._init_version import _read_version
from taipy.core.config.core_section import CoreSection
from taipy.core.exceptions import ConfigCoreVersionMismatched
from taipy.core.scenario._scenario_manager import _ScenarioManager
from tests.core.utils.named_temporary_file import NamedTemporaryFile

_MOCK_CORE_VERSION = "3.1.1"


def patch_core_version(mock_core_version: str):
    with mock.patch("taipy.core.config.core_section._read_version") as mock_read_version:
        mock_read_version.return_value = mock_core_version

    CoreSection._CURRENT_CORE_VERSION = mock_core_version
    Config._default_config._unique_sections[CoreSection.name] = CoreSection.default_config()
    Config._python_config._unique_sections[CoreSection.name] = CoreSection.default_config()


@pytest.fixture(scope="function", autouse=True)
def mock_core_version():
    patch_core_version(_MOCK_CORE_VERSION)

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
            """
        )
        Config.load(file_config.filename)
        assert Config.unique_sections[CoreSection.name]._core_version == _MOCK_CORE_VERSION

    def test_run_core_app_with_different_taipy_core_version_in_development_mode(self):
        with mock.patch("sys.argv", ["prog", "--development"]):
            run_application()

        # Run the application with a compatible version should NOT raise any error
        patch_core_version(f"{self.major}.{self.minor}.{self.patch}.dev0")
        with mock.patch("sys.argv", ["prog", "--development"]):
            run_application()

        # Run the application with an incompatible version in development mode should NOT raise an error
        patch_core_version(f"{self.major}.{int(self.minor) + 1}.{self.patch}.dev0")
        with mock.patch("sys.argv", ["prog", "--development"]):
            run_application()

    def test_run_core_app_with_different_taipy_core_version_in_experiment_mode(self, caplog):
        with mock.patch("sys.argv", ["prog", "--experiment", "1.0"]):
            run_application()

        # Run the application with a compatible version should not raise any error
        patch_core_version(f"{self.major}.{self.minor}.{int(self.patch) + 1}.dev0")
        with mock.patch("sys.argv", ["prog", "--experiment", "1.0"]):
            run_application()

        # Run the application with an incompatible version in experiment mode should raise SystemExit and log the error
        patch_core_version(f"{self.major}.{int(self.minor) + 1}.{self.patch}.dev0")
        with mock.patch("sys.argv", ["prog", "--experiment", "1.0"]):
            with pytest.raises(SystemExit):
                run_application()
        assert (
            f"The version {self.major}.{self.minor}.{self.patch} of Taipy's entities does not match version "
            f"of the Taipy Version management {self.major}.{int(self.minor) + 1}.{self.patch}.dev0"
        ) in caplog.text


def twice(a):
    return [a * 2]


def run_application():
    Config.configure_data_node(id="d0")
    data_node_1_config = Config.configure_data_node(id="d1", storage_type="pickle", default_data="abc")
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv")
    task_config = Config.configure_task("my_task", twice, data_node_1_config, data_node_2_config)
    scenario_config = Config.configure_scenario("my_scenario", [task_config])
    scenario_config.add_sequences({"my_sequence": [task_config]})

    orchestrator = Orchestrator()
    orchestrator.run()

    scenario = _ScenarioManager._create(scenario_config)
    taipy.submit(scenario)

    orchestrator.stop()
