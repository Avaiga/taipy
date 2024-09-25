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

from datetime import datetime, timedelta
from typing import Callable, Iterable, Optional
from unittest.mock import ANY, patch

import freezegun
import pytest

from taipy.common.config.common.frequency import Frequency
from taipy.common.config.common.scope import Scope
from taipy.common.config.config import Config
from taipy.core import Job
from taipy.core import taipy as tp
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._version._version_manager import _VersionManager
from taipy.core.common import _utils
from taipy.core.common._utils import _Subscriber
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.exceptions.exceptions import (
    DeletingPrimaryScenario,
    DifferentScenarioConfigs,
    InsufficientScenarioToCompare,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
    NonExistingTask,
    SequenceTaskConfigDoesNotExistInSameScenarioConfig,
    UnauthorizedTagError,
)
from taipy.core.job._job_manager import _JobManager
from taipy.core.reason import WrongConfigType
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_id import ScenarioId
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task
from taipy.core.task.task_id import TaskId
from tests.core.utils.NotifyMock import NotifyMock


def test_set_and_get_scenario(cycle):
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


def test_raise_sequence_task_configs_not_in_scenario_config():
    data_node = Config.configure_pickle_data_node("temp")
    task_config_1 = Config.configure_task("task_1", print, output=[data_node])
    task_config_2 = Config.configure_task("task_2", print, input=[data_node])
    scenario_config_1 = Config.configure_scenario("scenario_1")
    scenario_config_1.add_sequences({"sequence_0": []})

    _ScenarioManager._create(scenario_config_1)

    scenario_config_1.add_sequences({"sequence_1": [task_config_1]})
    with pytest.raises(SequenceTaskConfigDoesNotExistInSameScenarioConfig) as err:
        _ScenarioManager._create(scenario_config_1)
    assert err.value.args == ([task_config_1.id], "sequence_1", scenario_config_1.id)

    scenario_config_1._tasks = [task_config_1]
    _ScenarioManager._create(scenario_config_1)

    scenario_config_1.add_sequences({"sequence_2": [task_config_1]})
    _ScenarioManager._create(scenario_config_1)

    scenario_config_1.add_sequences({"sequence_3": [task_config_1, task_config_2]})
    with pytest.raises(SequenceTaskConfigDoesNotExistInSameScenarioConfig) as err:
        _ScenarioManager._create(scenario_config_1)
    assert err.value.args == ([task_config_2.id], "sequence_3", scenario_config_1.id)

    scenario_config_1._tasks = [task_config_1, task_config_2]
    _ScenarioManager._create(scenario_config_1)


def test_get_all_on_multiple_versions_environment():
    # Create 5 scenarios with 2 versions each
    # Only version 1.0 has the scenario with config_id = "config_id_1"
    # Only version 2.0 has the scenario with config_id = "config_id_6"
    for version in range(1, 3):
        for i in range(5):
            _ScenarioManager._set(
                Scenario(f"config_id_{i+version}", [], {}, [], ScenarioId(f"id{i}_v{version}"), version=f"{version}.0")
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


def test_create_scenario_does_not_modify_config():
    creation_date_1 = datetime.now()
    name_1 = "name_1"
    scenario_config = Config.configure_scenario("sc", None, None, Frequency.DAILY)
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


def test_create_and_delete_scenario():
    creation_date_1 = datetime.now()
    creation_date_2 = creation_date_1 + timedelta(minutes=10)

    name_1 = "name_1"

    _ScenarioManager._delete_all()
    assert len(_ScenarioManager._get_all()) == 0

    scenario_config = Config.configure_scenario("sc", None, None, Frequency.DAILY)

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


def test_can_create():
    dn_config = Config.configure_in_memory_data_node("dn", 10)
    task_config = Config.configure_task("task", print, [dn_config])
    scenario_config = Config.configure_scenario("sc", {task_config}, [], Frequency.DAILY)

    reasons = _ScenarioManager._can_create()
    assert bool(reasons) is True
    assert reasons._reasons == {}

    reasons = _ScenarioManager._can_create(scenario_config)
    assert bool(reasons) is True
    assert reasons._reasons == {}
    _ScenarioManager._create(scenario_config)

    reasons = _ScenarioManager._can_create(task_config)
    assert bool(reasons) is False
    assert reasons._reasons[task_config.id] == {WrongConfigType(task_config.id, ScenarioConfig.__name__)}
    assert str(list(reasons._reasons[task_config.id])[0]) == 'Object "task" must be a valid ScenarioConfig'
    with pytest.raises(AttributeError):
        _ScenarioManager._create(task_config)

    reasons = _ScenarioManager._can_create(1)
    assert bool(reasons) is False
    assert reasons._reasons["1"] == {WrongConfigType(1, ScenarioConfig.__name__)}
    assert str(list(reasons._reasons["1"])[0]) == 'Object "1" must be a valid ScenarioConfig'
    with pytest.raises(AttributeError):
        _ScenarioManager._create(1)


def test_is_deletable():
    assert len(_ScenarioManager._get_all()) == 0
    scenario_config = Config.configure_scenario("sc", None, None, Frequency.DAILY)
    creation_date = datetime.now()
    scenario_1_primary = _ScenarioManager._create(scenario_config, creation_date=creation_date, name="1")
    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date, name="2")

    rc = _ScenarioManager._is_deletable("some_scenario")
    assert not rc
    assert "Entity some_scenario does not exist in the repository." in rc.reasons

    assert len(_ScenarioManager._get_all()) == 2
    assert scenario_1_primary.is_primary
    assert not _ScenarioManager._is_deletable(scenario_1_primary)
    assert not _ScenarioManager._is_deletable(scenario_1_primary.id)
    assert not scenario_2.is_primary
    assert _ScenarioManager._is_deletable(scenario_2)
    assert _ScenarioManager._is_deletable(scenario_2.id)

    _ScenarioManager._hard_delete(scenario_2.id)
    del scenario_2

    assert len(_ScenarioManager._get_all()) == 1
    assert scenario_1_primary.is_primary
    assert _ScenarioManager._is_deletable(scenario_1_primary)
    assert _ScenarioManager._is_deletable(scenario_1_primary.id)


def test_assign_scenario_as_parent_of_task_and_additional_data_nodes():
    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.GLOBAL)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.GLOBAL)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.SCENARIO)
    additional_dn_config_1 = Config.configure_data_node("additional_dn_1", "in_memory", scope=Scope.GLOBAL)
    additional_dn_config_2 = Config.configure_data_node("additional_dn_2", "in_memory", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])
    scenario_config_1 = Config.configure_scenario(
        "scenario_1", [task_config_1, task_config_2], [additional_dn_config_1, additional_dn_config_2]
    )
    scenario_config_1.add_sequences({"sequence_1": [task_config_1, task_config_2]})
    scenario_config_2 = Config.configure_scenario(
        "scenario_2", [task_config_1, task_config_2, task_config_3], [additional_dn_config_1, additional_dn_config_2]
    )
    scenario_config_2.add_sequences(
        {"sequence_1": [task_config_1, task_config_2], "sequence_2": [task_config_1, task_config_3]}
    )

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    sequence_1_s1 = scenario_1.sequences["sequence_1"]

    assert all(sequence.parent_ids == {scenario_1.id} for sequence in scenario_1.sequences.values())
    tasks = scenario_1.tasks.values()
    assert all(task.parent_ids == {scenario_1.id, sequence_1_s1.id} for task in tasks)
    data_nodes = {}
    for task in tasks:
        data_nodes.update(task.data_nodes)
    assert data_nodes["dn_1"].parent_ids == {scenario_1.tasks["task_1"].id}
    assert data_nodes["dn_2"].parent_ids == {scenario_1.tasks["task_1"].id, scenario_1.tasks["task_2"].id}
    assert data_nodes["dn_3"].parent_ids == {scenario_1.tasks["task_2"].id}
    additional_data_nodes = scenario_1.additional_data_nodes
    assert additional_data_nodes["additional_dn_1"].parent_ids == {scenario_1.id}
    assert additional_data_nodes["additional_dn_2"].parent_ids == {scenario_1.id}

    scenario_2 = _ScenarioManager._create(scenario_config_2)
    sequence_1_s2 = scenario_2.sequences["sequence_1"]
    sequence_2_s2 = scenario_2.sequences["sequence_2"]

    assert all(sequence.parent_ids == {scenario_2.id} for sequence in scenario_2.sequences.values())
    assert scenario_1.tasks["task_1"] == scenario_2.tasks["task_1"]
    assert scenario_1.tasks["task_1"].parent_ids == {
        scenario_1.id,
        sequence_1_s1.id,
        scenario_2.id,
        sequence_1_s2.id,
        sequence_2_s2.id,
    }
    assert scenario_1.tasks["task_2"].parent_ids == {scenario_1.id, sequence_1_s1.id}
    assert scenario_2.tasks["task_2"].parent_ids == {scenario_2.id, sequence_1_s2.id}
    assert scenario_2.tasks["task_3"].parent_ids == {scenario_2.id, sequence_2_s2.id}
    additional_data_nodes = scenario_2.additional_data_nodes
    assert additional_data_nodes["additional_dn_1"].parent_ids == {scenario_1.id, scenario_2.id}
    assert additional_data_nodes["additional_dn_2"].parent_ids == {scenario_2.id}

    _ScenarioManager._hard_delete(scenario_1.id)
    _ScenarioManager._hard_delete(scenario_2.id)
    _TaskManager._delete_all()
    _DataManager._delete_all()

    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.GLOBAL)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.GLOBAL)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.GLOBAL)
    additional_dn_config_1 = Config.configure_data_node("additional_dn_1", "in_memory", scope=Scope.GLOBAL)
    additional_dn_config_2 = Config.configure_data_node("additional_dn_2", "in_memory", scope=Scope.GLOBAL)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])
    scenario_config_1 = Config.configure_scenario(
        "scenario_1", [task_config_1, task_config_2], [additional_dn_config_1, additional_dn_config_2]
    )
    scenario_config_1.add_sequences({"sequence_1": [task_config_1, task_config_2]})
    scenario_config_2 = Config.configure_scenario(
        "scenario_2", [task_config_1, task_config_2, task_config_3], [additional_dn_config_1, additional_dn_config_2]
    )
    scenario_config_2.add_sequences(
        {"sequence_1": [task_config_1, task_config_2], "sequence_2": [task_config_1, task_config_3]}
    )

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    sequence_1_s1 = scenario_1.sequences["sequence_1"]
    assert scenario_1.sequences["sequence_1"].parent_ids == {scenario_1.id}
    tasks = scenario_1.tasks.values()
    assert all(task.parent_ids == {scenario_1.id, sequence_1_s1.id} for task in tasks)
    data_nodes = {}
    for task in tasks:
        data_nodes.update(task.data_nodes)
    assert data_nodes["dn_1"].parent_ids == {scenario_1.tasks["task_1"].id}
    assert data_nodes["dn_2"].parent_ids == {scenario_1.tasks["task_1"].id, scenario_1.tasks["task_2"].id}
    assert data_nodes["dn_3"].parent_ids == {scenario_1.tasks["task_2"].id}
    additional_data_nodes = scenario_1.additional_data_nodes
    assert additional_data_nodes["additional_dn_1"].parent_ids == {scenario_1.id}
    assert additional_data_nodes["additional_dn_2"].parent_ids == {scenario_1.id}

    scenario_2 = _ScenarioManager._create(scenario_config_2)
    sequence_1_s2 = scenario_2.sequences["sequence_1"]
    sequence_2_s2 = scenario_2.sequences["sequence_2"]

    assert scenario_1.sequences["sequence_1"].parent_ids == {scenario_1.id}
    assert scenario_2.sequences["sequence_1"].parent_ids == {scenario_2.id}
    assert scenario_2.sequences["sequence_2"].parent_ids == {scenario_2.id}
    tasks = {**scenario_1.tasks, **scenario_2.tasks}
    assert tasks["task_1"].parent_ids == {
        scenario_1.id,
        scenario_2.id,
        sequence_1_s1.id,
        sequence_1_s2.id,
        sequence_2_s2.id,
    }
    assert tasks["task_2"].parent_ids == {scenario_1.id, scenario_2.id, sequence_1_s1.id, sequence_1_s2.id}
    assert tasks["task_3"].parent_ids == {scenario_2.id, sequence_2_s2.id}
    additional_data_nodes = scenario_2.additional_data_nodes
    assert additional_data_nodes["additional_dn_1"].parent_ids == {scenario_1.id, scenario_2.id}
    assert additional_data_nodes["additional_dn_2"].parent_ids == {scenario_1.id, scenario_2.id}


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_scenario_manager_only_creates_data_node_once():
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
        assert {t.config_id for t in list_tasks_by_level} == expected[i]
    assert scenario_1.cycle.frequency == Frequency.DAILY

    _ScenarioManager._create(scenario_config)

    assert len(_DataManager._get_all()) == 5
    assert len(_TaskManager._get_all()) == 4
    assert len(_SequenceManager._get_all()) == 4
    assert len(_ScenarioManager._get_all()) == 2


def test_notification_subscribe(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "pickle", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "pickle", Scope.SCENARIO, default_data=0),
            )
        ],
    )

    scenario = _ScenarioManager._create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)
    mocker.patch.object(
        _utils,
        "_load_fct",
        side_effect=[
            notify_1,
            notify_1,
            notify_1,
            notify_1,
            notify_2,
            notify_2,
            notify_2,
            notify_2,
        ],
    )

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._submit(scenario)
    notify_1.assert_called_3_times()
    notify_1.reset()

    # test unsubscribing notification
    # test notif subscribe only on new jobs
    _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_2, scenario=scenario)
    _ScenarioManager._submit(scenario)
    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


def test_notification_subscribe_multiple_params(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
    )
    notify = mocker.Mock()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._subscribe(callback=notify, params=["foobar", 123, 1.2], scenario=scenario)
    mocker.patch.object(_ScenarioManager, "_get", return_value=scenario)

    _ScenarioManager._submit(scenario)

    notify.assert_called_with("foobar", 123, 1.2, scenario, ANY)


def notify_multi_param(param, *args):
    assert len(param) == 3


def notify1(*args, **kwargs): ...


def notify2(*args, **kwargs): ...


def test_notification_unsubscribe(mocker):
    mocker.patch("taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
    )

    scenario = _ScenarioManager._create(scenario_config)

    notify_1 = notify1
    notify_2 = notify2

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_2, scenario=scenario)
    _ScenarioManager._submit(scenario.id)

    with pytest.raises(ValueError):
        _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._unsubscribe(callback=notify_2, scenario=scenario)


def test_notification_unsubscribe_multi_param():
    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
    )

    scenario = _ScenarioManager._create(scenario_config)

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 0], scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 1], scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 2], scenario=scenario)

    assert len(scenario.subscribers) == 3

    # if no params are passed, removes the first occurrence of the subscriber when there's more than one copy
    scenario.unsubscribe(notify_multi_param)
    assert len(scenario.subscribers) == 2
    assert _Subscriber(notify_multi_param, ["foobar", 123, 0]) not in scenario.subscribers

    # If params are passed, find the corresponding pair of callback and params to remove
    scenario.unsubscribe(notify_multi_param, ["foobar", 123, 2])
    assert len(scenario.subscribers) == 1
    assert _Subscriber(notify_multi_param, ["foobar", 123, 2]) not in scenario.subscribers

    # If params are passed but is not on the list of subscribers, throws a ValueErrors
    with pytest.raises(ValueError):
        scenario.unsubscribe(notify_multi_param, ["foobar", 123, 10000])


def test_scenario_notification_subscribe_all():
    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
    )
    other_scenario_config = Config.configure_scenario(
        "other_scenario",
        [
            Config.configure_task(
                "other_mult_by_2_2",
                mult_by_2,
                [Config.configure_data_node("other_foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("other_bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
    )

    scenario = _ScenarioManager._create(scenario_config)
    other_scenario = _ScenarioManager._create(other_scenario_config)
    notify_1 = NotifyMock(scenario)
    _ScenarioManager._subscribe(notify_1)
    assert len(_ScenarioManager._get(scenario.id).subscribers) == 1
    assert len(_ScenarioManager._get(other_scenario.id).subscribers) == 1


def test_is_promotable_to_primary_scenario():
    assert len(_ScenarioManager._get_all()) == 0
    scenario_config = Config.configure_scenario("sc", set(), set(), Frequency.DAILY)
    creation_date = datetime.now()
    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date, name="1")  # primary scenario
    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date, name="2")

    assert len(_ScenarioManager._get_all()) == 2
    assert scenario_1.is_primary
    assert not _ScenarioManager._is_promotable_to_primary(scenario_1)
    assert not _ScenarioManager._is_promotable_to_primary(scenario_1.id)
    assert not scenario_2.is_primary
    assert _ScenarioManager._is_promotable_to_primary(scenario_2)
    assert _ScenarioManager._is_promotable_to_primary(scenario_2.id)

    _ScenarioManager._set_primary(scenario_2)

    assert len(_ScenarioManager._get_all()) == 2
    assert not scenario_1.is_primary
    assert _ScenarioManager._is_promotable_to_primary(scenario_1)
    assert _ScenarioManager._is_promotable_to_primary(scenario_1.id)
    assert scenario_2.is_primary
    assert not _ScenarioManager._is_promotable_to_primary(scenario_2)
    assert not _ScenarioManager._is_promotable_to_primary(scenario_2.id)


def test_get_set_primary_scenario():
    cycle_1 = _CycleManager._create(Frequency.DAILY, name="foo")

    scenario_1 = Scenario("sc_1", [], {}, ScenarioId("sc_1"), is_primary=False, cycle=cycle_1)
    scenario_2 = Scenario("sc_2", [], {}, ScenarioId("sc_2"), is_primary=False, cycle=cycle_1)

    _ScenarioManager._delete_all()
    _CycleManager._delete_all()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_CycleManager._get_all()) == 0

    _CycleManager._set(cycle_1)

    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)

    assert len(_ScenarioManager._get_primary_scenarios()) == 0
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2

    _ScenarioManager._set_primary(scenario_1)

    assert len(_ScenarioManager._get_primary_scenarios()) == 1
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2
    assert _ScenarioManager._get_primary(cycle_1) == scenario_1

    _ScenarioManager._set_primary(scenario_2)

    assert len(_ScenarioManager._get_primary_scenarios()) == 1
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2
    assert _ScenarioManager._get_primary(cycle_1) == scenario_2


def test_get_primary_scenarios_sorted():
    scenario_1_cfg = Config.configure_scenario(id="scenario_1", frequency=Frequency.DAILY)
    scenario_2_cfg = Config.configure_scenario(id="scenario_2", frequency=Frequency.DAILY)

    not_primary_scenario = _ScenarioManager._create(scenario_1_cfg, name="not_primary_scenario")
    now = datetime.now()
    scenario_1 = _ScenarioManager._create(scenario_1_cfg, now, "B_scenario")
    scenario_2 = _ScenarioManager._create(scenario_2_cfg, now + timedelta(days=2), "A_scenario")
    scenario_3 = _ScenarioManager._create(scenario_2_cfg, now + timedelta(days=4), "C_scenario")
    scenario_4 = _ScenarioManager._create(scenario_2_cfg, now + timedelta(days=3), "D_scenario")

    _ScenarioManager._set_primary(scenario_1)
    scenario_1.tags = ["banana", "kiwi"]
    _ScenarioManager._set_primary(scenario_2)
    scenario_2.tags = ["apple", "banana"]
    _ScenarioManager._set_primary(scenario_3)
    scenario_3.tags = ["banana", "kiwi"]
    _ScenarioManager._set_primary(scenario_4)

    all_scenarios = tp.get_scenarios()
    assert not_primary_scenario in all_scenarios

    primary_scenarios = _ScenarioManager._get_primary_scenarios()
    assert not_primary_scenario not in primary_scenarios

    primary_scenarios_sorted_by_name = [scenario_2, scenario_1, scenario_3, scenario_4]
    assert primary_scenarios_sorted_by_name == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=False, sort_key="name"
    )

    scenarios_with_same_config_id = [scenario_2, scenario_3, scenario_4]
    scenarios_with_same_config_id.sort(key=lambda x: x.id)
    primary_scenarios_sorted_by_config_id = [
        scenario_1,
        scenarios_with_same_config_id[0],
        scenarios_with_same_config_id[1],
        scenarios_with_same_config_id[2],
    ]
    assert primary_scenarios_sorted_by_config_id == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=False, sort_key="config_id"
    )

    scenarios_sorted_by_id = [scenario_1, scenario_2, scenario_3, scenario_4]
    scenarios_sorted_by_id.sort(key=lambda x: x.id)
    assert scenarios_sorted_by_id == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=False, sort_key="id"
    )

    primary_scenarios_sorted_by_creation_date = [scenario_1, scenario_2, scenario_4, scenario_3]
    assert primary_scenarios_sorted_by_creation_date == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=False, sort_key="creation_date"
    )

    scenarios_with_same_tags = [scenario_1, scenario_3]
    scenarios_with_same_tags.sort(key=lambda x: x.id)
    primary_scenarios_sorted_by_tags = [
        scenario_4,
        scenario_2,
        scenarios_with_same_tags[0],
        scenarios_with_same_tags[1],
    ]
    assert primary_scenarios_sorted_by_tags == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=False, sort_key="tags"
    )

    primary_scenarios_sorted_by_name_descending_order = [scenario_4, scenario_3, scenario_1, scenario_2]
    assert primary_scenarios_sorted_by_name_descending_order == _ScenarioManager._sort_scenarios(
        primary_scenarios, descending=True, sort_key="name"
    )


def test_hard_delete_one_single_scenario_with_scenario_data_nodes():
    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    scenario_config = Config.configure_scenario("scenario_config", [task_config])
    scenario_config.add_sequences({"sequence_config": [task_config]})

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario.id)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _ScenarioManager._hard_delete(scenario.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_SequenceManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_scenario_among_two_with_scenario_data_nodes():
    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    scenario_config = Config.configure_scenario("scenario_config", [task_config])
    scenario_config.add_sequences({"sequence_config": [task_config]})

    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 2
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_2.id) is not None


def test_hard_delete_one_scenario_among_two_with_cycle_data_nodes():
    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    scenario_config = Config.configure_scenario("scenario_config", [task_config])
    scenario_config.add_sequences({"sequence_config": [task_config]})

    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 2
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_2.id) is not None


def test_hard_delete_shared_entities():
    dn_config_1 = Config.configure_data_node("my_input_1", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_config_2 = Config.configure_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_config_3 = Config.configure_data_node("my_input_3", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_config_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_config_1 = Config.configure_task("task_config_1", print, dn_config_1, dn_config_2)
    task_config_2 = Config.configure_task("task_config_2", print, dn_config_2, dn_config_3)
    task_config_3 = Config.configure_task("task_config_3", print, dn_config_3, dn_config_4)  # scope = global
    task_config_4 = Config.configure_task("task_config_4", print, dn_config_1)  # scope = cycle
    scenario_config_1 = Config.configure_scenario(
        "scenario_config_1",
        [task_config_1, task_config_2, task_config_3, task_config_4],
        frequency=Frequency.WEEKLY,
    )
    scenario_config_1.add_sequences(
        {
            "sequence_config_1": [task_config_1, task_config_2],
            "sequence_config_2": [task_config_1, task_config_2],
            "sequence_config_3": [task_config_3],
            "sequence_config_4": [task_config_4],
        }
    )

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    scenario_2 = _ScenarioManager._create(scenario_config_1)
    scenario_1.submit()
    scenario_2.submit()

    assert len(_CycleManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 8
    assert len(_TaskManager._get_all()) == 6
    assert len(_DataManager._get_all()) == 5
    assert len(_JobManager._get_all()) == 8
    _ScenarioManager._hard_delete(scenario_2.id)
    assert len(_CycleManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 4
    assert len(_TaskManager._get_all()) == 4
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 6


def test_is_submittable():
    assert len(_ScenarioManager._get_all()) == 0

    dn_config = Config.configure_in_memory_data_node("dn", 10)
    task_config = Config.configure_task("task", print, [dn_config])
    scenario_config = Config.configure_scenario("sc", {task_config}, set(), Frequency.DAILY)
    scenario = _ScenarioManager._create(scenario_config)

    rc = _ScenarioManager._is_submittable("some_scenario")
    assert not rc
    assert "Entity some_scenario does not exist in the repository." in rc.reasons

    assert len(_ScenarioManager._get_all()) == 1
    assert _ScenarioManager._is_submittable(scenario)
    assert _ScenarioManager._is_submittable(scenario.id)
    assert not _ScenarioManager._is_submittable("Scenario_temp")

    scenario.dn.edit_in_progress = True
    assert not _ScenarioManager._is_submittable(scenario)
    assert not _ScenarioManager._is_submittable(scenario.id)

    scenario.dn.edit_in_progress = False
    assert _ScenarioManager._is_submittable(scenario)
    assert _ScenarioManager._is_submittable(scenario.id)


def test_submit():
    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = InMemoryDataNode("fum", Scope.SCENARIO, "s8")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_3, data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("thud", {}, print, [data_node_6], [data_node_8], TaskId("t5"))

    scenario = Scenario(
        "scenario_name",
        [task_5, task_4, task_2, task_1, task_3],
        {},
        [],
        ScenarioId("sce_id"),
    )

    class MockOrchestrator(_Orchestrator):
        submit_calls = []

        @classmethod
        def _lock_dn_output_and_create_job(
            cls,
            task: Task,
            submit_id: str,
            submit_entity_id: str,
            callbacks: Optional[Iterable[Callable]] = None,
            force: bool = False,
        ) -> Job:
            cls.submit_calls.append(task.id)
            return super()._lock_dn_output_and_create_job(task, submit_id, submit_entity_id, callbacks, force)

    with patch("taipy.core.task._task_manager._TaskManager._orchestrator", new=MockOrchestrator):
        with pytest.raises(NonExistingScenario):
            _ScenarioManager._submit(scenario.id)
        with pytest.raises(NonExistingScenario):
            _ScenarioManager._submit(scenario)

        # scenario and sequence do exist, but tasks does not exist.
        # We expect an exception to be raised
        _ScenarioManager._set(scenario)
        with pytest.raises(NonExistingTask):
            _ScenarioManager._submit(scenario.id)
        with pytest.raises(NonExistingTask):
            _ScenarioManager._submit(scenario)

        # scenario, sequence, and tasks do exist.
        # We expect all the tasks to be submitted once,
        # and respecting specific constraints on the order
        _TaskManager._set(task_1)
        _TaskManager._set(task_2)
        _TaskManager._set(task_3)
        _TaskManager._set(task_4)
        _TaskManager._set(task_5)
        _ScenarioManager._submit(scenario.id)
        submit_calls = _TaskManager._orchestrator().submit_calls
        assert len(submit_calls) == 5
        assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
        assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)

        _ScenarioManager._submit(scenario)
        submit_calls = _TaskManager._orchestrator().submit_calls
        assert len(submit_calls) == 10
        assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
        assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
        assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)


def my_print(a, b):
    print(a + b)  # noqa: T201


def test_submit_task_with_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_path="wrong_path.pickle")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)
    scenario_cfg = Config.configure_scenario("scenario", [task_cfg, task_2_cfg])
    sc_manager = _ScenarioManagerFactory._build_manager()
    scenario = sc_manager._create(scenario_cfg)
    sc_manager._submit(scenario)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in scenario.get_inputs()
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in scenario.data_nodes.values()
        if input_dn not in scenario.get_inputs()
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_submit_task_with_one_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_data="value")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)
    scenario_cfg = Config.configure_scenario("scenario", [task_cfg, task_2_cfg])
    sce_manager = _ScenarioManagerFactory._build_manager()
    scenario = sce_manager._create(scenario_cfg)
    sce_manager._submit(scenario)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in scenario.get_inputs()
        if input_dn.config_id == "wrong_csv_file_path"
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in scenario.data_nodes.values()
        if input_dn.config_id != "wrong_csv_file_path"
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def subtraction(n1, n2):
    return n1 - n2


def addition(n1, n2):
    return n1 + n2


def test_scenarios_comparison():
    scenario_config = Config.configure_scenario(
        "Awesome_scenario",
        [
            Config.configure_task(
                "mult_by_2",
                mult_by_2,
                [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
            )
        ],
        comparators={"bar": [subtraction], "foo": [subtraction, addition]},
    )

    assert scenario_config.comparators is not None
    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)

    with pytest.raises(InsufficientScenarioToCompare):
        _ScenarioManager._compare(scenario_1, data_node_config_id="bar")

    scenario_3 = Scenario("awesome_scenario_config", [], {})
    with pytest.raises(DifferentScenarioConfigs):
        _ScenarioManager._compare(scenario_1, scenario_3, data_node_config_id="bar")

    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    bar_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="bar")["bar"]
    assert bar_comparison["subtraction"] == 0

    foo_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="foo")["foo"]
    assert len(foo_comparison.keys()) == 2
    assert foo_comparison["addition"] == 2
    assert foo_comparison["subtraction"] == 0

    assert len(_ScenarioManager._compare(scenario_1, scenario_2).keys()) == 2

    with pytest.raises(NonExistingScenarioConfig):
        _ScenarioManager._compare(scenario_3, scenario_3)

    with pytest.raises(NonExistingComparator):
        _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="abc")


def test_tags():
    cycle_1 = _CycleManager._create(Frequency.DAILY, name="today", creation_date=datetime.now())
    cycle_2 = _CycleManager._create(
        Frequency.DAILY,
        name="tomorrow",
        creation_date=datetime.now() + timedelta(days=1),
    )
    cycle_3 = _CycleManager._create(
        Frequency.DAILY,
        name="yesterday",
        creation_date=datetime.now() + timedelta(days=-1),
    )

    scenario_no_tag = Scenario("scenario_no_tag", [], {}, [], ScenarioId("scenario_no_tag"), cycle=cycle_1)
    scenario_1_tag = Scenario(
        "scenario_1_tag",
        [],
        {},
        [],
        ScenarioId("scenario_1_tag"),
        cycle=cycle_1,
        tags={"fst"},
    )
    scenario_2_tags = Scenario(
        "scenario_2_tags",
        [],
        {},
        [],
        ScenarioId("scenario_2_tags"),
        cycle=cycle_2,
        tags={"fst", "scd"},
    )

    # Test has_tag
    assert len(scenario_no_tag.tags) == 0
    assert not scenario_no_tag.has_tag("fst")
    assert not scenario_no_tag.has_tag("scd")

    assert len(scenario_1_tag.tags) == 1
    assert scenario_1_tag.has_tag("fst")
    assert not scenario_1_tag.has_tag("scd")

    assert len(scenario_2_tags.tags) == 2
    assert scenario_2_tags.has_tag("fst")
    assert scenario_2_tags.has_tag("scd")

    # test get and set serialize/deserialize tags
    _CycleManager._set(cycle_1)
    _CycleManager._set(cycle_2)
    _CycleManager._set(cycle_3)
    _ScenarioManager._set(scenario_no_tag)
    _ScenarioManager._set(scenario_1_tag)
    _ScenarioManager._set(scenario_2_tags)

    assert len(_ScenarioManager._get(ScenarioId("scenario_no_tag")).tags) == 0
    assert not _ScenarioManager._get(ScenarioId("scenario_no_tag")).has_tag("fst")
    assert not _ScenarioManager._get(ScenarioId("scenario_no_tag")).has_tag("scd")

    assert len(_ScenarioManager._get(ScenarioId("scenario_1_tag")).tags) == 1
    assert "fst" in _ScenarioManager._get(ScenarioId("scenario_1_tag")).tags
    assert "scd" not in _ScenarioManager._get(ScenarioId("scenario_1_tag")).tags

    assert len(_ScenarioManager._get(ScenarioId("scenario_2_tags")).tags) == 2
    assert "fst" in _ScenarioManager._get(ScenarioId("scenario_2_tags")).tags
    assert "scd" in _ScenarioManager._get(ScenarioId("scenario_2_tags")).tags

    # Test tag & untag

    _ScenarioManager._tag(scenario_no_tag, "thd")  # add new tag
    _ScenarioManager._untag(scenario_1_tag, "NOT_EXISTING_TAG")  # remove not existing tag does nothing
    _ScenarioManager._untag(scenario_1_tag, "fst")  # remove `fst` tag

    assert len(scenario_no_tag.tags) == 1
    assert not scenario_no_tag.has_tag("fst")
    assert not scenario_no_tag.has_tag("scd")
    assert scenario_no_tag.has_tag("thd")

    assert len(scenario_1_tag.tags) == 0
    assert not scenario_1_tag.has_tag("fst")
    assert not scenario_1_tag.has_tag("scd")
    assert not scenario_1_tag.has_tag("thd")

    assert len(scenario_2_tags.tags) == 2
    assert scenario_2_tags.has_tag("fst")
    assert scenario_2_tags.has_tag("scd")
    assert not scenario_2_tags.has_tag("thd")

    _ScenarioManager._untag(scenario_no_tag, "thd")
    _ScenarioManager._set(scenario_no_tag)
    _ScenarioManager._tag(scenario_1_tag, "fst")
    _ScenarioManager._set(scenario_1_tag)

    # test getters
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "fst") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "scd") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "thd") == []

    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "fst") == [scenario_2_tags]
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "scd") == [scenario_2_tags]
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "thd") == []

    assert _ScenarioManager._get_all_by_cycle_tag(cycle_1, "fst") == [scenario_1_tag]
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_1, "scd") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_1, "thd") == []

    assert len(_ScenarioManager._get_all_by_tag("NOT_EXISTING")) == 0
    assert scenario_1_tag in _ScenarioManager._get_all_by_tag("fst")
    assert scenario_2_tags in _ScenarioManager._get_all_by_tag("fst")
    assert _ScenarioManager._get_all_by_tag("scd") == [scenario_2_tags]
    assert len(_ScenarioManager._get_all_by_tag("thd")) == 0

    # test tag cycle mgt

    _ScenarioManager._tag(scenario_no_tag, "fst")  # tag sc_no_tag with fst should not affect sc_1_tag and sc_2_tags

    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "fst") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "scd") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_3, "thd") == []

    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "fst") == [scenario_2_tags]
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "scd") == [scenario_2_tags]
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_2, "thd") == []

    assert sorted([s.id for s in _ScenarioManager._get_all_by_cycle_tag(cycle_1, "fst")]) == sorted(
        [s.id for s in [scenario_no_tag, scenario_1_tag]]
    )
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_1, "scd") == []
    assert _ScenarioManager._get_all_by_cycle_tag(cycle_1, "thd") == []

    assert len(_ScenarioManager._get_all_by_tag("NOT_EXISTING")) == 0
    assert len(_ScenarioManager._get_all_by_tag("fst")) == 3
    assert scenario_2_tags in _ScenarioManager._get_all_by_tag("fst")
    assert scenario_no_tag in _ScenarioManager._get_all_by_tag("fst")
    assert _ScenarioManager._get_all_by_tag("scd") == [scenario_2_tags]
    assert len(_ScenarioManager._get_all_by_tag("thd")) == 0


def test_authorized_tags():
    scenario = Scenario("scenario_1", [], {"authorized_tags": ["foo", "bar"]}, [], ScenarioId("scenario_1"))
    scenario_2_cfg = Config.configure_scenario("scenario_2", [], [], Frequency.DAILY, authorized_tags=["foo", "bar"])

    scenario_2 = _ScenarioManager._create(scenario_2_cfg)
    _ScenarioManager._set(scenario)

    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    with pytest.raises(UnauthorizedTagError):
        _ScenarioManager._tag(scenario, "baz")
        _ScenarioManager._tag(scenario_2, "baz")
    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    _ScenarioManager._tag(scenario, "foo")
    _ScenarioManager._tag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1

    _ScenarioManager._tag(scenario, "bar")
    _ScenarioManager._tag(scenario_2, "bar")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    _ScenarioManager._tag(scenario, "foo")
    _ScenarioManager._tag(scenario_2, "foo")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    _ScenarioManager._untag(scenario, "foo")
    _ScenarioManager._untag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1


def test_get_scenarios_by_config_id():
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


def test_get_scenarios_by_config_id_in_multiple_versions_environment():
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


def test_filter_scenarios_by_creation_datetime():
    scenario_config_1 = Config.configure_scenario("s1", sequence_configs=[])

    with freezegun.freeze_time("2024-01-01"):
        s_1_1 = _ScenarioManager._create(scenario_config_1)
    with freezegun.freeze_time("2024-01-03"):
        s_1_2 = _ScenarioManager._create(scenario_config_1)
    with freezegun.freeze_time("2024-02-01"):
        s_1_3 = _ScenarioManager._create(scenario_config_1)

    all_scenarios = _ScenarioManager._get_all()

    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_start_time=datetime(2024, 1, 1),
        created_end_time=datetime(2024, 1, 2),
    )
    assert len(filtered_scenarios) == 1
    assert [s_1_1] == filtered_scenarios

    # The start time is inclusive
    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_start_time=datetime(2024, 1, 1),
        created_end_time=datetime(2024, 1, 3),
    )
    assert len(filtered_scenarios) == 1
    assert [s_1_1] == filtered_scenarios

    # The end time is exclusive
    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_start_time=datetime(2024, 1, 1),
        created_end_time=datetime(2024, 1, 4),
    )
    assert len(filtered_scenarios) == 2
    assert sorted([s_1_1.id, s_1_2.id]) == sorted([scenario.id for scenario in filtered_scenarios])

    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_start_time=datetime(2023, 1, 1),
        created_end_time=datetime(2025, 1, 1),
    )
    assert len(filtered_scenarios) == 3
    assert sorted([s_1_1.id, s_1_2.id, s_1_3.id]) == sorted([scenario.id for scenario in filtered_scenarios])

    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_start_time=datetime(2024, 2, 1),
    )
    assert len(filtered_scenarios) == 1
    assert [s_1_3] == filtered_scenarios

    filtered_scenarios = _ScenarioManager._filter_by_creation_time(
        scenarios=all_scenarios,
        created_end_time=datetime(2024, 1, 2),
    )
    assert len(filtered_scenarios) == 1
    assert [s_1_1] == filtered_scenarios
