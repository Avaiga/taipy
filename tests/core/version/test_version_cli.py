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
from src.taipy.core._version._version_cli import _VersioningCLI
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.exceptions.exceptions import NonExistingVersion
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.task._task_manager import _TaskManager
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config

from ...conftest import init_config


def test_version_cli_return_value():
    # Test default cli values
    _VersioningCLI._create_parser()
    mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "development"
    assert version_number == ""
    assert not force

    # Test Dev mode
    with patch("sys.argv", ["prog", "--development"]):
        mode, _, _, _ = _VersioningCLI._parse_arguments()
    assert mode == "development"

    with patch("sys.argv", ["prog", "-dev"]):
        mode, _, _, _ = _VersioningCLI._parse_arguments()
    assert mode == "development"

    # Test Experiment mode
    with patch("sys.argv", ["prog", "--experiment"]):
        mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "experiment"
    assert version_number == ""
    assert not force
    assert not clean_entities

    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "experiment"
    assert version_number == "2.1"
    assert not force
    assert not clean_entities

    with patch("sys.argv", ["prog", "--experiment", "2.1", "--force"]):
        mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "experiment"
    assert version_number == "2.1"
    assert force
    assert not clean_entities

    with patch("sys.argv", ["prog", "--experiment", "2.1", "--clean-entities"]):
        mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "experiment"
    assert version_number == "2.1"
    assert not force
    assert clean_entities

    # Test Production mode
    with patch("sys.argv", ["prog", "--production"]):
        mode, version_number, force, clean_entities = _VersioningCLI._parse_arguments()
    assert mode == "production"
    assert version_number == ""
    assert not force


def test_dev_mode_clean_all_entities_of_the_latest_version():
    scenario_config = config_scenario()

    # Create a scenario in development mode
    Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    # Initial assertion
    assert len(_DataManager._get_all(version_number="all")) == 2
    assert len(_TaskManager._get_all(version_number="all")) == 1
    assert len(_PipelineManager._get_all(version_number="all")) == 1
    assert len(_ScenarioManager._get_all(version_number="all")) == 1
    assert len(_CycleManager._get_all(version_number="all")) == 1
    assert len(_JobManager._get_all(version_number="all")) == 1

    # Create a new scenario in experiment mode
    with patch("sys.argv", ["prog", "--experiment"]):
        Core().run()
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    # Assert number of entities in 2nd version
    assert len(_DataManager._get_all(version_number="all")) == 4
    assert len(_TaskManager._get_all(version_number="all")) == 2
    assert len(_PipelineManager._get_all(version_number="all")) == 2
    assert len(_ScenarioManager._get_all(version_number="all")) == 2
    assert (
        len(_CycleManager._get_all(version_number="all")) == 1
    )  # No new cycle is created since old dev version use the same cycle
    assert len(_JobManager._get_all(version_number="all")) == 2

    # Run development mode again
    with patch("sys.argv", ["prog", "--development"]):
        Core().run()

    # The 1st dev version should be deleted run with development mode
    assert len(_DataManager._get_all(version_number="all")) == 2
    assert len(_TaskManager._get_all(version_number="all")) == 1
    assert len(_PipelineManager._get_all(version_number="all")) == 1
    assert len(_ScenarioManager._get_all(version_number="all")) == 1
    assert len(_CycleManager._get_all(version_number="all")) == 1
    assert len(_JobManager._get_all(version_number="all")) == 1

    # Submit new dev version
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    # Assert number of entities with 1 dev version and 1 exp version
    assert len(_DataManager._get_all(version_number="all")) == 4
    assert len(_TaskManager._get_all(version_number="all")) == 2
    assert len(_PipelineManager._get_all(version_number="all")) == 2
    assert len(_ScenarioManager._get_all(version_number="all")) == 2
    assert len(_CycleManager._get_all(version_number="all")) == 1
    assert len(_JobManager._get_all(version_number="all")) == 2

    # Assert number of entities of the latest version only
    assert len(_DataManager._get_all(version_number="latest")) == 2
    assert len(_TaskManager._get_all(version_number="latest")) == 1
    assert len(_PipelineManager._get_all(version_number="latest")) == 1
    assert len(_ScenarioManager._get_all(version_number="latest")) == 1
    assert len(_JobManager._get_all(version_number="latest")) == 1

    # Assert number of entities of the development version only
    assert len(_DataManager._get_all(version_number="development")) == 2
    assert len(_TaskManager._get_all(version_number="development")) == 1
    assert len(_PipelineManager._get_all(version_number="development")) == 1
    assert len(_ScenarioManager._get_all(version_number="development")) == 1
    assert len(_JobManager._get_all(version_number="development")) == 1

    # Assert number of entities of an unknown version
    with pytest.raises(NonExistingVersion):
        assert _DataManager._get_all(version_number="foo")
    with pytest.raises(NonExistingVersion):
        assert _TaskManager._get_all(version_number="foo")
    with pytest.raises(NonExistingVersion):
        assert _PipelineManager._get_all(version_number="foo")
    with pytest.raises(NonExistingVersion):
        assert _ScenarioManager._get_all(version_number="foo")
    with pytest.raises(NonExistingVersion):
        assert _JobManager._get_all(version_number="foo")


def test_version_number_when_switching_mode():
    with patch("sys.argv", ["prog", "--development"]):
        Core().run()
    ver_1 = _VersionManager._get_latest_version()
    ver_dev = _VersionManager._get_development_version()
    assert ver_1 == ver_dev
    assert len(_VersionManager._get_all()) == 1

    # Run with dev mode, the version number is the same
    with patch("sys.argv", ["prog", "--development"]):
        Core().run()
    ver_2 = _VersionManager._get_latest_version()
    assert ver_2 == ver_dev
    assert len(_VersionManager._get_all()) == 1

    # When run with experiment mode, a new version is created
    with patch("sys.argv", ["prog", "--experiment"]):
        Core().run()
    ver_3 = _VersionManager._get_latest_version()
    assert ver_3 != ver_dev
    assert len(_VersionManager._get_all()) == 2

    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        Core().run()
    ver_4 = _VersionManager._get_latest_version()
    assert ver_4 == "2.1"
    assert len(_VersionManager._get_all()) == 3

    with patch("sys.argv", ["prog", "--experiment"]):
        Core().run()
    ver_5 = _VersionManager._get_latest_version()
    assert ver_5 != ver_3
    assert ver_5 != ver_4
    assert ver_5 != ver_dev
    assert len(_VersionManager._get_all()) == 4

    # When run with production mode, the latest version is used as production
    with patch("sys.argv", ["prog", "--production"]):
        Core().run()
    ver_6 = _VersionManager._get_latest_version()
    production_versions = _VersionManager._get_production_version()
    assert ver_6 == ver_5
    assert production_versions == [ver_6]
    assert len(_VersionManager._get_all()) == 4

    # When run with production mode, the "2.1" version is used as production
    with patch("sys.argv", ["prog", "--production", "2.1"]):
        Core().run()
    ver_7 = _VersionManager._get_latest_version()
    production_versions = _VersionManager._get_production_version()
    assert ver_7 == "2.1"
    assert production_versions == [ver_6, ver_7]
    assert len(_VersionManager._get_all()) == 4

    # Run with dev mode, the version number is the same as the first dev version to overide it
    with patch("sys.argv", ["prog", "--development"]):
        Core().run()
    ver_7 = _VersionManager._get_latest_version()
    assert ver_1 == ver_7
    assert len(_VersionManager._get_all()) == 4


def test_production_mode_load_all_entities_from_previous_production_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--production"]):
        Core().run()
    production_ver_1 = _VersionManager._get_latest_version()
    assert _VersionManager._get_production_version() == [production_ver_1]
    # When run production mode on a new app, a dev version is created alongside
    assert _VersionManager._get_development_version() not in _VersionManager._get_production_version()
    assert len(_VersionManager._get_all()) == 2

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    with patch("sys.argv", ["prog", "--production", "2.0"]):
        Core().run()
    production_ver_2 = _VersionManager._get_latest_version()
    assert _VersionManager._get_production_version() == [production_ver_1, production_ver_2]
    assert len(_VersionManager._get_all()) == 3

    # All entities from previous production version should be saved
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 2


def test_force_override_experiment_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        Core().run()
    ver_1 = _VersionManager._get_latest_version()
    assert ver_1 == "1.0"
    # When create new experiment version, a development version entity is also created as a placeholder
    assert len(_VersionManager._get_all()) == 2  # 2 version include 1 experiment 1 development

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    # Update Config singleton to simulate conflict Config between versions
    Config.unblock_update()
    Config.configure_global_app(clean_entities_enabled=True)

    # Without --force parameter, a SystemExit will be raised
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "--experiment", "1.0"]):
            Core().run()

    # With --force parameter
    with patch("sys.argv", ["prog", "--experiment", "1.0", "--force"]):
        Core().run()
    ver_2 = _VersionManager._get_latest_version()
    assert ver_2 == "1.0"
    assert len(_VersionManager._get_all()) == 2  # 2 version include 1 experiment 1 development

    # All entities from previous submit should be saved
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 2


def test_force_override_production_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--production", "1.0"]):
        Core().run()
    ver_1 = _VersionManager._get_latest_version()
    production_versions = _VersionManager._get_production_version()
    assert ver_1 == "1.0"
    assert production_versions == ["1.0"]
    # When create new production version, a development version entity is also created as a placeholder
    assert len(_VersionManager._get_all()) == 2  # 2 version include 1 production 1 development

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    # Update Config singleton to simulate conflict Config between versions
    Config.unblock_update()
    Config.configure_global_app(clean_entities_enabled=True)

    # Without --force parameter, a SystemExit will be raised
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "--production", "1.0"]):
            Core().run()

    # With --force parameter
    with patch("sys.argv", ["prog", "--production", "1.0", "--force"]):
        Core().run()
    ver_2 = _VersionManager._get_latest_version()
    assert ver_2 == "1.0"
    assert len(_VersionManager._get_all()) == 2  # 2 version include 1 production 1 development

    # All entities from previous submit should be saved
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 2


def test_clean_experiment_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        Core().run()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    with patch("sys.argv", ["prog", "--experiment", "1.0", "--clean-entities"]):
        Core().run()

    # All entities from previous submit should be cleaned and re-created
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1


def test_clean_production_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--production", "1.0"]):
        Core().run()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    with patch("sys.argv", ["prog", "--production", "1.0", "--clean-entities"]):
        Core().run()

    # All entities from previous submit should be cleaned and re-created
    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario)

    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1


def test_delete_version():
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
    production_version = _VersionManager._get_production_version()
    assert len(all_versions) == 5
    assert len(production_version) == 2
    assert "1.0" in all_versions
    assert "1.1" in all_versions and "1.1" in production_version
    assert "2.0" in all_versions
    assert "2.1" in all_versions and "2.1" in production_version

    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "--delete-version", "1.0"]):
            Core().run()
    assert str(e.value) == "Successfully delete version 1.0."
    all_versions = [version.id for version in _VersionManager._get_all()]
    assert len(all_versions) == 4
    assert "1.0" not in all_versions

    # Test delete production version will change the version from production to experiment
    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "--delete-production-version", "1.1"]):
            Core().run()
    assert str(e.value) == "Successfully delete version 1.1 from production version list."
    all_versions = [version.id for version in _VersionManager._get_all()]
    production_version = _VersionManager._get_production_version()
    assert len(all_versions) == 4
    assert "1.1" in all_versions and "1.1" not in production_version

    # Test delete a wrong production version
    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "--delete-production-version", "non_exist_version"]):
            Core().run()
    assert str(e.value) == "Version non_exist_version is not a production version."


def test_list_version():
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

    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "--list-versions"]):
            Core().run()

    version_list = str(e.value).strip().split("\n")
    assert len(version_list) == 6  # 5 versions with the header
    assert all(column in version_list[0] for column in ["Version number", "Mode", "Creation date"])
    assert all(column in version_list[1] for column in ["2.1", "Production", "latest"])
    assert all(column in version_list[2] for column in ["2.0", "Experiment"]) and "latest" not in version_list[2]
    assert all(column in version_list[3] for column in ["1.1", "Production"]) and "latest" not in version_list[3]
    assert all(column in version_list[4] for column in ["1.0", "Experiment"]) and "latest" not in version_list[4]
    assert "Development" in version_list[5] and "latest" not in version_list[5]


def test_modify_config_properties_without_force():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        Core().run()
        scenario = _ScenarioManager._create(scenario_config)
        _ScenarioManager._submit(scenario)

    init_config()

    scenario_config_2 = config_scenario_2()

    with pytest.raises(SystemExit) as e:
        with patch("sys.argv", ["prog", "--experiment", "1.0"]):
            Core().run()
            scenario = _ScenarioManager._create(scenario_config_2)
            _ScenarioManager._submit(scenario)
    error_message = str(e.value)

    assert 'DATA_NODE "d3" was added' in error_message

    assert 'DATA_NODE "d0" was removed' in error_message

    assert 'DATA_NODE "d2" has attribute "default_path" modified' in error_message
    assert 'Global Configuration "root_folder" was modified' in error_message
    assert 'Global Configuration "clean_entities_enabled" was modified' in error_message
    assert 'Global Configuration "repository_type" was modified' in error_message
    assert 'JOB "mode" was modified' in error_message
    assert 'JOB "max_nb_of_workers" was modified' in error_message
    assert 'PIPELINE "my_pipeline" has attribute "tasks" modified' in error_message
    assert 'SCENARIO "my_scenario" has attribute "frequency" modified' in error_message
    assert 'SCENARIO "my_scenario" has attribute "pipelines" modified' in error_message
    assert 'TASK "my_task" has attribute "inputs" modified' in error_message
    assert 'TASK "my_task" has attribute "function" modified' in error_message
    assert 'TASK "my_task" has attribute "outputs" modified' in error_message
    assert 'DATA_NODE "d2" has attribute "has_header" modified' in error_message
    assert 'DATA_NODE "d2" has attribute "exposed_type" modified' in error_message

    assert 'Global Configuration "repository_properties" was added' in error_message


def twice(a):
    return a * 2


def config_scenario():
    Config.configure_data_node(id="d0")
    data_node_1_config = Config.configure_data_node(
        id="d1", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv", default_path="foo.csv")
    task_config = Config.configure_task("my_task", twice, data_node_1_config, data_node_2_config)
    pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
    scenario_config = Config.configure_scenario("my_scenario", pipeline_config, frequency=Frequency.DAILY)

    return scenario_config


def double_twice(a):
    return a * 2, a * 2


def config_scenario_2():
    Config.configure_global_app(
        root_folder="foo_root",
        # Changing the "storage_folder" will fail since older versions are stored in older folder
        # storage_folder="foo_storage",
        clean_entities_enabled=True,
        repository_type="bar",
        repository_properties={"foo": "bar"},
    )
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=5)
    data_node_1_config = Config.configure_data_node(
        id="d1", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
    )
    # Modify properties of "d2"
    data_node_2_config = Config.configure_data_node(
        id="d2", storage_type="csv", default_path="bar.csv", has_header=False, exposed_type="numpy"
    )
    # Add new data node "d3"
    data_node_3_config = Config.configure_data_node(
        id="d3", storage_type="csv", default_path="baz.csv", has_header=False, exposed_type="numpy"
    )
    # Modify properties of "my_task", including the function and outputs list
    task_config = Config.configure_task(
        "my_task", double_twice, data_node_3_config, [data_node_1_config, data_node_2_config]
    )
    # Modify properties of "my_pipeline", where tasks is now a list
    pipeline_config = Config.configure_pipeline("my_pipeline", [task_config, task_config])
    # Modify properties of "my_scenario", where pipelines is now a list
    scenario_config = Config.configure_scenario(
        "my_scenario", [pipeline_config, pipeline_config], frequency=Frequency.MONTHLY
    )

    return scenario_config
