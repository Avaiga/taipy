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

from time import sleep
from unittest.mock import patch

import pytest

from src.taipy.core import Core
from src.taipy.core._version._cli._version_cli import _VersionCLI
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config


def test_delete_version(caplog, tmp_sqlite):
    Config.configure_global_app(repository_type="sql", repository_properties={"db_location": tmp_sqlite})

    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--development"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    with patch("sys.argv", ["prog", "--experiment", "1.1"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    with patch("sys.argv", ["prog", "--production", "1.1"]):
        Core().run()

    with patch("sys.argv", ["prog", "--experiment", "2.0"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    with patch("sys.argv", ["prog", "--production", "2.1"]):
        Core().run()

    all_versions = [version.id for version in _VersionManager._get_all()]
    production_version = _VersionManager._get_production_versions()
    assert len(all_versions) == 5
    assert len(production_version) == 2
    assert "1.0" in all_versions
    assert "1.1" in all_versions and "1.1" in production_version
    assert "2.0" in all_versions
    assert "2.1" in all_versions and "2.1" in production_version

    _VersionCLI.create_parser()
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "manage-versions", "--delete", "1.0"]):
            _VersionCLI.parse_arguments()

    assert "Successfully delete version 1.0." in caplog.text
    all_versions = [version.id for version in _VersionManager._get_all()]
    assert len(all_versions) == 4
    assert "1.0" not in all_versions

    # Test delete a non-existed version
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "manage-versions", "--delete", "non_exist_version"]):
            _VersionCLI.parse_arguments()
    assert "Version 'non_exist_version' does not exist." in caplog.text

    # Test delete production version will change the version from production to experiment
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "manage-versions", "--delete-production", "1.1"]):
            _VersionCLI.parse_arguments()

    assert "Successfully delete version 1.1 from production version list." in caplog.text
    all_versions = [version.id for version in _VersionManager._get_all()]
    production_version = _VersionManager._get_production_versions()
    assert len(all_versions) == 4
    assert "1.1" in all_versions and "1.1" not in production_version

    # Test delete a non-existed production version
    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "manage-versions", "--delete-production", "non_exist_version"]):
            _VersionCLI.parse_arguments()

    assert str(e.value) == "Version 'non_exist_version' is not a production version."


def test_list_version(capsys, tmp_sqlite):
    Config.configure_global_app(repository_type="sql", repository_properties={"db_location": tmp_sqlite})

    with patch("sys.argv", ["prog", "--development"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--experiment", "1.1"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--production", "1.1"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--experiment", "2.0"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        Core().run()
    sleep(0.05)
    with patch("sys.argv", ["prog", "--production", "2.1"]):
        Core().run()

    _VersionCLI.create_parser()
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "manage-versions", "--list"]):
            _VersionCLI.parse_arguments()

    out, _ = capsys.readouterr()
    version_list = str(out).strip().split("\n")
    assert len(version_list) == 6  # 5 versions with the header
    assert all(column in version_list[0] for column in ["Version number", "Mode", "Creation date"])
    assert all(column in version_list[1] for column in ["2.1", "Production", "latest"])
    assert all(column in version_list[2] for column in ["2.0", "Experiment"]) and "latest" not in version_list[2]
    assert all(column in version_list[3] for column in ["1.1", "Production"]) and "latest" not in version_list[3]
    assert all(column in version_list[4] for column in ["1.0", "Experiment"]) and "latest" not in version_list[4]
    assert "Development" in version_list[5] and "latest" not in version_list[5]


def twice(a):
    return a * 2


def config_scenario():
    data_node_1_config = Config.configure_data_node(
        id="d1", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv", default_path="foo.csv")
    task_config = Config.configure_task("my_task", twice, data_node_1_config, data_node_2_config)
    pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
    scenario_config = Config.configure_scenario("my_scenario", pipeline_config, frequency=Frequency.DAILY)

    return scenario_config
