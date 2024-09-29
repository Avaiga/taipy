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

from unittest.mock import patch

import pytest

from taipy.common.config import Config
from taipy.common.config.common.frequency import Frequency
from taipy.common.config.common.scope import Scope
from taipy.core import Orchestrator, taipy
from taipy.core._version._version_manager import _VersionManager
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.common._utils import _load_fct
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.exceptions.exceptions import NonExistingVersion
from taipy.core.job._job_manager import _JobManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.task._task_manager import _TaskManager


def test_orchestrator_cli_no_arguments():
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "development"
        assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_development_version()
        assert not Config.core.force
        orchestrator.stop()


def test_orchestrator_cli_development_mode():
    with patch("sys.argv", ["prog", "--development"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "development"
        assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_development_version()
        orchestrator.stop()


def test_orchestrator_cli_dev_mode():
    with patch("sys.argv", ["prog", "-dev"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "development"
        assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_development_version()
        orchestrator.stop()


def test_orchestrator_cli_experiment_mode():
    with patch("sys.argv", ["prog", "--experiment"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == _VersionManagerFactory._build_manager()._get_latest_version()
        assert not Config.core.force
        orchestrator.stop()


def test_orchestrator_cli_experiment_mode_with_version():
    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == "2.1"
        assert not Config.core.force
        orchestrator.stop()


def test_orchestrator_cli_experiment_mode_with_force_version(init_config):
    with patch("sys.argv", ["prog", "--experiment", "2.1", "--taipy-force"]):
        init_config()
        orchestrator = Orchestrator()
        orchestrator.run()
        assert Config.core.mode == "experiment"
        assert Config.core.version_number == "2.1"
        assert Config.core.force
        orchestrator.stop()


def test_dev_mode_clean_all_entities_of_the_latest_version():
    scenario_config = config_scenario()

    # Create a scenario in development mode
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)
        orchestrator.stop()

    # Initial assertion
    assert len(_DataManager._get_all(version_number="all")) == 2
    assert len(_TaskManager._get_all(version_number="all")) == 1
    assert len(_SequenceManager._get_all(version_number="all")) == 1
    assert len(_ScenarioManager._get_all(version_number="all")) == 1
    assert len(_CycleManager._get_all(version_number="all")) == 1
    assert len(_JobManager._get_all(version_number="all")) == 1

    # Create a new scenario in experiment mode
    with patch("sys.argv", ["prog", "--experiment"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)
        orchestrator.stop()

    # Assert number of entities in 2nd version
    assert len(_DataManager._get_all(version_number="all")) == 4
    assert len(_TaskManager._get_all(version_number="all")) == 2
    assert len(_SequenceManager._get_all(version_number="all")) == 2
    assert len(_ScenarioManager._get_all(version_number="all")) == 2
    # No new cycle is created since old dev version use the same cycle
    assert len(_CycleManager._get_all(version_number="all")) == 1
    assert len(_JobManager._get_all(version_number="all")) == 2

    # Run development mode again
    with patch("sys.argv", ["prog", "--development"]):
        orchestrator = Orchestrator()
        orchestrator.run()

        # The 1st dev version should be deleted run with development mode
        assert len(_DataManager._get_all(version_number="all")) == 2
        assert len(_TaskManager._get_all(version_number="all")) == 1
        assert len(_SequenceManager._get_all(version_number="all")) == 1
        assert len(_ScenarioManager._get_all(version_number="all")) == 1
        assert len(_CycleManager._get_all(version_number="all")) == 1
        assert len(_JobManager._get_all(version_number="all")) == 1

        # Submit new dev version
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)
        orchestrator.stop()

        # Assert number of entities with 1 dev version and 1 exp version
        assert len(_DataManager._get_all(version_number="all")) == 4
        assert len(_TaskManager._get_all(version_number="all")) == 2
        assert len(_SequenceManager._get_all(version_number="all")) == 2
        assert len(_ScenarioManager._get_all(version_number="all")) == 2
        assert len(_CycleManager._get_all(version_number="all")) == 1
        assert len(_JobManager._get_all(version_number="all")) == 2

        # Assert number of entities of the latest version only
        assert len(_DataManager._get_all(version_number="latest")) == 2
        assert len(_TaskManager._get_all(version_number="latest")) == 1
        assert len(_SequenceManager._get_all(version_number="latest")) == 1
        assert len(_ScenarioManager._get_all(version_number="latest")) == 1
        assert len(_JobManager._get_all(version_number="latest")) == 1

        # Assert number of entities of the development version only
        assert len(_DataManager._get_all(version_number="development")) == 2
        assert len(_TaskManager._get_all(version_number="development")) == 1
        assert len(_SequenceManager._get_all(version_number="development")) == 1
        assert len(_ScenarioManager._get_all(version_number="development")) == 1
        assert len(_JobManager._get_all(version_number="development")) == 1

        # Assert number of entities of an unknown version
        with pytest.raises(NonExistingVersion):
            assert _DataManager._get_all(version_number="foo")
        with pytest.raises(NonExistingVersion):
            assert _TaskManager._get_all(version_number="foo")
        with pytest.raises(NonExistingVersion):
            assert _SequenceManager._get_all(version_number="foo")
        with pytest.raises(NonExistingVersion):
            assert _ScenarioManager._get_all(version_number="foo")
        with pytest.raises(NonExistingVersion):
            assert _JobManager._get_all(version_number="foo")


def twice_doppelganger(a):
    return a * 2


def test_dev_mode_clean_all_entities_when_config_is_alternated():
    data_node_1_config = Config.configure_data_node(
        id="d1", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv", default_path="foo.csv")
    task_config = Config.configure_task("my_task", twice_doppelganger, data_node_1_config, data_node_2_config)
    scenario_config = Config.configure_scenario("my_scenario", [task_config], frequency=Frequency.DAILY)

    # Create a scenario in development mode with the doppelganger function
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)
        orchestrator.stop()

    # Delete the twice_doppelganger function
    # and clear cache of _load_fct() to simulate a new run
    del globals()["twice_doppelganger"]
    _load_fct.cache_clear()

    # Create a scenario in development mode with another function
    scenario_config = config_scenario()
    with patch("sys.argv", ["prog"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)
        orchestrator.stop()


def test_version_number_when_switching_mode():
    with patch("sys.argv", ["prog", "--development"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_1 = _VersionManager._get_latest_version()
        ver_dev = _VersionManager._get_development_version()
        assert ver_1 == ver_dev
        assert len(_VersionManager._get_all()) == 1
        orchestrator.stop()

    # Run with dev mode, the version number is the same
    with patch("sys.argv", ["prog", "--development"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_2 = _VersionManager._get_latest_version()
        assert ver_2 == ver_dev
        assert len(_VersionManager._get_all()) == 1
        orchestrator.stop()

    # When run with experiment mode, a new version is created
    with patch("sys.argv", ["prog", "--experiment"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_3 = _VersionManager._get_latest_version()
        assert ver_3 != ver_dev
        assert len(_VersionManager._get_all()) == 2
        orchestrator.stop()

    with patch("sys.argv", ["prog", "--experiment", "2.1"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_4 = _VersionManager._get_latest_version()
        assert ver_4 == "2.1"
        assert len(_VersionManager._get_all()) == 3
        orchestrator.stop()

    with patch("sys.argv", ["prog", "--experiment"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_5 = _VersionManager._get_latest_version()
        assert ver_5 != ver_3
        assert ver_5 != ver_4
        assert ver_5 != ver_dev
        assert len(_VersionManager._get_all()) == 4
        orchestrator.stop()

    # Run with dev mode, the version number is the same as the first dev version to override it
    with patch("sys.argv", ["prog", "--development"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_7 = _VersionManager._get_latest_version()
        assert ver_1 == ver_7
        assert len(_VersionManager._get_all()) == 4
        orchestrator.stop()


def test_force_override_experiment_version():
    scenario_config = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_1 = _VersionManager._get_latest_version()
        assert ver_1 == "1.0"
        # When create new experiment version, a development version entity is also created as a placeholder
        assert len(_VersionManager._get_all()) == 2  # 2 version include 1 experiment 1 development

        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)

        assert len(_DataManager._get_all()) == 2
        assert len(_TaskManager._get_all()) == 1
        assert len(_SequenceManager._get_all()) == 1
        assert len(_ScenarioManager._get_all()) == 1
        assert len(_CycleManager._get_all()) == 1
        assert len(_JobManager._get_all()) == 1
        orchestrator.stop()

    Config.configure_global_app(foo="bar")

    # Without --taipy-force parameter, a SystemExit will be raised
    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "--experiment", "1.0"]):
            orchestrator = Orchestrator()
            orchestrator.run()
    orchestrator.stop()

    # With --taipy-force parameter
    with patch("sys.argv", ["prog", "--experiment", "1.0", "--taipy-force"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        ver_2 = _VersionManager._get_latest_version()
        assert ver_2 == "1.0"
        assert len(_VersionManager._get_all()) == 2  # 2 version include 1 experiment 1 development

        # All entities from previous submit should be saved
        scenario = _ScenarioManager._create(scenario_config)
        taipy.submit(scenario)

        assert len(_DataManager._get_all()) == 4
        assert len(_TaskManager._get_all()) == 2
        assert len(_SequenceManager._get_all()) == 2
        assert len(_ScenarioManager._get_all()) == 2
        assert len(_CycleManager._get_all()) == 1
        assert len(_JobManager._get_all()) == 2
        orchestrator.stop()


def test_modified_job_configuration_dont_block_application_run(caplog, init_config):
    _ = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        orchestrator = Orchestrator()
        Config.configure_job_executions(mode="development")
        orchestrator.run()
        orchestrator.stop()
    init_config()
    _ = config_scenario()
    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        orchestrator = Orchestrator()
        Config.configure_job_executions(mode="standalone", max_nb_of_workers=3)
        orchestrator.run()
        error_message = str(caplog.text)
        assert 'JOB "mode" was modified' in error_message
        assert 'JOB "max_nb_of_workers" was added' in error_message
        orchestrator.stop()


def test_modified_config_properties_without_force(caplog, init_config):
    _ = config_scenario()

    with patch("sys.argv", ["prog", "--experiment", "1.0"]):
        orchestrator = Orchestrator()
        orchestrator.run()
        orchestrator.stop()

    init_config()

    _ = config_scenario_2()

    with pytest.raises(SystemExit):
        with patch("sys.argv", ["prog", "--experiment", "1.0"]):
            orchestrator = Orchestrator()
            orchestrator.run()
    orchestrator.stop()
    error_message = str(caplog.text)

    assert 'DATA_NODE "d3" was added' in error_message
    assert 'JOB "max_nb_of_workers" was added' in error_message

    assert 'DATA_NODE "d0" was removed' in error_message

    assert 'DATA_NODE "d2" has attribute "default_path" modified' in error_message
    assert 'CORE "root_folder" was modified' in error_message
    assert 'CORE "repository_type" was modified' in error_message
    assert 'JOB "mode" was modified' in error_message
    assert 'SCENARIO "my_scenario" has attribute "frequency" modified' in error_message
    assert 'SCENARIO "my_scenario" has attribute "tasks" modified' in error_message
    assert 'TASK "my_task" has attribute "inputs" modified' in error_message
    assert 'TASK "my_task" has attribute "function" modified' in error_message
    assert 'TASK "my_task" has attribute "outputs" modified' in error_message
    assert 'DATA_NODE "d2" has attribute "has_header" modified' in error_message
    assert 'DATA_NODE "d2" has attribute "exposed_type" modified' in error_message

    assert 'CORE "repository_properties" was added' in error_message


def twice(a):
    return a * 2


def config_scenario():
    Config.configure_data_node(id="d0")
    data_node_1_config = Config.configure_data_node(
        id="d1", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_2_config = Config.configure_data_node(id="d2", storage_type="csv", default_path="foo.csv")
    task_config = Config.configure_task("my_task", twice, data_node_1_config, data_node_2_config)
    scenario_config = Config.configure_scenario("my_scenario", [task_config], frequency=Frequency.DAILY)
    scenario_config.add_sequences({"my_sequence": [task_config]})

    return scenario_config


def double_twice(a):
    return a * 2, a * 2


def config_scenario_2():
    Config.configure_core(
        root_folder="foo_root",
        # Changing the "storage_folder" will fail since older versions are stored in older folder
        # storage_folder="foo_storage",
        repository_type="bar",
        repository_properties={"foo": "bar"},
    )
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=3)
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
    Config.configure_task("my_task", double_twice, data_node_3_config, [data_node_1_config, data_node_2_config])
    task_config_1 = Config.configure_task("my_task_1", double_twice, data_node_3_config, [data_node_2_config])
    # Modify properties of "my_scenario", where tasks is now my_task_1
    scenario_config = Config.configure_scenario("my_scenario", [task_config_1], frequency=Frequency.MONTHLY)
    scenario_config.add_sequences({"my_sequence": [task_config_1]})

    return scenario_config
