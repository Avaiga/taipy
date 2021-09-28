from taipy.data import Scope
from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.pipeline import PipelineEntity, PipelineId
from taipy.scenario import ScenarioEntity, ScenarioId
from taipy.task import TaskEntity, TaskId


def test_create_scenario_entity():
    scenario_entity_1 = ScenarioEntity("fOo ", [], {"key": "value"})
    assert scenario_entity_1.id is not None
    assert scenario_entity_1.name == "foo"
    assert scenario_entity_1.pipeline_entities == {}
    assert scenario_entity_1.properties == {"key": "value"}
    assert scenario_entity_1.key == "value"

    scenario_entity_2 = ScenarioEntity("   bar   ", [], {}, ScenarioId("baz"))
    assert scenario_entity_2.id == "baz"
    assert scenario_entity_2.name == "bar"
    assert scenario_entity_2.pipeline_entities == {}
    assert scenario_entity_2.properties == {}

    pipeline_entity = PipelineEntity("qux", {}, [])
    scenario_entity_3 = ScenarioEntity("quux", [pipeline_entity], {})
    assert scenario_entity_3.id is not None
    assert scenario_entity_3.name == "quux"
    assert len(scenario_entity_3.pipeline_entities) == 1
    assert scenario_entity_3.qux == pipeline_entity
    assert scenario_entity_3.properties == {}


def test_to_model():
    input_ds = EmbeddedDataSourceEntity(
        "input_name", Scope.PIPELINE, "input_id", {"data": "this is some data"}
    )
    output = EmbeddedDataSourceEntity(
        "output_name", Scope.PIPELINE, "output_id", {"data": ""}
    )
    task = TaskEntity("task", [input_ds], print, [output], TaskId("task_id"))
    pipeline_entity = PipelineEntity(
        "pipeline_name", {"big_pty": "big value"}, [task], PipelineId("pipeline_id")
    )
    scenario_entity = ScenarioEntity(
        "scenario_name", [pipeline_entity], {"key": "value"}, ScenarioId("scenario_id")
    )

    model = scenario_entity.to_model()
    assert model.id == "scenario_id"
    assert model.name == "scenario_name"
    assert len(model.pipelines) == 1
    assert model.pipelines[0] == "pipeline_id"
    assert len(model.properties) == 1
    assert model.properties["key"] == "value"
