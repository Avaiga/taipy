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

import multiprocessing
from unittest.mock import patch

from src.taipy.config.config import Config
from src.taipy.core import Core, taipy
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from tests.core.conftest import init_config
from tests.core.utils import assert_true_after_time

m = multiprocessing.Manager()


def twice(a):
    return a * 2


def triple(a):
    return a * 3


def migrate_pickle_path(dn):
    dn.path = "bar.pkl"
    return dn


def migrate_skippable_task(task):
    task.skippable = True
    return task


def migrate_foo_scenario(scenario):
    scenario.properties["foo"] = "bar"
    return scenario


def test_migrate_datanode():
    scenario_v1 = submit_v1()

    init_config()
    Config.add_migration_function("2.0", "d1", migrate_pickle_path)

    submit_v2()
    v1 = taipy.get(scenario_v1.id)
    assert v1.d1.version == "2.0"
    assert v1.d1.path == "bar.pkl"


def test_migrate_datanode_in_standalone_mode():
    scenario_v1 = submit_v1()

    init_config()
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    Config.add_migration_function("2.0", "d1", migrate_pickle_path)

    scenario_cfg_v2 = config_scenario_v2()
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
        scenario_v2 = _ScenarioManager._create(scenario_cfg_v2)
        jobs = _ScenarioManager._submit(scenario_v2)
        v1 = taipy.get(scenario_v1.id)
        assert v1.d1.version == "2.0"
        assert v1.d1.path == "bar.pkl"
        assert_true_after_time(jobs[0].is_completed)
        core.stop()


def test_migrate_task():
    scenario_v1 = submit_v1()

    init_config()
    Config.add_migration_function("2.0", "my_task", migrate_skippable_task)

    submit_v2()
    v1 = taipy.get(scenario_v1.id)
    assert v1.my_task.version == "2.0"
    assert v1.my_task.skippable is True


def test_migrate_task_in_standalone_mode():
    scenario_v1 = submit_v1()

    init_config()
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    Config.add_migration_function("2.0", "my_task", migrate_skippable_task)

    scenario_cfg_v2 = config_scenario_v2()
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
        scenario_v2 = _ScenarioManager._create(scenario_cfg_v2)
        jobs = _ScenarioManager._submit(scenario_v2)
        v1 = taipy.get(scenario_v1.id)
        assert v1.my_task.version == "2.0"
        assert v1.my_task.skippable is True
        assert_true_after_time(jobs[0].is_completed)
        core.stop()


def test_migrate_scenario():
    scenario_v1 = submit_v1()

    init_config()
    Config.add_migration_function("2.0", "my_scenario", migrate_foo_scenario)

    submit_v2()
    v1 = taipy.get(scenario_v1.id)
    assert v1.version == "2.0"
    assert v1.properties["foo"] == "bar"


def test_migrate_scenario_in_standalone_mode():
    scenario_v1 = submit_v1()

    init_config()
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    Config.add_migration_function("2.0", "my_scenario", migrate_foo_scenario)

    scenario_cfg_v2 = config_scenario_v2()
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
        scenario_v2 = _ScenarioManager._create(scenario_cfg_v2)
        jobs = _ScenarioManager._submit(scenario_v2)
        v1 = taipy.get(scenario_v1.id)
        assert v1.version == "2.0"
        assert v1.properties["foo"] == "bar"
        assert_true_after_time(jobs[0].is_completed)
        core.stop()


def test_migrate_all_entities():
    scenario_v1 = submit_v1()

    init_config()
    Config.add_migration_function("2.0", "d1", migrate_pickle_path)
    Config.add_migration_function("2.0", "my_task", migrate_skippable_task)
    Config.add_migration_function("2.0", "my_scenario", migrate_foo_scenario)

    submit_v2()
    v1 = taipy.get(scenario_v1.id)

    assert v1.d1.version == "2.0"
    assert v1.my_task.version == "2.0"

    assert v1.d1.path == "bar.pkl"
    assert v1.my_task.skippable is True
    assert v1.properties["foo"] == "bar"


def test_migrate_all_entities_in_standalone_mode():
    scenario_v1 = submit_v1()

    init_config()
    Config.configure_job_executions(mode="standalone", max_nb_of_workers=2)
    Config.add_migration_function("2.0", "my_scenario", migrate_foo_scenario)

    scenario_cfg_v2 = config_scenario_v2()
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
        scenario_v2 = _ScenarioManager._create(scenario_cfg_v2)
        jobs = _ScenarioManager._submit(scenario_v2)
        v1 = taipy.get(scenario_v1.id)
        assert v1.version == "2.0"
        assert v1.properties["foo"] == "bar"
        assert_true_after_time(jobs[0].is_completed)
        core.stop()


def test_migrate_compatible_version():
    scenario_cfg = config_scenario_v1()
    # Production 1.0
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()

        scenario_v1 = _ScenarioManager._create(scenario_cfg)
        _ScenarioManager._submit(scenario_v1)

        assert scenario_v1.d2.read() == 2
        assert len(_DataManager._get_all(version_number="all")) == 2
        core.stop()

    init_config()
    scenario_cfg = config_scenario_v1()

    # Production 2.0 is a compatible version
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()

        scenario_v2 = _ScenarioManager._create(scenario_cfg)
        _ScenarioManager._submit(scenario_v2)

        assert scenario_v2.d2.read() == 2
        assert len(_DataManager._get_all(version_number="all")) == 4
        core.stop()

    init_config()

    # Production 2.1
    Config.add_migration_function(
        target_version="2.1",
        config="d1",
        migration_fct=migrate_pickle_path,
    )
    scenario_cfg_v2_1 = config_scenario_v2()

    with patch("sys.argv", ["prog", "--production", "2.1"]):
        core = Core()
        core.run()
        scenario_v2_1 = _ScenarioManager._create(scenario_cfg_v2_1)
        _ScenarioManager._submit(scenario_v2_1)
        core.stop()

    assert scenario_v2_1.d2.read() == 6
    assert len(_DataManager._get_all(version_number="all")) == 6

    v1 = taipy.get(scenario_v1.id)
    assert v1.d1.version == "2.1"
    assert v1.d1.path == "bar.pkl"

    v2 = taipy.get(scenario_v2.id)
    assert v2.d1.version == "2.1"
    assert v2.d1.path == "bar.pkl"


def submit_v1():
    scenario_cfg_v1 = config_scenario_v1()
    with patch("sys.argv", ["prog", "--production", "1.0"]):
        core = Core()
        core.run()
        scenario_v1 = _ScenarioManager._create(scenario_cfg_v1)
        _ScenarioManager._submit(scenario_v1)
        core.stop()
    return scenario_v1


def submit_v2():
    scenario_cfg_v2 = config_scenario_v2()
    with patch("sys.argv", ["prog", "--production", "2.0"]):
        core = Core()
        core.run()
        scenario_v2 = _ScenarioManager._create(scenario_cfg_v2)
        _ScenarioManager._submit(scenario_v2)
        core.stop()
    return scenario_v2


def config_scenario_v1():
    dn1 = Config.configure_pickle_data_node(id="d1", default_data=1)
    dn2 = Config.configure_pickle_data_node(id="d2")
    task_cfg = Config.configure_task("my_task", twice, dn1, dn2)
    scenario_cfg = Config.configure_scenario("my_scenario", [task_cfg])
    scenario_cfg.add_sequences({"my_sequence": [task_cfg]})
    return scenario_cfg


def config_scenario_v2():
    dn1 = Config.configure_pickle_data_node(id="d1", default_data=2)
    dn2 = Config.configure_pickle_data_node(id="d2")
    task_cfg = Config.configure_task("my_task", triple, dn1, dn2)
    scenario_cfg = Config.configure_scenario("my_scenario", [task_cfg])
    scenario_cfg.add_sequences({"my_scenario": [task_cfg]})
    return scenario_cfg
