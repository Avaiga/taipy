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
from unittest import mock

import pytest

from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.cycle.cycle import Cycle, CycleId
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import DataNode, InMemoryDataNode
from src.taipy.core.data.pickle import PickleDataNode
from src.taipy.core.exceptions.exceptions import SequenceTaskDoesNotExistInScenario
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.scenario.scenario_id import ScenarioId
from src.taipy.core.sequence.sequence import Sequence
from src.taipy.core.sequence.sequence_id import SequenceId
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task, TaskId
from taipy.config import Frequency
from taipy.config.common.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


def test_create_scenario(cycle, current_datetime):
    scenario_1 = Scenario("foo", set(), {"key": "value"}, is_primary=True, cycle=cycle)
    assert scenario_1.id is not None
    assert scenario_1.config_id == "foo"
    assert scenario_1.tasks == {}
    assert scenario_1.additional_data_nodes == {}
    assert scenario_1.data_nodes == {}
    assert scenario_1.sequences == {}
    assert scenario_1.properties == {"key": "value"}
    assert scenario_1.key == "value"
    assert scenario_1.creation_date is not None
    assert scenario_1.is_primary
    assert scenario_1.cycle == cycle
    assert scenario_1.tags == set()
    assert scenario_1.get_simple_label() == scenario_1.config_id
    with mock.patch("src.taipy.core.get") as get_mck:

        class MockOwner:
            label = "owner_label"

            def get_label(self):
                return self.label

        get_mck.return_value = MockOwner()
        assert scenario_1.get_label() == "owner_label > " + scenario_1.config_id

    scenario_2 = Scenario("bar", set(), {}, set(), ScenarioId("baz"), creation_date=current_datetime)
    assert scenario_2.id == "baz"
    assert scenario_2.config_id == "bar"
    assert scenario_2.tasks == {}
    assert scenario_2.additional_data_nodes == {}
    assert scenario_2.data_nodes == {}
    assert scenario_2.sequences == {}
    assert scenario_2.properties == {}
    assert scenario_2.creation_date == current_datetime
    assert not scenario_2.is_primary
    assert scenario_2.cycle is None
    assert scenario_2.tags == set()
    assert scenario_2.get_simple_label() == scenario_2.config_id
    assert scenario_2.get_label() == scenario_2.config_id

    dn_1 = PickleDataNode("xyz", Scope.SCENARIO)
    dn_2 = PickleDataNode("abc", Scope.SCENARIO)
    task = Task("qux", {}, print, [dn_1])

    scenario_3 = Scenario("quux", set([task]), {}, set([dn_2]), sequences={"acb": {"tasks": [task]}})
    sequence = scenario_3.sequences["acb"]
    assert scenario_3.id is not None
    assert scenario_3.config_id == "quux"
    assert len(scenario_3.tasks) == 1
    assert len(scenario_3.additional_data_nodes) == 1
    assert len(scenario_3.data_nodes) == 2
    assert len(scenario_3.sequences) == 1
    assert scenario_3.qux == task
    assert scenario_3.xyz == dn_1
    assert scenario_3.abc == dn_2
    assert scenario_3.acb == sequence
    assert scenario_3.properties == {}
    assert scenario_3.tags == set()

    with pytest.raises(InvalidConfigurationId):
        Scenario("foo bar", [], {})

    input_1 = PickleDataNode("input_1", Scope.SCENARIO)
    output_1 = PickleDataNode("output_1", Scope.SCENARIO)
    output_2 = PickleDataNode("output_2", Scope.SCENARIO)
    additional_dn_1 = PickleDataNode("additional_1", Scope.SCENARIO)
    additional_dn_2 = PickleDataNode("additional_2", Scope.SCENARIO)
    task_1 = Task("task_1", {}, print, [input_1], [output_1], TaskId("task_id_1"))
    task_2 = Task("task_2", {}, print, [output_1], [output_2], TaskId("task_id_2"))

    data_manager = _DataManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()

    data_manager._set(input_1)
    data_manager._set(output_1)
    data_manager._set(output_2)
    data_manager._set(additional_dn_1)
    data_manager._set(additional_dn_2)
    task_manager._set(task_1)
    task_manager._set(task_2)

    scenario_4 = Scenario(
        "scenario_4",
        set([task_1]),
        {},
    )
    scenario_4.sequences = {"sequence_1": {"tasks": [task_1]}, "sequence_2": {"tasks": []}}

    sequence_1 = scenario_4.sequences["sequence_1"]
    sequence_2 = scenario_4.sequences["sequence_2"]
    assert scenario_4.id is not None
    assert scenario_4.config_id == "scenario_4"
    assert len(scenario_4.tasks) == 1
    assert len(scenario_4.additional_data_nodes) == 0
    assert len(scenario_4.data_nodes) == 2
    assert scenario_4.tasks.keys() == {task_1.config_id}
    assert scenario_4.additional_data_nodes == {}
    assert scenario_4.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
    }
    assert scenario_4.sequences == {"sequence_1": sequence_1, "sequence_2": sequence_2}

    scenario_5 = Scenario("scenario_5", set([task_1, task_2]), {})
    scenario_5.add_sequences({"sequence_1": {"tasks": [task_1]}, "sequence_2": {"tasks": [task_1, task_2]}})
    sequence_1 = scenario_5.sequences["sequence_1"]
    sequence_2 = scenario_5.sequences["sequence_2"]
    assert scenario_5.id is not None
    assert scenario_5.config_id == "scenario_5"
    assert len(scenario_5.tasks) == 2
    assert len(scenario_5.additional_data_nodes) == 0
    assert len(scenario_5.data_nodes) == 3
    assert scenario_5.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_5.additional_data_nodes == {}
    assert scenario_5.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        output_2.config_id: output_2,
    }
    assert scenario_5.sequences == {"sequence_1": sequence_1, "sequence_2": sequence_2}
    scenario_5.remove_sequences(["sequence_2"])
    assert scenario_5.sequences == {"sequence_1": sequence_1}
    scenario_5.remove_sequences(["sequence_1"])
    assert scenario_5.sequences == {}

    scenario_6 = Scenario("scenario_6", set(), {}, set([additional_dn_1]))
    assert scenario_6.id is not None
    assert scenario_6.config_id == "scenario_6"
    assert len(scenario_6.tasks) == 0
    assert len(scenario_6.additional_data_nodes) == 1
    assert len(scenario_6.data_nodes) == 1
    assert scenario_6.tasks == {}
    assert scenario_6.additional_data_nodes == {additional_dn_1.config_id: additional_dn_1}
    assert scenario_6.data_nodes == {additional_dn_1.config_id: additional_dn_1}

    scenario_7 = Scenario("scenario_7", set(), {}, set([additional_dn_1, additional_dn_2]))
    assert scenario_7.id is not None
    assert scenario_7.config_id == "scenario_7"
    assert len(scenario_7.tasks) == 0
    assert len(scenario_7.additional_data_nodes) == 2
    assert len(scenario_7.data_nodes) == 2
    assert scenario_7.tasks == {}
    assert scenario_7.additional_data_nodes == {
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }
    assert scenario_7.data_nodes == {
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }

    scenario_8 = Scenario("scenario_8", set([task_1]), {}, set([additional_dn_1]))
    assert scenario_8.id is not None
    assert scenario_8.config_id == "scenario_8"
    assert len(scenario_8.tasks) == 1
    assert len(scenario_8.additional_data_nodes) == 1
    assert len(scenario_8.data_nodes) == 3
    assert scenario_8.tasks.keys() == {task_1.config_id}
    assert scenario_8.additional_data_nodes == {
        additional_dn_1.config_id: additional_dn_1,
    }
    assert scenario_8.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        additional_dn_1.config_id: additional_dn_1,
    }

    scenario_9 = Scenario("scenario_9", set([task_1, task_2]), {}, set([additional_dn_1, additional_dn_2]))
    assert scenario_9.id is not None
    assert scenario_9.config_id == "scenario_9"
    assert len(scenario_9.tasks) == 2
    assert len(scenario_9.additional_data_nodes) == 2
    assert len(scenario_9.data_nodes) == 5
    assert scenario_9.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_9.additional_data_nodes == {
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }
    assert scenario_9.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        output_2.config_id: output_2,
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }


def test_raise_sequence_tasks_not_in_scenario(data_node):
    task_1 = Task("task_1", {}, print, output=[data_node])
    task_2 = Task("task_2", {}, print, input=[data_node])

    with pytest.raises(SequenceTaskDoesNotExistInScenario) as err:
        Scenario("scenario", [], {}, sequences={"sequence": {"tasks": [task_1]}}, scenario_id="SCENARIO_scenario")
    assert err.value.args == ([task_1.id], "sequence", "SCENARIO_scenario")

    with pytest.raises(SequenceTaskDoesNotExistInScenario) as err:
        Scenario(
            "scenario",
            [task_1],
            {},
            sequences={"sequence": {"tasks": [task_1, task_2]}},
            scenario_id="SCENARIO_scenario",
        )
    assert err.value.args == ([task_2.id], "sequence", "SCENARIO_scenario")

    Scenario("scenario", [task_1], {}, sequences={"sequence": {"tasks": [task_1]}})
    Scenario(
        "scenario",
        [task_1, task_2],
        {},
        sequences={"sequence_1": {"tasks": [task_1]}, "sequence_2": {"tasks": [task_1, task_2]}},
    )

    scenario = Scenario("scenario", [], {})

    scenario_manager = _ScenarioManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()

    scenario_manager._set(scenario)
    task_manager._set(task_1)
    task_manager._set(task_2)

    scenario.add_sequences({"sequence_1": {}})

    with pytest.raises(SequenceTaskDoesNotExistInScenario) as err:
        scenario.add_sequences({"sequence_2": {"tasks": [task_1]}})
    assert err.value.args == ([task_1.id], "sequence_2", scenario.id)

    scenario.tasks = [task_1]

    scenario.add_sequences({"sequence_2": {"tasks": [task_1]}})

    with pytest.raises(SequenceTaskDoesNotExistInScenario) as err:
        scenario.add_sequences({"sequence_3": {"tasks": [task_2]}})
    assert err.value.args == ([task_2.id], "sequence_3", scenario.id)

    with pytest.raises(SequenceTaskDoesNotExistInScenario) as err:
        scenario.add_sequences({"sequence_4": {"tasks": [task_1, task_2]}})
    assert err.value.args == ([task_2.id], "sequence_4", scenario.id)

    scenario.tasks = [task_1, task_2]
    scenario.add_sequences({"sequence_5": {"tasks": [task_1, task_2]}})


def test_add_property_to_scenario():
    scenario = Scenario("foo", [], {"key": "value"})
    assert scenario.properties == {"key": "value"}
    assert scenario.key == "value"

    scenario.properties["new_key"] = "new_value"

    assert scenario.properties == {"key": "value", "new_key": "new_value"}
    assert scenario.key == "value"
    assert scenario.new_key == "new_value"


def test_add_cycle_to_scenario(cycle):
    scenario = Scenario("foo", [], {})
    assert scenario.cycle is None
    _CycleManagerFactory._build_manager()._set(cycle)
    scenario.cycle = cycle

    assert scenario.cycle == cycle


def test_add_and_remove_subscriber():
    scenario = Scenario("foo", [], {})

    scenario._add_subscriber(print)
    assert len(scenario.subscribers) == 1

    scenario._remove_subscriber(print)
    assert len(scenario.subscribers) == 0


def test_add_and_remove_tag():
    scenario = Scenario("foo", [], {})

    assert len(scenario.tags) == 0
    scenario._add_tag("tag")
    assert len(scenario.tags) == 1

    scenario._remove_tag("tag")
    assert len(scenario.tags) == 0


def test_auto_set_and_reload(cycle, current_datetime, task, data_node):
    scenario_1 = Scenario(
        "foo",
        set(),
        {"name": "bar"},
        set(),
        creation_date=current_datetime,
        is_primary=True,
        cycle=None,
    )
    additional_dn = InMemoryDataNode("additional_dn", Scope.SCENARIO)
    example_date = datetime.fromisoformat("2021-11-11T11:11:01.000001")
    tmp_cycle = Cycle(
        Frequency.WEEKLY,
        {},
        creation_date=example_date,
        start_date=example_date,
        end_date=example_date,
        name="cc",
        id=CycleId("tmp_cc_id"),
    )

    sequence_1_name = "sequence_1"
    sequence_1 = Sequence({}, [], SequenceId(f"SEQUENCE_{sequence_1_name}_{scenario_1.id}"))

    tmp_sequence_name = "tmp_sequence"
    tmp_sequence = Sequence(
        {},
        [],
        SequenceId(f"SEQUENCE_{tmp_sequence_name}_{scenario_1.id}"),
    )

    _TaskManagerFactory._build_manager()._set(task)
    _DataManagerFactory._build_manager()._set(data_node)
    _DataManagerFactory._build_manager()._set(additional_dn)
    _CycleManagerFactory._build_manager()._set(cycle)
    scenario_manager = _ScenarioManagerFactory._build_manager()
    cycle_manager = _CycleManagerFactory._build_manager()
    cycle_manager._set(cycle)
    cycle_manager._set(tmp_cycle)
    scenario_manager._set(scenario_1)

    scenario_2 = scenario_manager._get(scenario_1)
    assert scenario_1.config_id == "foo"
    assert scenario_2.config_id == "foo"

    # auto set & reload on name attribute
    assert scenario_1.name == "bar"
    assert scenario_2.name == "bar"
    scenario_1.name = "zab"
    assert scenario_1.name == "zab"
    assert scenario_2.name == "zab"
    scenario_2.name = "baz"
    assert scenario_1.name == "baz"
    assert scenario_2.name == "baz"

    # auto set & reload on sequences attribute
    assert len(scenario_1.sequences) == 0
    assert len(scenario_2.sequences) == 0
    scenario_1.sequences = {tmp_sequence_name: {}}
    assert len(scenario_1.sequences) == 1
    assert scenario_1.sequences[tmp_sequence_name] == tmp_sequence
    assert len(scenario_2.sequences) == 1
    assert scenario_2.sequences[tmp_sequence_name] == tmp_sequence
    scenario_2.add_sequences({sequence_1_name: {}})
    assert len(scenario_1.sequences) == 2
    assert scenario_1.sequences == {sequence_1_name: sequence_1, tmp_sequence_name: tmp_sequence}
    assert len(scenario_2.sequences) == 2
    assert scenario_2.sequences == {sequence_1_name: sequence_1, tmp_sequence_name: tmp_sequence}
    scenario_2.remove_sequences([tmp_sequence_name])
    assert len(scenario_1.sequences) == 1
    assert scenario_1.sequences == {sequence_1_name: sequence_1}
    assert len(scenario_2.sequences) == 1
    assert scenario_2.sequences == {sequence_1_name: sequence_1}

    assert len(scenario_1.tasks) == 0
    assert len(scenario_1.data_nodes) == 0
    scenario_1.tasks = {task}
    assert len(scenario_1.tasks) == 1
    assert scenario_1.tasks[task.config_id] == task
    assert len(scenario_1.data_nodes) == 2
    assert len(scenario_2.tasks) == 1
    assert scenario_2.tasks[task.config_id] == task
    assert len(scenario_2.data_nodes) == 2

    assert len(scenario_1.additional_data_nodes) == 0
    scenario_1.additional_data_nodes = {additional_dn}
    assert len(scenario_1.additional_data_nodes) == 1
    assert scenario_1.additional_data_nodes[additional_dn.config_id] == additional_dn
    assert len(scenario_1.data_nodes) == 3
    assert len(scenario_2.additional_data_nodes) == 1
    assert scenario_2.additional_data_nodes[additional_dn.config_id] == additional_dn
    assert len(scenario_2.data_nodes) == 3

    new_datetime = current_datetime + timedelta(1)
    new_datetime_1 = current_datetime + timedelta(2)

    # auto set & reload on name attribute
    assert scenario_1.creation_date == current_datetime
    assert scenario_2.creation_date == current_datetime
    scenario_1.creation_date = new_datetime_1
    assert scenario_1.creation_date == new_datetime_1
    assert scenario_2.creation_date == new_datetime_1
    scenario_2.creation_date = new_datetime
    assert scenario_1.creation_date == new_datetime
    assert scenario_2.creation_date == new_datetime

    # auto set & reload on cycle attribute
    assert scenario_1.cycle is None
    assert scenario_2.cycle is None
    scenario_1.cycle = tmp_cycle
    assert scenario_1.cycle == tmp_cycle
    assert scenario_2.cycle == tmp_cycle
    scenario_2.cycle = cycle
    assert scenario_1.cycle == cycle
    assert scenario_2.cycle == cycle

    # auto set & reload on is_primary attribute
    assert scenario_1.is_primary
    assert scenario_2.is_primary
    scenario_1.is_primary = False
    assert not scenario_1.is_primary
    assert not scenario_2.is_primary
    scenario_2.is_primary = True
    assert scenario_1.is_primary
    assert scenario_2.is_primary

    # auto set & reload on subscribers attribute
    assert len(scenario_1.subscribers) == 0
    assert len(scenario_2.subscribers) == 0
    scenario_1.subscribers.append(_Subscriber(print, []))
    assert len(scenario_1.subscribers) == 1
    assert len(scenario_2.subscribers) == 1
    scenario_2.subscribers.append(_Subscriber(print, []))
    assert len(scenario_1.subscribers) == 2
    assert len(scenario_2.subscribers) == 2

    scenario_1.subscribers.clear()
    assert len(scenario_1.subscribers) == 0
    assert len(scenario_2.subscribers) == 0

    scenario_1.subscribers.extend([_Subscriber(print, []), _Subscriber(map, [])])
    assert len(scenario_1.subscribers) == 2
    assert len(scenario_2.subscribers) == 2

    scenario_1.subscribers.remove(_Subscriber(print, []))
    assert len(scenario_1.subscribers) == 1
    assert len(scenario_2.subscribers) == 1

    scenario_1.subscribers + print + len
    assert len(scenario_1.subscribers) == 3
    assert len(scenario_2.subscribers) == 3

    scenario_1.subscribers = []
    assert len(scenario_1.subscribers) == 0
    assert len(scenario_2.subscribers) == 0

    assert len(scenario_1.tags) == 0
    scenario_1.tags = {"hi"}
    assert len(scenario_1.tags) == 1
    assert len(scenario_2.tags) == 1

    # auto set & reload on properties attribute
    assert scenario_1.properties == {"name": "baz"}
    assert scenario_2.properties == {"name": "baz"}
    scenario_1._properties["qux"] = 4
    assert scenario_1.properties["qux"] == 4
    assert scenario_2.properties["qux"] == 4

    assert scenario_1.properties == {"name": "baz", "qux": 4}
    assert scenario_2.properties == {"name": "baz", "qux": 4}
    scenario_2._properties["qux"] = 5
    assert scenario_1.properties["qux"] == 5
    assert scenario_2.properties["qux"] == 5

    scenario_1.properties["temp_key_1"] = "temp_value_1"
    scenario_1.properties["temp_key_2"] = "temp_value_2"
    assert scenario_1.properties == {
        "name": "baz",
        "qux": 5,
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    assert scenario_2.properties == {
        "name": "baz",
        "qux": 5,
        "temp_key_1": "temp_value_1",
        "temp_key_2": "temp_value_2",
    }
    scenario_1.properties.pop("temp_key_1")
    assert "temp_key_1" not in scenario_1.properties.keys()
    assert "temp_key_1" not in scenario_1.properties.keys()
    assert scenario_1.properties == {
        "name": "baz",
        "qux": 5,
        "temp_key_2": "temp_value_2",
    }
    assert scenario_2.properties == {
        "name": "baz",
        "qux": 5,
        "temp_key_2": "temp_value_2",
    }
    scenario_2.properties.pop("temp_key_2")
    assert scenario_1.properties == {"name": "baz", "qux": 5}
    assert scenario_2.properties == {"name": "baz", "qux": 5}
    assert "temp_key_2" not in scenario_1.properties.keys()
    assert "temp_key_2" not in scenario_2.properties.keys()

    scenario_1.properties["temp_key_3"] = 0
    assert scenario_1.properties == {"name": "baz", "qux": 5, "temp_key_3": 0}
    assert scenario_2.properties == {"name": "baz", "qux": 5, "temp_key_3": 0}
    scenario_1.properties.update({"temp_key_3": 1})
    assert scenario_1.properties == {"name": "baz", "qux": 5, "temp_key_3": 1}
    assert scenario_2.properties == {"name": "baz", "qux": 5, "temp_key_3": 1}
    scenario_1.properties.update(dict())
    assert scenario_1.properties == {"name": "baz", "qux": 5, "temp_key_3": 1}
    assert scenario_2.properties == {"name": "baz", "qux": 5, "temp_key_3": 1}
    scenario_1.properties["temp_key_4"] = 0
    scenario_1.properties["temp_key_5"] = 0

    with scenario_1 as scenario:
        assert scenario.config_id == "foo"
        assert len(scenario.tasks) == 1
        assert len(scenario.sequences) == 1
        assert scenario.sequences["sequence_1"] == sequence_1
        assert scenario.tasks[task.config_id] == task
        assert len(scenario.additional_data_nodes) == 1
        assert scenario.additional_data_nodes[additional_dn.config_id] == additional_dn
        assert scenario.creation_date == new_datetime
        assert scenario.cycle == cycle
        assert scenario.is_primary
        assert len(scenario.subscribers) == 0
        assert len(scenario.tags) == 1
        assert scenario._is_in_context
        assert scenario.name == "baz"
        assert scenario.properties["qux"] == 5
        assert scenario.properties["temp_key_3"] == 1
        assert scenario.properties["temp_key_4"] == 0
        assert scenario.properties["temp_key_5"] == 0

        new_datetime_2 = new_datetime + timedelta(5)
        scenario.config_id = "foo"
        scenario.tasks = set()
        scenario.additional_data_nodes = set()
        scenario.remove_sequences([sequence_1_name])
        scenario.creation_date = new_datetime_2
        scenario.cycle = None
        scenario.is_primary = False
        scenario.subscribers = [print]
        scenario.tags = None
        scenario.name = "qux"
        scenario.properties["qux"] = 9
        scenario.properties.pop("temp_key_3")
        scenario.properties.pop("temp_key_4")
        scenario.properties.update({"temp_key_4": 1})
        scenario.properties.update({"temp_key_5": 2})
        scenario.properties.pop("temp_key_5")
        scenario.properties.update(dict())

        assert scenario.config_id == "foo"
        assert len(scenario.sequences) == 1
        assert scenario.sequences[sequence_1_name] == sequence_1
        assert len(scenario.tasks) == 1
        assert scenario.tasks[task.config_id] == task
        assert len(scenario.additional_data_nodes) == 1
        assert scenario.additional_data_nodes[additional_dn.config_id] == additional_dn
        assert scenario.creation_date == new_datetime
        assert scenario.cycle == cycle
        assert scenario.is_primary
        assert len(scenario.subscribers) == 0
        assert len(scenario.tags) == 1
        assert scenario._is_in_context
        assert scenario.name == "baz"
        assert scenario.properties["qux"] == 5
        assert scenario.properties["temp_key_3"] == 1
        assert scenario.properties["temp_key_4"] == 0
        assert scenario.properties["temp_key_5"] == 0

    assert scenario_1.config_id == "foo"
    assert len(scenario_1.sequences) == 0
    assert len(scenario_1.tasks) == 0
    assert len(scenario_1.additional_data_nodes) == 0
    assert scenario_1.tasks == {}
    assert scenario_1.additional_data_nodes == {}
    assert scenario_1.creation_date == new_datetime_2
    assert scenario_1.cycle is None
    assert not scenario_1.is_primary
    assert len(scenario_1.subscribers) == 1
    assert len(scenario_1.tags) == 0
    assert not scenario_1._is_in_context
    assert scenario_1.properties["qux"] == 9
    assert "temp_key_3" not in scenario_1.properties.keys()
    assert scenario_1.properties["temp_key_4"] == 1
    assert "temp_key_5" not in scenario_1.properties.keys()


def test_is_deletable():
    with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_deletable") as mock_submit:
        scenario = Scenario("foo", [], {})
        scenario.is_deletable()
        mock_submit.assert_called_once_with(scenario)


def test_submit_scenario():
    with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mock_submit:
        scenario = Scenario("foo", [], {})
        scenario.submit(force=False)
        mock_submit.assert_called_once_with(scenario, None, False, False, None)


def test_subscribe_scenario():
    with mock.patch("src.taipy.core.subscribe_scenario") as mock_subscribe:
        scenario = Scenario("foo", [], {})
        scenario.subscribe(None)
        mock_subscribe.assert_called_once_with(None, None, scenario)


def test_unsubscribe_scenario():
    with mock.patch("src.taipy.core.unsubscribe_scenario") as mock_unsubscribe:
        scenario = Scenario("foo", [], {})
        scenario.unsubscribe(None)
        mock_unsubscribe.assert_called_once_with(None, None, scenario)


def test_add_tag_scenario():
    with mock.patch("src.taipy.core.tag") as mock_add_tag:
        scenario = Scenario("foo", [], {})
        scenario.add_tag("tag")
        mock_add_tag.assert_called_once_with(scenario, "tag")


def test_remove_tag_scenario():
    with mock.patch("src.taipy.core.untag") as mock_remove_tag:
        scenario = Scenario("foo", [], {})
        scenario.remove_tag("tag")
        mock_remove_tag.assert_called_once_with(scenario, "tag")


def test_get_inputs_outputs_intermediate_data_nodes():
    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = DataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3, data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4}, {}, set(), ScenarioId("s1"))
    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert scenario.get_inputs() == {data_node_1, data_node_2}
    assert scenario.get_outputs() == {data_node_6, data_node_7}
    assert scenario.get_intermediate() == {data_node_3, data_node_4, data_node_5}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4}, {}, set(), ScenarioId("s1"))
    # s1 ---      t2 ---> s5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    assert scenario.get_inputs() == {data_node_1, data_node_2}
    assert scenario.get_outputs() == {data_node_6, data_node_7}
    assert scenario.get_intermediate() == {data_node_4, data_node_5}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = DataNode("d8", Scope.SCENARIO, "s8")
    data_node_9 = DataNode("d9", Scope.SCENARIO, "s9")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [data_node_8], [data_node_9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [data_node_7, data_node_9], id=TaskId("t6"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4, task_5, task_6}, {}, set(), ScenarioId("s1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7 ---> t6
    #                                              |
    # s8 -------> t5 -------> s9 ------------------
    assert scenario.get_inputs() == {data_node_1, data_node_2, data_node_6, data_node_8}
    assert scenario.get_outputs() == set()
    assert scenario.get_intermediate() == {data_node_5, data_node_4, data_node_7, data_node_9}

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = DataNode("hugh", Scope.SCENARIO, "s8")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4, data_node_6], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_8], None, TaskId("t5"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4, task_5}, {}, set(), ScenarioId("sc1"))
    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5                   |
    # s8 ---> t5              s6 --|
    assert scenario.get_inputs() == {data_node_1, data_node_2, data_node_8, data_node_6}
    assert scenario.get_outputs() == {data_node_5, data_node_7}
    assert scenario.get_intermediate() == {data_node_4}


def test_is_ready_to_run():
    data_node_1 = PickleDataNode("foo", Scope.SCENARIO, "s1", properties={"default_data": 1})
    data_node_2 = PickleDataNode("bar", Scope.SCENARIO, "s2", properties={"default_data": 2})
    data_node_4 = PickleDataNode("qux", Scope.SCENARIO, "s4", properties={"default_data": 4})
    data_node_5 = PickleDataNode("quux", Scope.SCENARIO, "s5", properties={"default_data": 5})
    data_node_6 = PickleDataNode("quuz", Scope.SCENARIO, "s6", properties={"default_data": 6})
    data_node_7 = PickleDataNode("corge", Scope.SCENARIO, "s7", properties={"default_data": 7})
    data_node_8 = PickleDataNode("d8", Scope.SCENARIO, "s8", properties={"default_data": 8})
    data_node_9 = PickleDataNode("d9", Scope.SCENARIO, "s9", properties={"default_data": 9})
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [data_node_8], [data_node_9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [data_node_7, data_node_9], id=TaskId("t6"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4, task_5, task_6}, {}, set(), ScenarioId("s1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7 ---> t6
    #                                              |
    # s8 -------> t5 -------> s9 ------------------
    assert scenario.get_inputs() == {data_node_1, data_node_2, data_node_6, data_node_8}

    data_manager = _DataManagerFactory._build_manager()
    data_manager._delete_all()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7, data_node_8, data_node_9]:
        data_manager._set(dn)

    assert scenario.is_ready_to_run()

    data_node_1.edit_in_progress = True
    assert not scenario.is_ready_to_run()

    data_node_2.edit_in_progress = True
    assert not scenario.is_ready_to_run()

    data_node_6.edit_in_progress = True
    data_node_8.edit_in_progress = True
    assert not scenario.is_ready_to_run()

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    data_node_8.edit_in_progress = False
    assert scenario.is_ready_to_run()


def test_data_nodes_being_edited():
    data_node_1 = PickleDataNode("foo", Scope.SCENARIO, "s1", properties={"default_data": 1})
    data_node_2 = PickleDataNode("bar", Scope.SCENARIO, "s2", properties={"default_data": 2})
    data_node_4 = PickleDataNode("qux", Scope.SCENARIO, "s4", properties={"default_data": 4})
    data_node_5 = PickleDataNode("quux", Scope.SCENARIO, "s5", properties={"default_data": 5})
    data_node_6 = PickleDataNode("quuz", Scope.SCENARIO, "s6", properties={"default_data": 6})
    data_node_7 = PickleDataNode("corge", Scope.SCENARIO, "s7", properties={"default_data": 7})
    data_node_8 = PickleDataNode("d8", Scope.SCENARIO, "s8", properties={"default_data": 8})
    data_node_9 = PickleDataNode("d9", Scope.SCENARIO, "s9", properties={"default_data": 9})
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [data_node_8], [data_node_9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [data_node_7, data_node_9], id=TaskId("t6"))
    scenario = Scenario("scenario", {task_1, task_2, task_3, task_4, task_5, task_6}, {}, set(), ScenarioId("s1"))
    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7 ---> t6
    #                                              |
    # s8 -------> t5 -------> s9 ------------------

    data_manager = _DataManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_4, data_node_5, data_node_6, data_node_7, data_node_8, data_node_9]:
        data_manager._set(dn)

    assert len(scenario.data_nodes_being_edited()) == 0
    assert scenario.data_nodes_being_edited() == set()

    data_node_1.edit_in_progress = True
    assert len(scenario.data_nodes_being_edited()) == 1
    assert scenario.data_nodes_being_edited() == {data_node_1}

    data_node_2.edit_in_progress = True
    data_node_6.edit_in_progress = True
    data_node_8.edit_in_progress = True
    assert len(scenario.data_nodes_being_edited()) == 4
    assert scenario.data_nodes_being_edited() == {data_node_1, data_node_2, data_node_6, data_node_8}

    data_node_4.edit_in_progress = True
    data_node_5.edit_in_progress = True
    data_node_9.edit_in_progress = True
    assert len(scenario.data_nodes_being_edited()) == 7
    assert scenario.data_nodes_being_edited() == {
        data_node_1,
        data_node_2,
        data_node_4,
        data_node_5,
        data_node_6,
        data_node_8,
        data_node_9,
    }

    data_node_1.edit_in_progress = False
    data_node_2.edit_in_progress = False
    data_node_6.edit_in_progress = False
    data_node_8.edit_in_progress = False
    assert len(scenario.data_nodes_being_edited()) == 3
    assert scenario.data_nodes_being_edited() == {data_node_4, data_node_5, data_node_9}

    data_node_4.edit_in_progress = False
    data_node_5.edit_in_progress = False
    data_node_7.edit_in_progress = True
    assert len(scenario.data_nodes_being_edited()) == 2
    assert scenario.data_nodes_being_edited() == {data_node_7, data_node_9}

    data_node_7.edit_in_progress = False
    data_node_9.edit_in_progress = False
    assert len(scenario.data_nodes_being_edited()) == 0
    assert scenario.data_nodes_being_edited() == set()


def test_get_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, id=TaskId("t4"))
    scenario_1 = Scenario("scenario_1", {task_1, task_2, task_3, task_4}, {}, set(), ScenarioId("s1"))
    assert scenario_1.tasks == {"grault": task_1, "garply": task_2, "waldo": task_3, "fred": task_4}

    task_5 = Task("wallo", {}, print, id=TaskId("t5"))
    scenario_2 = Scenario("scenario_2", {task_1, task_2, task_3, task_4, task_5}, {}, set(), ScenarioId("s2"))
    assert scenario_2.tasks == {"grault": task_1, "garply": task_2, "waldo": task_3, "fred": task_4, "wallo": task_5}


def test_get_set_of_tasks():
    task_1 = Task("grault", {}, print, id=TaskId("t1"))
    task_2 = Task("garply", {}, print, id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, id=TaskId("t4"))
    scenario_1 = Scenario("scenario_1", {task_1, task_2, task_3, task_4}, {}, set(), ScenarioId("s1"))
    assert scenario_1._get_set_of_tasks() == {task_1, task_2, task_3, task_4}

    task_5 = Task("wallo", {}, print, id=TaskId("t5"))
    scenario_2 = Scenario("scenario_2", {task_1, task_2, task_3, task_4, task_5}, {}, set(), ScenarioId("s2"))
    assert scenario_2._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}


def test_get_sorted_tasks():
    def _assert_equal(tasks_a, tasks_b) -> bool:
        if len(tasks_a) != len(tasks_b):
            return False
        for i in range(len(tasks_a)):
            task_a, task_b = tasks_a[i], tasks_b[i]
            if isinstance(task_a, list) and isinstance(task_b, list):
                if not _assert_equal(task_a, task_b):
                    return False
            elif isinstance(task_a, list) or isinstance(task_b, list):
                return False
            else:
                index_task_b = tasks_b.index(task_a)
                if any([isinstance(task_b, list) for task_b in tasks_b[i : index_task_b + 1]]):
                    return False
        return True

    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3, data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_1 = Scenario("scenario_1", {task_1, task_2, task_3, task_4}, {}, [], ScenarioId("s1"))

    assert scenario_1.get_inputs() == {data_node_1, data_node_2}
    assert scenario_1._get_set_of_tasks() == {task_1, task_2, task_3, task_4}
    _assert_equal(scenario_1._get_sorted_tasks(), [[task_1], [task_2, task_4], [task_3]])

    # s1 ---              t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_2 = Scenario("scenario_2", {task_1, task_2, task_3, task_4}, {}, [], ScenarioId("s2"))

    assert scenario_2.get_inputs() == {data_node_1, data_node_2}
    assert scenario_2._get_set_of_tasks() == {task_1, task_2, task_3, task_4}
    _assert_equal(scenario_2._get_sorted_tasks(), [[task_1, task_2], [task_3, task_4]])

    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_3 = Scenario("quest", [task_4, task_2, task_1, task_3], {}, [], scenario_id=ScenarioId("s3"))

    assert scenario_3.get_inputs() == {data_node_1, data_node_2, data_node_6}
    assert scenario_3._get_set_of_tasks() == {task_1, task_2, task_3, task_4}
    assert _assert_equal(scenario_3._get_sorted_tasks(), [[task_2, task_1], [task_4, task_3]])

    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7 ---> t6
    #                                              |
    # s8 -------> t5 -------> s9 ------------------

    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = InMemoryDataNode("d8", Scope.SCENARIO, "s8")
    data_node_9 = InMemoryDataNode("d9", Scope.SCENARIO, "s9")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [data_node_8], [data_node_9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [data_node_7, data_node_9], id=TaskId("t6"))
    scenario_4 = Scenario("scenario_3", [task_1, task_2, task_3, task_4, task_5, task_6], {}, [], ScenarioId("s4"))

    assert scenario_4.get_inputs() == {data_node_1, data_node_2, data_node_6, data_node_8}
    assert scenario_4._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5, task_6}
    _assert_equal(scenario_4._get_sorted_tasks(), [[task_1, task_2, task_5], [task_3, task_4], [task_6]])

    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5                      |
    # s8 ---> t5                 s6 --|

    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = InMemoryDataNode("hugh", Scope.SCENARIO, "s8")
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4, data_node_6], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_8], None, TaskId("t5"))
    scenario_5 = Scenario("scenario_4", [task_1, task_2, task_3, task_4, task_5], {}, [], ScenarioId("s5"))

    assert scenario_5.get_inputs() == {data_node_1, data_node_2, data_node_8, data_node_6}
    assert scenario_5._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_5._get_sorted_tasks(), [[task_1, task_2, task_5], [task_3, task_4]])

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s4 ---> t4 ---> s5
    #  p2  t2 ---> s4 ---> t3
    #  p3  s6 ---> t5

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, output=[data_node_4], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_6], None, TaskId("t5"))
    scenario_6 = Scenario("quest", [task_1, task_2, task_3, task_4, task_5], {}, [], ScenarioId("s6"))

    assert scenario_6.get_inputs() == {data_node_1, data_node_2, data_node_6}
    assert scenario_6._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_6._get_sorted_tasks(), [[task_5, task_2, task_1], [task_4, task_3]])

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s4 ---> t4 ---> s5
    #  p2  t2 ---> s4 ---> t3
    #  p3  s6 ---> t5 ---> s4 ---> t4 ---> s5

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, output=[data_node_4], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_6], [data_node_4], None, TaskId("t5"))
    scenario_7 = Scenario("quest", [task_4, task_1, task_2, task_3, task_5], {}, [], scenario_id=ScenarioId("s7"))

    assert scenario_7.get_inputs() == {data_node_1, data_node_2, data_node_6}
    assert scenario_7._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_7._get_sorted_tasks(), [[task_5, task_2, task_1], [task_4, task_3]])

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s3 ---> t4 ---> s4
    #  p2  t2 ---> s3 ---> t3
    #  p3  s5 ---> t5 ---> s3 ---> t4 ---> s4
    #  p4  s3 ---> t4 ---> s4

    data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = DataNode("qux", Scope.SCENARIO, "s3")
    data_node_4 = DataNode("quux", Scope.SCENARIO, "s4")
    data_node_5 = DataNode("quuz", Scope.SCENARIO, "s5")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_3],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, output=[data_node_3], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_3], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_3], [data_node_4], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_5], [data_node_3], TaskId("t5"))
    scenario_8 = Scenario("quest", [task_1, task_2, task_3, task_4, task_5], {}, [], scenario_id=ScenarioId("s8"))

    assert scenario_8.get_inputs() == {data_node_1, data_node_2, data_node_5}
    assert scenario_8._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_8._get_sorted_tasks(), [[task_5, task_2, task_1], [task_3, task_4]])


def test_add_and_remove_sequences():
    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("qux", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("quux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quuz", Scope.SCENARIO, "s5")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_3],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_3], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_3], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_3], [data_node_4], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_5], [data_node_3], TaskId("t5"))
    scenario_1 = Scenario("quest", [task_1, task_2, task_3, task_4, task_5], {}, [], scenario_id=ScenarioId("s1"))

    sequence_1 = Sequence({"name": "sequence_1"}, [task_1], SequenceId(f"SEQUENCE_sequence_1_{scenario_1.id}"))
    sequence_2 = Sequence({"name": "sequence_2"}, [task_1, task_2], SequenceId(f"SEQUENCE_sequence_2_{scenario_1.id}"))
    sequence_3 = Sequence(
        {"name": "sequence_3"}, [task_1, task_5, task_3], SequenceId(f"SEQUENCE_sequence_3_{scenario_1.id}")
    )

    task_manager = _TaskManagerFactory._build_manager()
    data_manager = _DataManagerFactory._build_manager()
    scenario_manager = _ScenarioManagerFactory._build_manager()
    for dn in [data_node_1, data_node_2, data_node_3, data_node_4, data_node_5]:
        data_manager._set(dn)
    for t in [task_1, task_2, task_3, task_4, task_5]:
        task_manager._set(t)
    scenario_manager._set(scenario_1)

    assert scenario_1.get_inputs() == {data_node_1, data_node_2, data_node_5}
    assert scenario_1._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    assert len(scenario_1.sequences) == 0

    scenario_1.sequences = {"sequence_1": {"tasks": [task_1]}}
    assert scenario_1.sequences == {"sequence_1": sequence_1}

    scenario_1.add_sequences({"sequence_2": {"tasks": [task_1, task_2]}})
    assert scenario_1.sequences == {"sequence_1": sequence_1, "sequence_2": sequence_2}

    scenario_1.remove_sequences(["sequence_1"])
    assert scenario_1.sequences == {"sequence_2": sequence_2}

    scenario_1.add_sequences({"sequence_1": {"tasks": [task_1]}, "sequence_3": {"tasks": [task_1, task_5, task_3]}})
    assert scenario_1.sequences == {
        "sequence_2": sequence_2,
        "sequence_1": sequence_1,
        "sequence_3": sequence_3,
    }

    scenario_1.remove_sequences(["sequence_2", "sequence_3"])
    assert scenario_1.sequences == {"sequence_1": sequence_1}


def test_check_consistency():
    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("bar", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    data_node_8 = InMemoryDataNode("d8", Scope.SCENARIO, "s8")
    data_node_9 = InMemoryDataNode("d9", Scope.SCENARIO, "s9")

    scenario_0 = Scenario("scenario_0", [], {})
    assert scenario_0._is_consistent()

    task_1 = Task("foo", {}, print, [data_node_1], [data_node_2], TaskId("t1"))
    scenario_1 = Scenario("scenario_1", [task_1], {})
    assert scenario_1._is_consistent()

    # s1 ---             ---> s3 ---> t2 ---> s5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3, data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_2 = Scenario("scenario_2", {task_1, task_2, task_3, task_4}, {}, [], ScenarioId("s1"))
    assert scenario_2._is_consistent()

    # s1 ---              t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> s6
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_3 = Scenario("scenario_3", {task_1, task_2, task_3, task_4}, {}, [], ScenarioId("s2"))
    assert scenario_3._is_consistent()

    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    scenario_4 = Scenario("scenario_4", [task_4, task_2, task_1, task_3], {}, [], scenario_id=ScenarioId("s3"))
    assert scenario_4._is_consistent()

    # s1 ---      s6 ---> t2 ---> s5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7 ---> t6
    #                                              |
    # s8 -------> t5 -------> s9 ------------------
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [data_node_6], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [data_node_8], [data_node_9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [data_node_7, data_node_9], id=TaskId("t6"))
    scenario_5 = Scenario("scenario_5", [task_1, task_2, task_3, task_4, task_5, task_6], {}, [], ScenarioId("s4"))
    assert scenario_5._is_consistent()

    # s1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # s2 ---             ---> s4 ---> t4 ---> s7
    # t2 ---> s5                      |
    # s8 ---> t5                 s6 --|
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4, data_node_6], [data_node_7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_8], None, TaskId("t5"))
    scenario_6 = Scenario("scenario_6", [task_1, task_2, task_3, task_4, task_5], {}, [], ScenarioId("s5"))
    assert scenario_6._is_consistent()

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s4 ---> t4 ---> s5
    #  p2  t2 ---> s4 ---> t3
    #  p3  s6 ---> t5
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_4], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_6], None, TaskId("t5"))
    scenario_7 = Scenario("scenario_7", [task_1, task_2, task_3, task_4, task_5], {}, [], ScenarioId("s6"))
    assert scenario_7._is_consistent()

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s4 ---> t4 ---> s5
    #  p2  t2 ---> s4 ---> t3
    #  p3  s6 ---> t5 ---> s4 ---> t4 ---> s5
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_4], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_6], [data_node_4], None, TaskId("t5"))
    scenario_8 = Scenario("scenario_8", [task_4, task_1, task_2, task_3, task_5], {}, [], scenario_id=ScenarioId("s7"))
    assert scenario_8._is_consistent()

    #  p1  s1 ---
    #            |
    #            |---> t1 ---|      -----> t3
    #            |           |      |
    #      s2 ---             ---> s3 ---> t4 ---> s4
    #  p2  t2 ---> s3 ---> t3
    #  p3  s5 ---> t5 ---> s3 ---> t4 ---> s4
    #  p4  s3 ---> t4 ---> s4
    task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[data_node_3], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_3], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_3], [data_node_4], TaskId("t4"))
    task_5 = Task("bob", {}, print, [data_node_5], [data_node_3], TaskId("t5"))
    scenario_9 = Scenario("scenario_9", [task_1, task_2, task_3, task_4, task_5], {}, [], scenario_id=ScenarioId("s8"))
    assert scenario_9._is_consistent()
