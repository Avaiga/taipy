# Copyright 2022 Avaiga Private Limited
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
from click.testing import CliRunner

from src.taipy.core._version._version_cli import version_cli
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.task._task_manager import _TaskManager
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config

from ..utils.core_service_for_test import CoreForTest


def test_version_cli_return_value():
    runner = CliRunner()

    # Test default cli values
    result = runner.invoke(version_cli, standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "development"
    assert version_number is None
    assert not override

    # Test Dev mode
    result = runner.invoke(version_cli, ["--development"], standalone_mode=False)
    mode, _, _ = result.return_value
    assert mode == "development"

    result = runner.invoke(version_cli, ["--dev"], standalone_mode=False)
    mode, _, _ = result.return_value
    assert mode == "development"

    result = runner.invoke(version_cli, ["-d"], standalone_mode=False)
    mode, _, _ = result.return_value
    assert mode == "development"

    # Test Experiment mode
    result = runner.invoke(version_cli, ["--experiment"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "experiment"
    assert version_number is None
    assert not override

    result = runner.invoke(version_cli, ["-e"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "experiment"
    assert version_number is None
    assert not override

    result = runner.invoke(version_cli, ["-e", "--version-number", "2.1"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "experiment"
    assert version_number == "2.1"
    assert not override

    result = runner.invoke(version_cli, ["-e", "--version-number", "2.1", "--override"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "experiment"
    assert version_number == "2.1"
    assert override

    # Test Production mode
    result = runner.invoke(version_cli, ["--production"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "production"
    assert version_number is None
    assert not override

    result = runner.invoke(version_cli, ["-p"], standalone_mode=False)
    mode, version_number, override = result.return_value
    assert mode == "production"
    assert version_number is None
    assert not override


def test_dev_mode_clean_all_entities_of_the_current_version():
    core = CoreForTest()

    # Create a scenario in development mode
    core.run(parameters=["--development"])
    submit_scenario()

    # Initial assertion
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    # Create a new scenario in experiment mode
    core.run(parameters=["--experiment"])
    submit_scenario()

    # Assert number of entities in 2nd version
    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1  # No new cycle is created since old dev version use the same cycle
    assert len(_JobManager._get_all()) == 2

    # Run development mode again
    core.run(parameters=["--development"])

    # The 1st dev version should be deleted run with development mode
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    # Submit new dev version
    submit_scenario()

    # Assert number of entities with 1 dev version and 1 exp version
    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 2


def test_version_number_when_switching_mode():
    core = CoreForTest()

    core.run(parameters=["--development"])
    ver_1 = _VersionManager.get_current_version()
    assert len(_VersionManager._get_all()) == 1

    # Run with dev mode, the version number is the same
    core.run(parameters=["--development"])
    ver_2 = _VersionManager.get_current_version()
    assert ver_1 == ver_2
    assert len(_VersionManager._get_all()) == 1

    # When run with experiment mode, a new version is created
    core.run(parameters=["--experiment"])
    ver_3 = _VersionManager.get_current_version()
    assert ver_1 != ver_3
    assert len(_VersionManager._get_all()) == 2

    core.run(parameters=["--experiment"])
    ver_4 = _VersionManager.get_current_version()
    assert ver_1 != ver_4
    assert ver_3 != ver_4
    assert len(_VersionManager._get_all()) == 3

    core.run(parameters=["--experiment", "--version-number", "2.1"])
    ver_5 = _VersionManager.get_current_version()
    assert ver_5 == "2.1"
    assert len(_VersionManager._get_all()) == 4

    # When run with production mode, "production" version is created
    core.run(parameters=["--production"])
    ver_6 = _VersionManager.get_current_version()
    assert ver_6 == "production"
    assert len(_VersionManager._get_all()) == 5

    # Run with dev mode, the version number is the same as the first dev version to overide it
    core.run(parameters=["--development"])
    ver_7 = _VersionManager.get_current_version()
    assert ver_1 == ver_7
    assert len(_VersionManager._get_all()) == 5


def test_production_mode_save_all_entities():
    core = CoreForTest()

    core.run(parameters=["--production"])
    ver = _VersionManager.get_current_version()
    assert ver == "production"
    assert len(_VersionManager._get_all()) == 1

    submit_scenario()
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    core.run(parameters=["--production"])
    ver = _VersionManager.get_current_version()
    assert ver == "production"
    assert len(_VersionManager._get_all()) == 1

    # All entities from previous submit should be saved
    submit_scenario()
    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 2


def test_override_experiment_version():
    core = CoreForTest()

    core.run(parameters=["--experiment", "--version-number", "2.1"])
    ver_1 = _VersionManager.get_current_version()
    assert ver_1 == "2.1"
    assert len(_VersionManager._get_all()) == 1

    submit_scenario()
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    # Without --override parameter
    with pytest.raises(SystemExit) as e:
        core.run(parameters=["--experiment", "--version-number", "2.1"])
    assert str(e.value) == "Version 2.1 already exists."

    # With --override parameter
    core.run(parameters=["--experiment", "--version-number", "2.1", "--override"])
    ver_2 = _VersionManager.get_current_version()
    assert ver_2 == "2.1"
    assert len(_VersionManager._get_all()) == 1

    # The number of entities should not change
    submit_scenario()
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1


def task_test(a):
    return a


def submit_scenario():
    # Unblock for test
    Config.unblock_update()

    data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
    data_node_2_config = Config.configure_data_node(
        id="d2", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
    )
    task_config = Config.configure_task(
        "my_task", task_test, data_node_1_config, data_node_2_config, scope=Scope.SCENARIO
    )
    pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
    scenario_config = Config.configure_scenario("my_scenario", pipeline_config, frequency=Frequency.DAILY)

    scenario = _ScenarioManager._create(scenario_config)

    _ScenarioManager._submit(scenario)
