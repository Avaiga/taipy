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

from datetime import datetime, timedelta

import pytest

from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core._version._version_manager import _VersionManager
from taipy.core.config.job_config import JobConfig
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.exceptions.exceptions import DeletingPrimaryScenario
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_id import ScenarioId
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.sequence.sequence import Sequence
from taipy.core.sequence.sequence_id import SequenceId
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_id import TaskId
from tests.core.conftest import init_managers


def test_set_and_get_scenario(cycle, init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()
    _OrchestratorFactory._build_dispatcher()

    scenario_id_1 = ScenarioId("scenario_id_1")
    scenario_1 = Scenario("scenario_name_1", [], {}, [], scenario_id_1)

    input_dn_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_dn_2 = InMemoryDataNode("bar", Scope.SCENARIO)
    additional_dn_2 = InMemoryDataNode("zyx", Scope.SCENARIO)
    task_name_2 = "task_2"
    task_2 = Task(task_name_2, {}, print, [input_dn_2], [output_dn_2], TaskId("task_id_2"))
    scenario_id_2 = ScenarioId("scenario_id_2")
    scenario_2 = Scenario(
        "scenario_name_2",
        [task_2],
        {},
        [additional_dn_2],
        scenario_id_2,
        datetime.now(),
        True,
        cycle,
        sequences={"sequence_2": {"tasks": [task_2]}},
    )

    additional_dn_3 = InMemoryDataNode("baz", Scope.SCENARIO)
    task_name_3 = "task_3"
    task_3 = Task(task_name_3, {}, print, id=TaskId("task_id_3"))
    scenario_3_with_same_id = Scenario(
        "scenario_name_3",
        [task_3],
        {},
        [additional_dn_3],
        scenario_id_1,
        datetime.now(),
        False,
        cycle,
        sequences={"sequence_3": {}},
    )

    # No existing scenario
    assert len(_ScenarioManager._get_all()) == 0
    assert _ScenarioManager._get(scenario_id_1) is None
    assert _ScenarioManager._get(scenario_1) is None
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save one scenario. We expect to have only one scenario stored
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_id_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).sequences) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).sequences) == 0
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    _TaskManager._set(task_2)
    _CycleManager._set(cycle)
    _ScenarioManager._set(scenario_2)
    _DataManager._set(additional_dn_2)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_id_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).sequences) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).sequences) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_id_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_id_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_id_2).sequences) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_2).sequences) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _ScenarioManager._get(scenario_id_2).cycle == cycle
    assert _ScenarioManager._get(scenario_2).cycle == cycle
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save the first scenario again. We expect nothing to change
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_id_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_id_1).sequences) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).tasks) == 0
    assert len(_ScenarioManager._get(scenario_1).additional_data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).data_nodes) == 0
    assert len(_ScenarioManager._get(scenario_1).sequences) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_id_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_id_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_id_2).sequences) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_2).sequences) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    _DataManager._set(additional_dn_3)
    _TaskManager._set(task_3)
    _TaskManager._set(scenario_2.tasks[task_name_2])
    _ScenarioManager._set(scenario_3_with_same_id)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_id_1).tasks) == 1
    assert len(_ScenarioManager._get(scenario_id_1).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_id_1).data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_id_1).sequences) == 1
    assert _ScenarioManager._get(scenario_id_1).cycle == cycle
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_1).tasks) == 1
    assert len(_ScenarioManager._get(scenario_1).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_1).data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_1).sequences) == 1
    assert _ScenarioManager._get(scenario_1).cycle == cycle
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_id_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_id_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_id_2).sequences) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).tasks) == 1
    assert len(_ScenarioManager._get(scenario_2).additional_data_nodes) == 1
    assert len(_ScenarioManager._get(scenario_2).data_nodes) == 3
    assert len(_ScenarioManager._get(scenario_2).sequences) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


def test_get_all_on_multiple_versions_environment(init_sql_repo):
    init_managers()

    # Create 5 scenarios with 2 versions each
    # Only version 1.0 has the scenario with config_id = "config_id_1"
    # Only version 2.0 has the scenario with config_id = "config_id_6"
    for version in range(1, 3):
        for i in range(5):
            _ScenarioManager._set(
                Scenario(f"config_id_{i+version}", [], {}, ScenarioId(f"id{i}_v{version}"), version=f"{version}.0")
            )

    _VersionManager._set_experiment_version("1.0")
    assert len(_ScenarioManager._get_all()) == 5
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_experiment_version("2.0")
    assert len(_ScenarioManager._get_all()) == 5
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1

    _VersionManager._set_development_version("1.0")
    assert len(_ScenarioManager._get_all()) == 5
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_1"}])) == 1
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "1.0", "config_id": "config_id_6"}])) == 0

    _VersionManager._set_development_version("2.0")
    assert len(_ScenarioManager._get_all()) == 5
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_1"}])) == 0
    assert len(_ScenarioManager._get_all_by(filters=[{"version": "2.0", "config_id": "config_id_6"}])) == 1


def test_create_scenario_does_not_modify_config(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    creation_date_1 = datetime.now()
    name_1 = "name_1"
    scenario_config = Config.configure_scenario("sc", None, None, Frequency.DAILY)

    _OrchestratorFactory._build_dispatcher()

    assert scenario_config.properties.get("name") is None
    assert len(scenario_config.properties) == 0

    scenario = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 1
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario.properties["foo"] = "bar"
    _ScenarioManager._set(scenario)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 2
    assert scenario.properties.get("foo") == "bar"
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1)
    assert scenario_2.name is None


def test_create_and_delete_scenario(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    creation_date_1 = datetime.now()
    creation_date_2 = creation_date_1 + timedelta(minutes=10)

    name_1 = "name_1"

    _ScenarioManager._delete_all()
    assert len(_ScenarioManager._get_all()) == 0

    scenario_config = Config.configure_scenario("sc", None, None, Frequency.DAILY)

    _OrchestratorFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert scenario_1.config_id == "sc"
    assert scenario_1.sequences == {}
    assert scenario_1.tasks == {}
    assert scenario_1.additional_data_nodes == {}
    assert scenario_1.data_nodes == {}
    assert scenario_1.cycle.frequency == Frequency.DAILY
    assert scenario_1.is_primary
    assert scenario_1.cycle.creation_date == creation_date_1
    assert scenario_1.cycle.start_date.date() == creation_date_1.date()
    assert scenario_1.cycle.end_date.date() == creation_date_1.date()
    assert scenario_1.creation_date == creation_date_1
    assert scenario_1.name == name_1
    assert scenario_1.properties["name"] == name_1
    assert scenario_1.tags == set()

    cycle_id_1 = scenario_1.cycle.id
    assert _CycleManager._get(cycle_id_1).id == cycle_id_1
    _ScenarioManager._delete(scenario_1.id)
    assert _ScenarioManager._get(scenario_1.id) is None
    assert _CycleManager._get(cycle_id_1) is None

    # Recreate scenario_1
    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_2)
    assert scenario_2.config_id == "sc"
    assert scenario_2.sequences == {}
    assert scenario_2.tasks == {}
    assert scenario_2.additional_data_nodes == {}
    assert scenario_2.data_nodes == {}
    assert scenario_2.cycle.frequency == Frequency.DAILY
    assert not scenario_2.is_primary
    assert scenario_2.cycle.creation_date == creation_date_1
    assert scenario_2.cycle.start_date.date() == creation_date_2.date()
    assert scenario_2.cycle.end_date.date() == creation_date_2.date()
    assert scenario_2.properties.get("name") is None
    assert scenario_2.tags == set()

    assert scenario_1 != scenario_2
    assert scenario_1.cycle == scenario_2.cycle

    assert len(_ScenarioManager._get_all()) == 2
    with pytest.raises(DeletingPrimaryScenario):
        _ScenarioManager._delete(
            scenario_1.id,
        )

    _ScenarioManager._delete(
        scenario_2.id,
    )
    assert len(_ScenarioManager._get_all()) == 1
    _ScenarioManager._delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 0


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_scenario_manager_only_creates_data_node_once(init_sql_repo):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    init_managers()

    # dn_1 ---> mult_by_2 ---> dn_2 ---> mult_by_3 ---> dn_6
    # dn_1 ---> mult_by_4 ---> dn_4

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.GLOBAL, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.CYCLE, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.CYCLE, default_data=0)
    dn_config_4 = Config.configure_data_node("qux", "in_memory", Scope.SCENARIO, default_data=0)
    task_mult_by_2_config = Config.configure_task("mult_by_2", mult_by_2, [dn_config_1], dn_config_2)
    task_mult_by_3_config = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    task_mult_by_4_config = Config.configure_task("mult_by_4", mult_by_4, [dn_config_1], dn_config_4)
    scenario_config = Config.configure_scenario(
        "awesome_scenario", [task_mult_by_2_config, task_mult_by_3_config, task_mult_by_4_config], None, Frequency.DAILY
    )
    scenario_config.add_sequences(
        {"by_6": [task_mult_by_2_config, task_mult_by_3_config], "by_4": [task_mult_by_4_config]}
    )

    _OrchestratorFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_SequenceManager._get_all()) == 0
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_CycleManager._get_all()) == 0

    scenario_1 = _ScenarioManager._create(scenario_config)

    assert len(_DataManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 3
    assert len(_SequenceManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 1
    assert scenario_1.foo.read() == 1
    assert scenario_1.bar.read() == 0
    assert scenario_1.baz.read() == 0
    assert scenario_1.qux.read() == 0
    assert scenario_1.by_6._get_sorted_tasks()[0][0].config_id == task_mult_by_2_config.id
    assert scenario_1.by_6._get_sorted_tasks()[1][0].config_id == task_mult_by_3_config.id
    assert scenario_1.by_4._get_sorted_tasks()[0][0].config_id == task_mult_by_4_config.id
    assert scenario_1.tasks.keys() == {task_mult_by_2_config.id, task_mult_by_3_config.id, task_mult_by_4_config.id}

    scenario_1_sorted_tasks = scenario_1._get_sorted_tasks()
    expected = [{task_mult_by_2_config.id, task_mult_by_4_config.id}, {task_mult_by_3_config.id}]
    for i, list_tasks_by_level in enumerate(scenario_1_sorted_tasks):
        assert set([t.config_id for t in list_tasks_by_level]) == expected[i]
    assert scenario_1.cycle.frequency == Frequency.DAILY

    _ScenarioManager._create(scenario_config)

    assert len(_DataManager._get_all()) == 5
    assert len(_TaskManager._get_all()) == 4
    assert len(_SequenceManager._get_all()) == 4
    assert len(_ScenarioManager._get_all()) == 2


def test_get_scenarios_by_config_id(init_sql_repo):
    init_managers()

    scenario_config_1 = Config.configure_scenario("s1", sequence_configs=[])
    scenario_config_2 = Config.configure_scenario("s2", sequence_configs=[])
    scenario_config_3 = Config.configure_scenario("s3", sequence_configs=[])

    s_1_1 = _ScenarioManager._create(scenario_config_1)
    s_1_2 = _ScenarioManager._create(scenario_config_1)
    s_1_3 = _ScenarioManager._create(scenario_config_1)
    assert len(_ScenarioManager._get_all()) == 3

    s_2_1 = _ScenarioManager._create(scenario_config_2)
    s_2_2 = _ScenarioManager._create(scenario_config_2)
    assert len(_ScenarioManager._get_all()) == 5

    s_3_1 = _ScenarioManager._create(scenario_config_3)
    assert len(_ScenarioManager._get_all()) == 6

    s1_scenarios = _ScenarioManager._get_by_config_id(scenario_config_1.id)
    assert len(s1_scenarios) == 3
    assert sorted([s_1_1.id, s_1_2.id, s_1_3.id]) == sorted([scenario.id for scenario in s1_scenarios])

    s2_scenarios = _ScenarioManager._get_by_config_id(scenario_config_2.id)
    assert len(s2_scenarios) == 2
    assert sorted([s_2_1.id, s_2_2.id]) == sorted([scenario.id for scenario in s2_scenarios])

    s3_scenarios = _ScenarioManager._get_by_config_id(scenario_config_3.id)
    assert len(s3_scenarios) == 1
    assert sorted([s_3_1.id]) == sorted([scenario.id for scenario in s3_scenarios])


def test_get_scenarios_by_config_id_in_multiple_versions_environment(init_sql_repo):
    init_managers()

    scenario_config_1 = Config.configure_scenario("s1", sequence_configs=[])
    scenario_config_2 = Config.configure_scenario("s2", sequence_configs=[])

    _VersionManager._set_experiment_version("1.0")
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_2)
    _ScenarioManager._create(scenario_config_2)

    assert len(_ScenarioManager._get_by_config_id(scenario_config_1.id)) == 3
    assert len(_ScenarioManager._get_by_config_id(scenario_config_2.id)) == 2

    _VersionManager._set_experiment_version("2.0")
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_1)
    _ScenarioManager._create(scenario_config_2)
    _ScenarioManager._create(scenario_config_2)

    assert len(_ScenarioManager._get_by_config_id(scenario_config_1.id)) == 3
    assert len(_ScenarioManager._get_by_config_id(scenario_config_2.id)) == 2
