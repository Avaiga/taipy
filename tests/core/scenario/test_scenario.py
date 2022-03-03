import taipy.core.taipy as tp
from taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.scenario.scenario import Scenario
from taipy.core.task.task import Task


def test_create_scenario(cycle, current_datetime):
    scenario_entity_1 = Scenario("fOo ", [], {"key": "value"}, is_master=True, cycle=cycle)
    assert scenario_entity_1.id is not None
    assert scenario_entity_1.config_id == "foo"
    assert scenario_entity_1.pipelines == {}
    assert scenario_entity_1.properties == {"key": "value"}
    assert scenario_entity_1.key == "value"
    assert scenario_entity_1.creation_date is not None
    assert scenario_entity_1.is_master
    assert scenario_entity_1.cycle == cycle
    assert scenario_entity_1.tags == set()

    scenario_entity_2 = Scenario("   bar/ξéà   ", [], {}, ScenarioId("baz"), creation_date=current_datetime)
    assert scenario_entity_2.id == "baz"
    assert scenario_entity_2.config_id == "bar-xea"
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

    pipeline_entity_1 = Pipeline("abcξyₓéà", {}, [])
    scenario_entity_4 = Scenario("abcx", [pipeline_entity_1], {})
    assert scenario_entity_4.id is not None
    assert scenario_entity_4.config_id == "abcx"
    assert len(scenario_entity_4.pipelines) == 1
    assert scenario_entity_4.abcxyxea == pipeline_entity_1
    assert scenario_entity_4.properties == {}
    assert scenario_entity_4.tags == set()


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
    scenario.add_tag("tag")
    assert len(scenario.tags) == 1

    scenario.remove_tag("tag")
    assert len(scenario.tags) == 0
