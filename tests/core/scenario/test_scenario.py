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

from datetime import timedelta
from unittest import mock

import pytest

from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.common.alias import ScenarioId, TaskId
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task.task import Task
from taipy.config.common.scope import Scope
from taipy.config.exceptions.exceptions import InvalidConfigurationId


def test_create_scenario(cycle, current_datetime):
    scenario_1 = Scenario("foo", [], {"key": "value"}, is_primary=True, cycle=cycle)
    assert scenario_1.id is not None
    assert scenario_1.config_id == "foo"
    assert scenario_1.pipelines == {}
    assert scenario_1.properties == {"key": "value"}
    assert scenario_1.key == "value"
    assert scenario_1.creation_date is not None
    assert scenario_1.is_primary
    assert scenario_1.cycle == cycle
    assert scenario_1.tags == set()

    scenario_2 = Scenario("bar", [], {}, ScenarioId("baz"), creation_date=current_datetime)
    assert scenario_2.id == "baz"
    assert scenario_2.config_id == "bar"
    assert scenario_2.pipelines == {}
    assert scenario_2.properties == {}
    assert scenario_2.creation_date == current_datetime
    assert not scenario_2.is_primary
    assert scenario_2.cycle is None
    assert scenario_2.tags == set()

    pipeline = Pipeline("qux", {}, [])
    scenario_3 = Scenario("quux", [pipeline], {})
    assert scenario_3.id is not None
    assert scenario_3.config_id == "quux"
    assert len(scenario_3.pipelines) == 1
    assert scenario_3.qux == pipeline
    assert scenario_3.properties == {}
    assert scenario_3.tags == set()

    pipeline_1 = Pipeline("abcx", {}, [])
    scenario_4 = Scenario("abcxy", [pipeline_1], {})
    assert scenario_4.id is not None
    assert scenario_4.config_id == "abcxy"
    assert len(scenario_4.pipelines) == 1
    assert scenario_4.abcx == pipeline_1
    assert scenario_4.properties == {}
    assert scenario_4.tags == set()

    with pytest.raises(InvalidConfigurationId):
        Scenario("foo bar", [], {})

    input_1 = InMemoryDataNode("input_1", Scope.SCENARIO)
    input_2 = InMemoryDataNode("input_2", Scope.SCENARIO)
    output_1 = InMemoryDataNode("output_1", Scope.SCENARIO)
    output_2 = InMemoryDataNode("output_2", Scope.SCENARIO)
    task_1 = Task("task_1", {}, print, [input_1], [output_1], TaskId("task_id_1"))
    task_2 = Task("task_2", {}, print, [input_2], [output_2], TaskId("task_id_2"))

    pipeline_2 = Pipeline("pipeline_2", {"description": "description"}, [task_1], owner_id="owner_id")
    pipeline_3 = Pipeline("pipeline_3", {"description": "description"}, [task_2], owner_id="owner_id")
    pipeline_4 = Pipeline("pipeline_4", {"description": "description"}, [task_1, task_2], owner_id="owner_id")

    scenario_5 = Scenario("scenario_5", [pipeline_2], {})
    assert scenario_5.id is not None
    assert scenario_5.config_id == "scenario_5"
    assert len(scenario_5.pipelines) == 1
    assert scenario_5.pipelines == {pipeline_2.config_id: pipeline_2}
    assert scenario_5.data_nodes == {input_1.config_id: input_1, output_1.config_id: output_1}

    scenario_6 = Scenario("scenario_6", [pipeline_2, pipeline_3], {})
    assert scenario_6.id is not None
    assert scenario_6.config_id == "scenario_6"
    assert len(scenario_6.pipelines) == 2
    assert scenario_6.pipelines == {pipeline_2.config_id: pipeline_2, pipeline_3.config_id: pipeline_3}
    assert scenario_6.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        input_2.config_id: input_2,
        output_2.config_id: output_2,
    }

    scenario_7 = Scenario("scenario_7", [pipeline_4], {})
    assert scenario_7.id is not None
    assert scenario_7.config_id == "scenario_7"
    assert len(scenario_7.pipelines) == 1
    assert scenario_7.pipelines == {pipeline_4.config_id: pipeline_4}
    assert scenario_7.data_nodes == {
        input_1.config_id: input_1,
        output_1.config_id: output_1,
        input_2.config_id: input_2,
        output_2.config_id: output_2,
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


def test_auto_set_and_reload(cycle, current_datetime, pipeline):
    scenario_1 = Scenario(
        "foo",
        [],
        {"name": "bar"},
        creation_date=current_datetime,
        is_primary=False,
        cycle=None,
    )
    _ScenarioManager._set(scenario_1)
    _PipelineManager._set(pipeline)
    _CycleManager._set(cycle)

    scenario_2 = _ScenarioManager._get(scenario_1)
    assert scenario_1.config_id == "foo"
    assert scenario_2.config_id == "foo"

    assert scenario_1.name == "bar"
    scenario_1.name = "baz"
    assert scenario_1.name == "baz"
    assert scenario_2.name == "baz"

    assert len(scenario_1.pipelines) == 0
    scenario_1.pipelines = [pipeline]
    assert len(scenario_1.pipelines) == 1
    assert scenario_1.pipelines[pipeline.config_id] == pipeline
    assert len(scenario_2.pipelines) == 1
    assert scenario_2.pipelines[pipeline.config_id] == pipeline

    new_datetime = current_datetime + timedelta(1)

    assert scenario_1.creation_date == current_datetime
    scenario_1.creation_date = new_datetime
    assert scenario_1.creation_date == new_datetime
    assert scenario_2.creation_date == new_datetime

    assert scenario_1.cycle is None
    scenario_1.cycle = cycle
    assert scenario_1.cycle == cycle
    assert scenario_2.cycle == cycle

    assert not scenario_1.is_primary
    scenario_1.is_primary = True
    assert scenario_1.is_primary
    assert scenario_2.is_primary

    assert len(scenario_1.subscribers) == 0
    scenario_1.subscribers.append(_Subscriber(print, []))
    assert len(scenario_1.subscribers) == 1
    assert len(scenario_2.subscribers) == 1

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

    assert scenario_1.properties == {"name": "baz"}
    scenario_1.properties["qux"] = 5
    assert scenario_1.properties["qux"] == 5
    assert scenario_2.properties["qux"] == 5

    with scenario_1 as scenario:
        assert scenario.config_id == "foo"
        assert len(scenario.pipelines) == 1
        assert scenario.pipelines[pipeline.config_id] == pipeline
        assert scenario.creation_date == new_datetime
        assert scenario.cycle == cycle
        assert scenario.is_primary
        assert len(scenario.subscribers) == 0
        assert len(scenario.tags) == 1
        assert scenario._is_in_context
        assert scenario.name == "baz"

        new_datetime_2 = new_datetime + timedelta(1)
        scenario.config_id = "foo"
        scenario.pipelines = []
        scenario.creation_date = new_datetime_2
        scenario.cycle = None
        scenario.is_primary = False
        scenario.subscribers = [print]
        scenario.tags = None
        scenario.name = "qux"

        assert scenario.config_id == "foo"
        assert len(scenario.pipelines) == 1
        assert scenario.pipelines[pipeline.config_id] == pipeline
        assert scenario.creation_date == new_datetime
        assert scenario.cycle == cycle
        assert scenario.is_primary
        assert len(scenario.subscribers) == 0
        assert len(scenario.tags) == 1
        assert scenario._is_in_context
        assert scenario.name == "qux"  # should be baz here

    assert scenario_1.config_id == "foo"
    assert len(scenario_1.pipelines) == 0
    assert scenario_1.creation_date == new_datetime_2
    assert scenario_1.cycle is None
    assert not scenario_1.is_primary
    assert len(scenario_1.subscribers) == 1
    assert len(scenario_1.tags) == 0
    assert not scenario_1._is_in_context
    assert scenario_1.name == "qux"


def test_submit_scenario():
    with mock.patch("src.taipy.core.submit") as mock_submit:
        scenario = Scenario("foo", [], {})
        scenario.submit(False)
        mock_submit.assert_called_once_with(scenario, False, False, None)


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
