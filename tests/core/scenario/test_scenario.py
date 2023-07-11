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

from src.taipy.core import DataNode, taipy
from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.cycle.cycle import Cycle, CycleId
from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.pipeline.pipeline_id import PipelineId
from src.taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.scenario.scenario_id import ScenarioId
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task
from src.taipy.core.task.task_id import TaskId
from taipy.config import Config, Frequency
from taipy.config.common.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


def test_create_scenario(cycle, current_datetime):
    scenario_1 = Scenario("foo", set(), {"key": "value"}, is_primary=True, cycle=cycle)
    assert scenario_1.id is not None
    assert scenario_1.config_id == "foo"
    assert scenario_1.tasks == {}
    assert scenario_1.additional_data_nodes == {}
    assert scenario_1.data_nodes == {}
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
    assert scenario_2.properties == {}
    assert scenario_2.creation_date == current_datetime
    assert not scenario_2.is_primary
    assert scenario_2.cycle is None
    assert scenario_2.tags == set()
    assert scenario_2.get_simple_label() == scenario_2.config_id
    assert scenario_2.get_label() == scenario_2.config_id

    dn_1 = DataNode("xyz")
    dn_2 = DataNode("abc")
    task = Task("qux", {}, print, [dn_1])

    scenario_3 = Scenario("quux", set([task]), {}, set([dn_2]))
    assert scenario_3.id is not None
    assert scenario_3.config_id == "quux"
    assert len(scenario_3.tasks) == 1
    assert len(scenario_3.additional_data_nodes) == 1
    assert len(scenario_3.data_nodes) == 2
    assert scenario_3.qux == task
    assert scenario_3.xyz == dn_1
    assert scenario_3.abc == dn_2
    assert scenario_3.properties == {}
    assert scenario_3.tags == set()

    with pytest.raises(InvalidConfigurationId):
        Scenario("foo bar", [], {})

    input_1 = InMemoryDataNode("input_1", Scope.SCENARIO)
    input_2 = InMemoryDataNode("input_2", Scope.SCENARIO)
    output_1 = InMemoryDataNode("output_1", Scope.SCENARIO)
    output_2 = InMemoryDataNode("output_2", Scope.SCENARIO)
    additional_dn_1 = InMemoryDataNode("additional_1", Scope.SCENARIO)
    additional_dn_2 = InMemoryDataNode("additional_2", Scope.SCENARIO)
    task_1 = Task("task_1", {}, print, [input_1], [output_1], TaskId("task_id_1"))
    task_2 = Task("task_2", {}, print, [input_2], [output_2], TaskId("task_id_2"))

    data_manager = _DataManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()

    data_manager._set(input_1)
    data_manager._set(output_1)
    data_manager._set(input_2)
    data_manager._set(output_2)
    data_manager._set(additional_dn_1)
    data_manager._set(additional_dn_2)
    task_manager._set(task_1)
    task_manager._set(task_2)

    scenario_4 = Scenario("scenario_4", set([task_1]), {})
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

    scenario_5 = Scenario("scenario_5", set([task_1, task_2]), {})
    assert scenario_5.id is not None
    assert scenario_5.config_id == "scenario_5"
    assert len(scenario_5.tasks) == 2
    assert len(scenario_5.additional_data_nodes) == 0
    assert len(scenario_5.data_nodes) == 4
    assert scenario_5.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_5.additional_data_nodes == {}
    assert scenario_5.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        input_2.config_id: input_2,
        output_2.config_id: output_2,
    }

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
    assert len(scenario_9.data_nodes) == 6
    assert scenario_9.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_9.additional_data_nodes == {
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }
    assert scenario_9.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        input_2.config_id: input_2,
        output_2.config_id: output_2,
        additional_dn_1.config_id: additional_dn_1,
        additional_dn_2.config_id: additional_dn_2,
    }


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

    with scenario_1 as scenario:
        assert scenario.config_id == "foo"
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

        new_datetime_2 = new_datetime + timedelta(5)
        scenario.config_id = "foo"
        scenario.tasks = set()
        scenario.additional_data_nodes = set()
        scenario.creation_date = new_datetime_2
        scenario.cycle = None
        scenario.is_primary = False
        scenario.subscribers = [print]
        scenario.tags = None
        scenario.name = "qux"
        scenario.properties["qux"] = 9

        assert scenario.config_id == "foo"
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

    assert scenario_1.config_id == "foo"
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


def test_get_inputs():
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

    assert scenario_1._get_inputs() == {data_node_1, data_node_2}
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

    assert scenario_2._get_inputs() == {data_node_1, data_node_2}
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

    assert scenario_3._get_inputs() == {data_node_1, data_node_2, data_node_6}
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

    assert scenario_4._get_inputs() == {data_node_1, data_node_2, data_node_6, data_node_8}
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

    assert scenario_5._get_inputs() == {data_node_1, data_node_2, data_node_8, data_node_6}
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

    assert scenario_6._get_inputs() == {data_node_1, data_node_2, data_node_6}
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

    assert scenario_7._get_inputs() == {data_node_1, data_node_2, data_node_6}
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

    assert scenario_8._get_inputs() == {data_node_1, data_node_2, data_node_5}
    assert scenario_8._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_8._get_sorted_tasks(), [[task_5, task_2, task_1], [task_3, task_4]])
