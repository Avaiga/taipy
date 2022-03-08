from unittest import mock

import pytest

import taipy.core.taipy as tp
from taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import InvalidConfigurationId
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scenario.scenario import Scenario
from taipy.core.task.task import Task


def test_create_scenario(cycle, current_datetime):
    scenario_entity_1 = Scenario("foo", [], {"key": "value"}, is_master=True, cycle=cycle)
    assert scenario_entity_1.id is not None
    assert scenario_entity_1.config_id == "foo"
    assert scenario_entity_1.pipelines == {}
    assert scenario_entity_1.properties == {"key": "value"}
    assert scenario_entity_1.key == "value"
    assert scenario_entity_1.creation_date is not None
    assert scenario_entity_1.is_master
    assert scenario_entity_1.cycle == cycle
    assert scenario_entity_1.tags == set()

    scenario_entity_2 = Scenario("bar", [], {}, ScenarioId("baz"), creation_date=current_datetime)
    assert scenario_entity_2.id == "baz"
    assert scenario_entity_2.config_id == "bar"
    assert scenario_entity_2.pipelines == {}
    assert scenario_entity_2.properties == {}
    assert scenario_entity_2.creation_date == current_datetime
    assert not scenario_entity_2.is_master
    assert scenario_entity_2.cycle is None
    assert scenario_entity_2.tags == set()

    pipeline_entity = Pipeline("qux", {}, [])
    scenario_entity_3 = Scenario("quux", [pipeline_entity], {})
    assert scenario_entity_3.id is not None
    assert scenario_entity_3.config_id == "quux"
    assert len(scenario_entity_3.pipelines) == 1
    assert scenario_entity_3.qux == pipeline_entity
    assert scenario_entity_3.properties == {}
    assert scenario_entity_3.tags == set()

    pipeline_entity_1 = Pipeline("abcx", {}, [])
    scenario_entity_4 = Scenario("abcxy", [pipeline_entity_1], {})
    assert scenario_entity_4.id is not None
    assert scenario_entity_4.config_id == "abcxy"
    assert len(scenario_entity_4.pipelines) == 1
    assert scenario_entity_4.abcx == pipeline_entity_1
    assert scenario_entity_4.properties == {}
    assert scenario_entity_4.tags == set()

    with pytest.raises(InvalidConfigurationId):
        Scenario("foo bar", [], {})


def test_add_property_to_scenario():
    scenario = Scenario("foo", [], {"key": "value"})
    assert scenario.properties == {"key": "value"}
    assert scenario.key == "value"

    scenario.properties["new_key"] = "new_value"

    assert scenario.properties == {"key": "value", "new_key": "new_value"}
    assert scenario.key == "value"
    assert scenario.new_key == "new_value"

    # test scenario properties saved and reloaded
    tp.set(scenario)
    scenario.properties["qux"] = 5
    same_scenario = tp.get(scenario.id)
    assert scenario.properties["qux"] == 5
    assert same_scenario.properties["qux"] == 5


def test_add_cycle_to_scenario(cycle):
    scenario = Scenario("foo", [], {})
    assert scenario.cycle is None

    scenario.cycle = cycle

    assert scenario.cycle == cycle


def test_add_and_remove_subscriber():
    def mock_function():
        pass

    scenario = Scenario("foo", [], {})

    scenario.add_subscriber(mock_function)
    assert len(scenario.subscribers) == 1

    scenario.remove_subscriber(mock_function)
    assert len(scenario.subscribers) == 0


def test_add_and_remove_tag():
    scenario = Scenario("foo", [], {})

    assert len(scenario.tags) == 0
    scenario._add_tag("tag")
    assert len(scenario.tags) == 1

    scenario._remove_tag("tag")
    assert len(scenario.tags) == 0


def test_submit_scenario():
    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mock_submit:
        scenario = Scenario("foo", [], {})
        scenario.submit(False)
        mock_submit.assert_called_once_with(scenario, False)


def test_subscribe_scenario():
    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._subscribe") as mock_subscribe:
        scenario = Scenario("foo", [], {})
        scenario.subscribe(None)
        mock_subscribe.assert_called_once_with(None, scenario)


def test_unsubscribe_scenario():
    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._unsubscribe") as mock_unsubscribe:
        scenario = Scenario("foo", [], {})
        scenario.unsubscribe(None)
        mock_unsubscribe.assert_called_once_with(None, scenario)


def test_add_tag_scenario():
    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._tag") as mock_add_tag:
        scenario = Scenario("foo", [], {})
        scenario.add_tag("tag")
        mock_add_tag.assert_called_once_with(scenario, "tag")


def test_remove_tag_scenario():
    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._untag") as mock_remove_tag:
        scenario = Scenario("foo", [], {})
        scenario.remove_tag("tag")
        mock_remove_tag.assert_called_once_with(scenario, "tag")
