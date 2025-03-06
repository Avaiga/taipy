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

from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import call

from taipy import Config, Frequency, Scope, Sequence
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager import _JobManager
from taipy.core.scenario._scenario_duplicator import _ScenarioDuplicator
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.sequence._sequence_manager import _SequenceManager
from taipy.core.submission._submission_manager import _SubmissionManager
from taipy.core.task._task_manager import _TaskManager


def identity(x):
    return x

def test_constructor():
    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    additional_dn_config_1 = Config.configure_data_node("additional_dn_1")
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [])
    scenario_config_1 = Config.configure_scenario("scenario_1", [task_config_1], [additional_dn_config_1])
    scenario = _ScenarioManager._create(scenario_config_1)

    duplicator = _ScenarioDuplicator(scenario)
    assert duplicator.scenario == scenario
    assert duplicator.data_to_duplicate == {"dn_1", "additional_dn_1"}

    duplicator = _ScenarioDuplicator(scenario, True)
    assert duplicator.scenario == scenario
    assert duplicator.data_to_duplicate == {"dn_1", "additional_dn_1"}

    duplicator = _ScenarioDuplicator(scenario, False)
    assert duplicator.scenario == scenario
    assert duplicator.data_to_duplicate == set()

    duplicator = _ScenarioDuplicator(scenario, {"dn_1"})
    assert duplicator.scenario == scenario
    assert duplicator.data_to_duplicate == {"dn_1"}

    duplicator = _ScenarioDuplicator(scenario, {"additional_dn_1"})
    assert duplicator.scenario == scenario
    assert duplicator.data_to_duplicate == {"additional_dn_1"}


def test_duplicate_scenario_scoped_dns_no_cycle_one_sequence():
    dn_config_1 = Config.configure_pickle_data_node("dn_1", default_data="data1", key1="value1")
    dn_config_2 = Config.configure_pickle_data_node("dn_2", key1="value2")
    additional_dn_config_1 = Config.configure_data_node("additional_dn_1")
    task_config_1 = Config.configure_task("task_1",
                                          print,
                                          input=[dn_config_1],
                                          output=[dn_config_2],
                                          skippable=True,
                                          k="v")
    scenario_config_1 = Config.configure_scenario("scenario_1", [task_config_1], [additional_dn_config_1])
    creation_date = datetime.now() - timedelta(minutes=1)
    name = "original"
    scenario = _ScenarioManager._create(scenario_config_1, creation_date, name)
    scenario.properties["key"] = "value"
    scenario.add_sequence("sequence_1", [scenario.task_1], {"key_seq": "value_seq"})
    scenario.submit()
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 1
    assert len(_SequenceManager._get_all()) == 1
    assert len(_CycleManager._get_all()) == 0
    assert len(_SubmissionManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1

    new_scenario = _ScenarioDuplicator(scenario, False).duplicate()

    # Check scenario attributes
    assert scenario.id != new_scenario.id
    assert scenario.config_id == new_scenario.config_id == "scenario_1"
    assert scenario.name == name
    assert new_scenario.name == name
    assert scenario.creation_date == creation_date
    assert new_scenario.creation_date > creation_date
    assert scenario.cycle is None
    assert new_scenario.cycle is None

    # Check task attributes
    assert len(scenario.tasks) == len(new_scenario.tasks) == 1
    task = scenario.tasks["task_1"]
    new_task = new_scenario.tasks["task_1"]
    assert task.id != new_task.id
    assert task._config_id == new_task._config_id == "task_1"
    assert task._owner_id == scenario.id
    assert new_task._owner_id == new_scenario.id
    assert task._parent_ids == {scenario.id, Sequence._new_id("sequence_1", scenario.id)}
    assert new_task._parent_ids == {new_scenario.id, Sequence._new_id("sequence_1", new_scenario.id)}

    assert task._function == new_task._function
    assert task._skippable == new_task._skippable is True
    assert task._properties == new_task._properties == {"k": "v"}

    # Check data node attributes
    assert len(scenario.data_nodes) == len(new_scenario.data_nodes) == 3
    def assert_dn(config_id, ppties, additional_dn=False):
        dn = scenario.data_nodes[config_id]
        new_dn = new_scenario.data_nodes[config_id]
        assert dn.id != new_dn.id
        assert dn._config_id == new_dn._config_id == config_id
        assert dn._owner_id == scenario.id
        assert new_dn._owner_id == new_scenario.id
        if additional_dn:
            assert dn._parent_ids == {scenario.id}
            assert new_dn._parent_ids == {new_scenario.id}
        else:
            assert dn._parent_ids == {task.id}
            assert new_dn._parent_ids == {new_task.id}
        assert dn._scope == new_dn._scope == Scope.SCENARIO
        assert len(dn._properties) == len(new_dn._properties)
        for k, v in dn._properties.items():
            assert new_dn._properties[k] == v
        for k, v in ppties.items():
            assert dn._properties[k] == new_dn._properties[k] == v
        # assert dn_1._last_edit_date < new_dn_1._last_edit_date>
        # assert dn_1.edits
        # assert new_dn_1.edits

    assert_dn("dn_1", {"key1": "value1"})
    assert_dn("dn_2", {"key1": "value2"})
    assert_dn("additional_dn_1", {}, additional_dn=True)

    # Check sequence attributes
    assert len(scenario.sequences) == len(new_scenario.sequences) == 1
    sequence = scenario.sequences["sequence_1"]
    new_sequence = new_scenario.sequences["sequence_1"]
    assert sequence.id != new_sequence.id
    assert len(sequence._tasks) == len(new_sequence._tasks) == 1
    assert sequence.tasks["task_1"].id == task.id
    assert new_sequence.tasks["task_1"].id == new_task.id
    assert sequence._owner_id == scenario.id
    assert new_sequence._owner_id == new_scenario.id
    assert sequence._parent_ids == {scenario.id}
    assert new_sequence._parent_ids == {new_scenario.id}
    assert len(sequence._properties) == len(new_sequence._properties)
    for k, v in sequence._properties.items():
        assert new_sequence._properties[k] == v
    assert sequence._properties["key_seq"] == new_sequence._properties["key_seq"] == "value_seq"

    # Check cycles, submissions and jobs are not duplicated
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 6
    assert len(_TaskManager._get_all()) == 2
    assert len(_SequenceManager._get_all()) == 2
    assert len(_CycleManager._get_all()) == 0
    assert len(_SubmissionManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 1


def test_duplicate_same_cycle():
    dn_cfg_1 = Config.configure_pickle_data_node("dn_1", scope=Scope.GLOBAL)
    dn_cfg_2 = Config.configure_pickle_data_node("dn_2", scope=Scope.CYCLE)
    dn_cfg_3 = Config.configure_pickle_data_node("dn_3", scope=Scope.SCENARIO)
    dn_cfg_4 = Config.configure_pickle_data_node("dn_4", scope=Scope.SCENARIO)
    t_cfg_1 = Config.configure_task("task_1", identity, input=[dn_cfg_1], output=[dn_cfg_2])
    t_cfg_2 = Config.configure_task("task_2", identity, input=[dn_cfg_2], output=[dn_cfg_3])
    t_cfg_3 = Config.configure_task("task_3", identity, input=[dn_cfg_3], output=[dn_cfg_4])
    s_cfg_1 = Config.configure_scenario("scenario_1", [t_cfg_1, t_cfg_2, t_cfg_3], frequency=Frequency.DAILY)
    creation_date = datetime.now() - timedelta(days=2)
    name = "original"
    scenario = _ScenarioManager._create(s_cfg_1, creation_date, name)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4

    new_name = "new"
    new_scenario = _ScenarioDuplicator(scenario, False).duplicate(creation_date, new_name)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 5
    assert len(_DataManager._get_all()) == 6

    # Check scenario attributes
    assert scenario.id != new_scenario.id
    assert scenario.config_id == new_scenario.config_id == "scenario_1"
    assert scenario.name == name
    assert new_scenario.name == new_name
    assert scenario.creation_date == new_scenario.creation_date == creation_date
    assert scenario.cycle.id == new_scenario.cycle.id
    assert len(scenario.sequences) == len(new_scenario.sequences) == 0

    # Check tasks attributes
    assert len(scenario.tasks) == len(new_scenario.tasks) == 3
    task_1 = scenario.tasks["task_1"]
    new_task_1 = new_scenario.tasks["task_1"]
    assert task_1 == new_task_1
    assert task_1.id == new_task_1.id
    assert task_1._config_id == new_task_1._config_id == "task_1"
    assert task_1._owner_id == new_task_1._owner_id == scenario.cycle.id
    assert task_1._parent_ids == new_task_1._parent_ids == {scenario.id, new_scenario.id}
    assert task_1._function == new_task_1._function
    assert task_1._skippable == new_task_1._skippable is False
    assert task_1._properties == new_task_1._properties == {}

    task_2 = scenario.tasks["task_2"]
    new_task_2 = new_scenario.tasks["task_2"]
    assert task_2.id != new_task_2.id
    assert task_2._config_id == new_task_2._config_id == "task_2"
    assert task_2._owner_id == scenario.id
    assert new_task_2._owner_id == new_scenario.id
    assert task_2._parent_ids == {scenario.id}
    assert new_task_2._parent_ids == {new_scenario.id}
    assert task_2._function == new_task_2._function
    assert task_2._skippable == new_task_2._skippable is False
    assert task_2._properties == new_task_2._properties == {}

    task_3 = scenario.tasks["task_3"]
    new_task_3 = new_scenario.tasks["task_3"]
    assert task_3.id != new_task_3.id
    assert task_3._config_id == new_task_3._config_id == "task_3"
    assert task_3._owner_id == scenario.id
    assert new_task_3._owner_id == new_scenario.id
    assert task_3._parent_ids == {scenario.id}
    assert new_task_3._parent_ids == {new_scenario.id}
    assert task_3._function == new_task_3._function
    assert task_3._skippable == new_task_3._skippable is False
    assert task_3._properties == new_task_3._properties == {}

    # Check data node attributes
    assert len(scenario.data_nodes) == len(new_scenario.data_nodes) == 4
    dn_1 = scenario.data_nodes["dn_1"]
    new_dn_1 = new_scenario.data_nodes["dn_1"]
    assert dn_1.id == new_dn_1.id
    assert dn_1._config_id == new_dn_1._config_id == "dn_1"
    assert dn_1._scope == new_dn_1._scope == Scope.GLOBAL
    assert dn_1._owner_id == new_dn_1._owner_id is None
    assert dn_1._parent_ids == new_dn_1._parent_ids == {task_1.id, new_task_1.id}
    assert dn_1._last_edit_date == new_dn_1._last_edit_date
    assert dn_1._edits == new_dn_1._edits
    assert len(dn_1._properties) == len(new_dn_1._properties)
    for k, v in dn_1._properties.items():
        assert new_dn_1._properties[k] == v

    dn_2 = scenario.dn_2
    new_dn_2 = new_scenario.dn_2
    assert dn_2.id == new_dn_2.id
    assert dn_2._config_id == new_dn_2._config_id == "dn_2"
    assert dn_2._scope == new_dn_2._scope == Scope.CYCLE
    assert dn_2._owner_id == new_dn_2._owner_id == scenario.cycle.id
    assert dn_2._parent_ids == {task_1.id, task_2.id, new_task_2.id}
    assert new_dn_2._parent_ids == {task_1.id, task_2.id, new_task_2.id}
    assert dn_2._last_edit_date == new_dn_2._last_edit_date
    assert dn_2._edits == new_dn_2._edits
    assert len(dn_2._properties) == len(new_dn_2._properties)
    for k, v in dn_2._properties.items():
        assert new_dn_2._properties[k] == v

    dn_3 = scenario.data_nodes["dn_3"]
    new_dn_3 = new_scenario.data_nodes["dn_3"]
    assert dn_3.id != new_dn_3.id
    assert dn_3._config_id == new_dn_3._config_id == "dn_3"
    assert dn_3._scope == new_dn_3._scope == Scope.SCENARIO
    assert dn_3._owner_id == scenario.id
    assert new_dn_3._owner_id == new_scenario.id
    assert dn_3._parent_ids == {task_2.id, task_3.id}
    assert new_dn_3._parent_ids == {new_task_2.id, new_task_3.id}
    assert dn_3._last_edit_date == new_dn_3._last_edit_date
    assert dn_3._edits == new_dn_3._edits
    assert len(dn_3._properties) == len(new_dn_3._properties)
    for k, v in dn_3._properties.items():
        assert new_dn_3._properties[k] == v

    dn_4 = scenario.data_nodes["dn_4"]
    new_dn_4 = new_scenario.data_nodes["dn_4"]
    assert dn_4.id != new_dn_4.id
    assert dn_4._config_id == new_dn_4._config_id == "dn_4"
    assert dn_4._scope == new_dn_4._scope == Scope.SCENARIO
    assert dn_4._owner_id == scenario.id
    assert new_dn_4._owner_id == new_scenario.id
    assert dn_4._parent_ids == {task_3.id}
    assert new_dn_4._parent_ids == {new_task_3.id}
    assert dn_4._last_edit_date == new_dn_4._last_edit_date
    assert dn_4._edits == new_dn_4._edits
    assert len(dn_4._properties) == len(new_dn_4._properties)
    for k, v in dn_4._properties.items():
        assert new_dn_4._properties[k] == v


def test_duplicate_to_new_cycle():
    dn_cfg_1 = Config.configure_pickle_data_node("dn_1", scope=Scope.GLOBAL)
    dn_cfg_2 = Config.configure_pickle_data_node("dn_2", scope=Scope.CYCLE)
    dn_cfg_3 = Config.configure_pickle_data_node("dn_3", scope=Scope.SCENARIO)
    dn_cfg_4 = Config.configure_pickle_data_node("dn_4", scope=Scope.SCENARIO)
    t_cfg_1 = Config.configure_task("task_1", identity, input=[dn_cfg_1], output=[dn_cfg_2])
    t_cfg_2 = Config.configure_task("task_2", identity, input=[dn_cfg_2], output=[dn_cfg_3])
    t_cfg_3 = Config.configure_task("task_3", identity, input=[dn_cfg_3], output=[dn_cfg_4])
    s_cfg_1 = Config.configure_scenario("scenario_1", [t_cfg_1, t_cfg_2, t_cfg_3], frequency=Frequency.DAILY)
    creation_date = datetime.now() - timedelta(days=2)
    name = "original"
    scenario = _ScenarioManager._create(s_cfg_1, creation_date, name)

    assert len(_CycleManager._get_all()) == 1
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4

    new_creation_date = datetime.now()
    new_name = "new"
    new_scenario = _ScenarioDuplicator(scenario, False).duplicate(new_creation_date, new_name)

    assert len(_CycleManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 6
    assert len(_DataManager._get_all()) == 7

    # Check scenario attributes
    assert scenario.id != new_scenario.id
    assert scenario.config_id == new_scenario.config_id == "scenario_1"
    assert scenario.name == name
    assert new_scenario.name == new_name
    assert scenario.creation_date == creation_date
    assert new_scenario.creation_date == new_creation_date
    assert scenario.cycle.id != new_scenario.cycle.id

    # Check tasks attributes
    assert len(scenario.tasks) == len(new_scenario.tasks) == 3
    task_1 = scenario.tasks["task_1"]
    new_task_1 = new_scenario.tasks["task_1"]
    assert task_1 != new_task_1
    assert task_1.id != new_task_1.id
    assert task_1._config_id == new_task_1._config_id == "task_1"
    assert task_1._owner_id == scenario.cycle.id
    assert new_task_1._owner_id == new_scenario.cycle.id
    assert task_1._parent_ids == {scenario.id}
    assert new_task_1._parent_ids == {new_scenario.id}
    assert task_1._function == new_task_1._function
    assert task_1._skippable == new_task_1._skippable is False
    assert task_1._properties == new_task_1._properties == {}

    task_2 = scenario.tasks["task_2"]
    new_task_2 = new_scenario.tasks["task_2"]
    assert task_2.id != new_task_2.id
    assert task_2._config_id == new_task_2._config_id == "task_2"
    assert task_2._owner_id == scenario.id
    assert new_task_2._owner_id == new_scenario.id
    assert task_2._parent_ids == {scenario.id}
    assert new_task_2._parent_ids == {new_scenario.id}
    assert task_2._function == new_task_2._function
    assert task_2._skippable == new_task_2._skippable is False
    assert task_2._properties == new_task_2._properties == {}

    task_3 = scenario.tasks["task_3"]
    new_task_3 = new_scenario.tasks["task_3"]
    assert task_3.id != new_task_3.id
    assert task_3._config_id == new_task_3._config_id == "task_3"
    assert task_3._owner_id == scenario.id
    assert new_task_3._owner_id == new_scenario.id
    assert task_3._parent_ids == {scenario.id}
    assert new_task_3._parent_ids == {new_scenario.id}
    assert task_3._function == new_task_3._function
    assert task_3._skippable == new_task_3._skippable is False
    assert task_3._properties == new_task_3._properties == {}

    # Check data node attributes
    assert len(scenario.data_nodes) == len(new_scenario.data_nodes) == 4
    dn_1 = scenario.data_nodes["dn_1"]
    new_dn_1 = new_scenario.data_nodes["dn_1"]
    assert dn_1.id == new_dn_1.id
    assert dn_1._config_id == new_dn_1._config_id == "dn_1"
    assert dn_1._scope == new_dn_1._scope == Scope.GLOBAL
    assert dn_1._owner_id == new_dn_1._owner_id is None
    assert dn_1._parent_ids == new_dn_1._parent_ids == {task_1.id, new_task_1.id}
    assert dn_1._last_edit_date == new_dn_1._last_edit_date
    assert dn_1._edits == new_dn_1._edits
    assert len(dn_1._properties) == len(new_dn_1._properties)
    for k, v in dn_1._properties.items():
        assert new_dn_1._properties[k] == v

    dn_2 = scenario.dn_2
    new_dn_2 = new_scenario.dn_2
    assert dn_2.id != new_dn_2.id
    assert dn_2._config_id == new_dn_2._config_id == "dn_2"
    assert dn_2._scope == new_dn_2._scope == Scope.CYCLE
    assert dn_2._owner_id == scenario.cycle.id
    assert new_dn_2._owner_id == new_scenario.cycle.id
    assert dn_2._parent_ids == {task_1.id, task_2.id}
    assert new_dn_2._parent_ids == {new_task_1.id, new_task_2.id}
    assert dn_2._last_edit_date == new_dn_2._last_edit_date
    assert dn_2._edits == new_dn_2._edits
    assert len(dn_2._properties) == len(new_dn_2._properties)
    for k, v in dn_2._properties.items():
        assert new_dn_2._properties[k] == v

    dn_3 = scenario.data_nodes["dn_3"]
    new_dn_3 = new_scenario.data_nodes["dn_3"]
    assert dn_3.id != new_dn_3.id
    assert dn_3._config_id == new_dn_3._config_id == "dn_3"
    assert dn_3._scope == new_dn_3._scope == Scope.SCENARIO
    assert dn_3._owner_id == scenario.id
    assert new_dn_3._owner_id == new_scenario.id
    assert dn_3._parent_ids == {task_2.id, task_3.id}
    assert new_dn_3._parent_ids == {new_task_2.id, new_task_3.id}
    assert dn_3._last_edit_date == new_dn_3._last_edit_date
    assert dn_3._edits == new_dn_3._edits
    assert len(dn_3._properties) == len(new_dn_3._properties)
    for k, v in dn_3._properties.items():
        assert new_dn_3._properties[k] == v

    dn_4 = scenario.data_nodes["dn_4"]
    new_dn_4 = new_scenario.data_nodes["dn_4"]
    assert dn_4.id != new_dn_4.id
    assert dn_4._config_id == new_dn_4._config_id == "dn_4"
    assert dn_4._scope == new_dn_4._scope == Scope.SCENARIO
    assert dn_4._owner_id == scenario.id
    assert new_dn_4._owner_id == new_scenario.id
    assert dn_4._parent_ids == {task_3.id}
    assert new_dn_4._parent_ids == {new_task_3.id}
    assert dn_4._last_edit_date == new_dn_4._last_edit_date
    assert dn_4._edits == new_dn_4._edits
    assert len(dn_4._properties) == len(new_dn_4._properties)
    for k, v in dn_4._properties.items():
        assert new_dn_4._properties[k] == v


def test_duplicate_to_new_cycle_with_existing_scenario():
    dn_cfg_1 = Config.configure_pickle_data_node("dn_1", scope=Scope.GLOBAL)
    dn_cfg_2 = Config.configure_pickle_data_node("dn_2", scope=Scope.CYCLE)
    dn_cfg_3 = Config.configure_pickle_data_node("dn_3", scope=Scope.SCENARIO)
    dn_cfg_4 = Config.configure_pickle_data_node("dn_4", scope=Scope.SCENARIO)
    t_cfg_1 = Config.configure_task("task_1", identity, input=[dn_cfg_1], output=[dn_cfg_2])
    t_cfg_2 = Config.configure_task("task_2", identity, input=[dn_cfg_2], output=[dn_cfg_3])
    t_cfg_3 = Config.configure_task("task_3", identity, input=[dn_cfg_3], output=[dn_cfg_4])
    s_cfg_1 = Config.configure_scenario("scenario_1", [t_cfg_1, t_cfg_2, t_cfg_3], frequency=Frequency.DAILY)
    creation_date = datetime.now() - timedelta(days=2)
    new_creation_date = datetime.now()
    name = "original"
    existing_name = "existing"
    new_name = "new"

    scenario = _ScenarioManager._create(s_cfg_1, creation_date, name)
    existing_scenario = _ScenarioManager._create(s_cfg_1, new_creation_date, existing_name)

    assert len(_CycleManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 6
    assert len(_DataManager._get_all()) == 7
    new_scenario = _ScenarioDuplicator(scenario, False).duplicate(new_creation_date, new_name)

    assert len(_CycleManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 8
    assert len(_DataManager._get_all()) == 9

    # Check scenario attributes
    assert scenario.id != new_scenario.id != existing_scenario.id
    assert scenario.config_id == new_scenario.config_id == "scenario_1"
    assert scenario.name == name
    assert new_scenario.name == new_name
    assert scenario.creation_date == creation_date
    assert new_scenario.creation_date == new_creation_date
    assert scenario.cycle.id != new_scenario.cycle.id == existing_scenario.cycle.id

    # Check tasks attributes
    assert len(scenario.tasks) == len(new_scenario.tasks) == 3
    task_1 = scenario.tasks["task_1"]
    existing_task_1 = existing_scenario.tasks["task_1"]
    new_task_1 = new_scenario.tasks["task_1"]
    assert existing_task_1 == new_task_1
    assert existing_task_1.id == new_task_1.id
    assert task_1._config_id == existing_task_1._config_id == new_task_1._config_id == "task_1"
    assert task_1._owner_id == scenario.cycle.id
    assert existing_task_1._owner_id == new_task_1._owner_id == existing_scenario.cycle.id
    assert task_1._parent_ids == {scenario.id}
    assert existing_task_1._parent_ids == new_task_1._parent_ids == {existing_scenario.id, new_scenario.id}
    assert task_1._function == existing_task_1._function == new_task_1._function
    assert task_1._skippable == existing_task_1._skippable == new_task_1._skippable is False
    assert task_1._properties == existing_task_1._properties == new_task_1._properties == {}

    task_2 = scenario.tasks["task_2"]
    existing_task_2 = existing_scenario.tasks["task_2"]
    new_task_2 = new_scenario.tasks["task_2"]
    assert task_2.id != new_task_2.id
    assert task_2._config_id == new_task_2._config_id == "task_2"
    assert task_2._owner_id == scenario.id
    assert new_task_2._owner_id == new_scenario.id
    assert task_2._parent_ids == {scenario.id}
    assert new_task_2._parent_ids == {new_scenario.id}
    assert task_2._function == new_task_2._function
    assert task_2._skippable == new_task_2._skippable is False
    assert task_2._properties == new_task_2._properties == {}

    task_3 = scenario.tasks["task_3"]
    new_task_3 = new_scenario.tasks["task_3"]
    assert task_3.id != new_task_3.id
    assert task_3._config_id == new_task_3._config_id == "task_3"
    assert task_3._owner_id == scenario.id
    assert new_task_3._owner_id == new_scenario.id
    assert task_3._parent_ids == {scenario.id}
    assert new_task_3._parent_ids == {new_scenario.id}
    assert task_3._function == new_task_3._function
    assert task_3._skippable == new_task_3._skippable is False
    assert task_3._properties == new_task_3._properties == {}

    # Check data node attributes
    assert len(scenario.data_nodes) == len(new_scenario.data_nodes) == 4
    dn_1 = scenario.data_nodes["dn_1"]
    new_dn_1 = new_scenario.data_nodes["dn_1"]
    assert dn_1.id == new_dn_1.id
    assert dn_1._config_id == new_dn_1._config_id == "dn_1"
    assert dn_1._scope == new_dn_1._scope == Scope.GLOBAL
    assert dn_1._owner_id == new_dn_1._owner_id is None
    assert dn_1._parent_ids == new_dn_1._parent_ids == {task_1.id, new_task_1.id}
    assert dn_1._last_edit_date == new_dn_1._last_edit_date
    assert dn_1._edits == new_dn_1._edits
    assert len(dn_1._properties) == len(new_dn_1._properties)
    for k, v in dn_1._properties.items():
        assert new_dn_1._properties[k] == v

    dn_2 = scenario.dn_2
    existing_dn_2 = existing_scenario.dn_2
    new_dn_2 = new_scenario.dn_2
    assert dn_2.id != new_dn_2.id == existing_dn_2.id
    assert dn_2._config_id == existing_dn_2._config_id == new_dn_2._config_id == "dn_2"
    assert dn_2._scope == existing_dn_2._scope == new_dn_2._scope == Scope.CYCLE
    assert dn_2._owner_id == scenario.cycle.id
    assert existing_dn_2._owner_id == new_dn_2._owner_id == new_scenario.cycle.id
    assert dn_2._parent_ids == {task_1.id, task_2.id}
    assert existing_dn_2._parent_ids == new_dn_2._parent_ids == {new_task_1.id, new_task_2.id, existing_task_2.id}
    assert dn_2._last_edit_date == new_dn_2._last_edit_date
    assert dn_2._edits == new_dn_2._edits
    assert len(dn_2._properties) == len(new_dn_2._properties)
    for k, v in dn_2._properties.items():
        if k == "path":
            assert new_dn_2._properties[k] == existing_dn_2._properties[k] != v
        else:
            assert new_dn_2._properties[k] == existing_dn_2._properties[k] == v

    dn_3 = scenario.data_nodes["dn_3"]
    existing_dn_3 = existing_scenario.data_nodes["dn_3"]
    new_dn_3 = new_scenario.data_nodes["dn_3"]
    assert dn_3.id != new_dn_3.id != existing_dn_3.id
    assert dn_3._config_id == new_dn_3._config_id == existing_dn_3._config_id == "dn_3"
    assert dn_3._scope == new_dn_3._scope == existing_dn_3._scope == Scope.SCENARIO
    assert dn_3._owner_id == scenario.id
    assert existing_dn_3._owner_id != new_dn_3._owner_id == new_scenario.id
    assert dn_3._parent_ids == {task_2.id, task_3.id}
    assert new_dn_3._parent_ids == {new_task_2.id, new_task_3.id}
    assert dn_3._last_edit_date == new_dn_3._last_edit_date
    assert dn_3._edits == new_dn_3._edits
    assert len(dn_3._properties) == len(new_dn_3._properties)
    for k, v in dn_3._properties.items():
        assert new_dn_3._properties[k] == v

    dn_4 = scenario.data_nodes["dn_4"]
    new_dn_4 = new_scenario.data_nodes["dn_4"]
    assert dn_4.id != new_dn_4.id
    assert dn_4._config_id == new_dn_4._config_id == "dn_4"
    assert dn_4._scope == new_dn_4._scope == Scope.SCENARIO
    assert dn_4._owner_id == scenario.id
    assert new_dn_4._owner_id == new_scenario.id
    assert dn_4._parent_ids == {task_3.id}
    assert new_dn_4._parent_ids == {new_task_3.id}
    assert dn_4._last_edit_date == new_dn_4._last_edit_date
    assert dn_4._edits == new_dn_4._edits
    assert len(dn_4._properties) == len(new_dn_4._properties)
    for k, v in dn_4._properties.items():
        assert new_dn_4._properties[k] == v


def test_duplicate_with_all_global_dn():
    dn_config_1 = Config.configure_pickle_data_node("dn_1", scope=Scope.GLOBAL)
    dn_config_2 = Config.configure_pickle_data_node("dn_2", scope=Scope.GLOBAL)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    scenario_config_1 = Config.configure_scenario("scenario_1", [task_config_1], frequency=Frequency.DAILY)
    scenario = _ScenarioManager._create(scenario_config_1, datetime.now() - timedelta(days=10), "original")

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1

    new_scenario = _ScenarioDuplicator(scenario, False).duplicate(datetime.now(), "new")

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 1

    # Check scenario attributes
    assert scenario.id != new_scenario.id
    assert scenario.config_id == new_scenario.config_id == "scenario_1"
    assert scenario.name == "original"
    assert new_scenario.name == "new"
    assert scenario.creation_date != new_scenario.creation_date
    assert scenario.cycle.id != new_scenario.cycle.id

    # Check tasks attributes
    assert len(scenario.tasks) == len(new_scenario.tasks) == 1
    task_1 = scenario.tasks["task_1"]
    new_task_1 = new_scenario.tasks["task_1"]
    assert task_1 == new_task_1
    assert task_1.id == new_task_1.id
    assert task_1._config_id == new_task_1._config_id == "task_1"
    assert task_1._owner_id == new_task_1._owner_id is None
    assert task_1._parent_ids == new_task_1._parent_ids == {scenario.id, new_scenario.id}
    assert task_1._function == new_task_1._function
    assert task_1._skippable == new_task_1._skippable is False
    assert task_1._properties == new_task_1._properties == {}

    # Check data node attributes
    assert len(scenario.data_nodes) == len(new_scenario.data_nodes) == 2
    dn_1 = scenario.data_nodes["dn_1"]
    new_dn_1 = new_scenario.data_nodes["dn_1"]
    assert dn_1.id == new_dn_1.id
    assert dn_1._config_id == new_dn_1._config_id == "dn_1"
    assert dn_1._scope == new_dn_1._scope == Scope.GLOBAL
    assert dn_1._owner_id == new_dn_1._owner_id is None
    assert dn_1._parent_ids == new_dn_1._parent_ids == {task_1.id, new_task_1.id}
    assert dn_1._last_edit_date == new_dn_1._last_edit_date
    assert dn_1._edits == new_dn_1._edits
    assert len(dn_1._properties) == len(new_dn_1._properties)
    for k, v in dn_1._properties.items():
        assert new_dn_1._properties[k] == v

    # Check data node attributes
    dn_2 = scenario.dn_2
    new_dn_2 = new_scenario.dn_2
    assert dn_2.id == new_dn_2.id
    assert dn_2._config_id == new_dn_2._config_id == "dn_2"
    assert dn_2._scope == new_dn_2._scope == Scope.GLOBAL
    assert dn_2._owner_id == new_dn_2._owner_id is None
    assert dn_2._parent_ids == {task_1.id}
    assert dn_2._last_edit_date == new_dn_2._last_edit_date
    assert dn_2._edits == new_dn_2._edits
    assert len(dn_2._properties) == len(new_dn_2._properties)
    for k, v in dn_2._properties.items():
        assert new_dn_2._properties[k] == v


def test_data_duplication():
    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    dn_config_2 = Config.configure_json_data_node("dn_2")
    dn_config_3 = Config.configure_generic_data_node("dn_3", read_fct=print)
    dn_config_4 = Config.configure_in_memory_data_node("dn_4")
    scenario_config_1 = Config.configure_scenario(
        "scenario_1",
        [],
        additional_data_node_configs=[dn_config_1, dn_config_2, dn_config_3, dn_config_4])
    scenario = _ScenarioManager._create(scenario_config_1)

    with mock.patch("taipy.core.data._data_duplicator._DataDuplicator.duplicate_data") as mck:
        new_scenario = _ScenarioDuplicator(scenario, True).duplicate(datetime.now(), "new")
        mck.assert_has_calls([call(new_scenario.dn_1), call(new_scenario.dn_2)], any_order=True)

    with mock.patch("taipy.core.data._data_duplicator._DataDuplicator.duplicate_data") as mck:
        new_scenario = _ScenarioDuplicator(scenario, {"dn_1", "dn_3"}).duplicate(datetime.now(), "new")
        mck.assert_called_once_with(new_scenario.dn_1)
