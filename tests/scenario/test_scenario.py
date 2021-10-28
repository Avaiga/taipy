from taipy.common.alias import PipelineId, ScenarioId, TaskId
from taipy.data import Scope
from taipy.data.in_memory import InMemoryDataSource
from taipy.pipeline import Pipeline
from taipy.scenario import Scenario
from taipy.task import Task


def test_create_scenario_entity():
    scenario_entity_1 = Scenario("fOo ", [], {"key": "value"})
    assert scenario_entity_1.id is not None
    assert scenario_entity_1.config_name == "foo"
    assert scenario_entity_1.pipelines == {}
    assert scenario_entity_1.properties == {"key": "value"}
    assert scenario_entity_1.key == "value"

    scenario_entity_2 = Scenario("   bar   ", [], {}, ScenarioId("baz"))
    assert scenario_entity_2.id == "baz"
    assert scenario_entity_2.config_name == "bar"
    assert scenario_entity_2.pipelines == {}
    assert scenario_entity_2.properties == {}

    pipeline_entity = Pipeline("qux", {}, [])
    scenario_entity_3 = Scenario("quux", [pipeline_entity], {})
    assert scenario_entity_3.id is not None
    assert scenario_entity_3.config_name == "quux"
    assert len(scenario_entity_3.pipelines) == 1
    assert scenario_entity_3.qux == pipeline_entity
    assert scenario_entity_3.properties == {}


def test_add_property_to_scenario():
    scenario_1 = Scenario("foo", [], {"key": "value"})
    assert scenario_1.properties == {"key": "value"}
    assert scenario_1.key == "value"

    scenario_1.properties["new_key"] = "new_value"

    assert scenario_1.properties == {"key": "value", "new_key": "new_value"}
    assert scenario_1.key == "value"
    assert scenario_1.new_key == "new_value"


def test_to_model():
    input_ds = InMemoryDataSource("input_name", Scope.PIPELINE, "input_id", {"data": "this is some data"})
    output = InMemoryDataSource("output_name", Scope.PIPELINE, "output_id", {"data": ""})
    task = Task("task", [input_ds], print, [output], TaskId("task_id"))
    pipeline_entity = Pipeline("pipeline_name", {"big_pty": "big value"}, [task], PipelineId("pipeline_id"))
    scenario_entity = Scenario("scenario_name", [pipeline_entity], {"key": "value"}, ScenarioId("scenario_id"))

    model = scenario_entity.to_model()
    assert model.id == "scenario_id"
    assert model.name == "scenario_name"
    assert len(model.pipelines) == 1
    assert model.pipelines[0] == "pipeline_id"
    assert len(model.properties) == 1
    assert model.properties["key"] == "value"
