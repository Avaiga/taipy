import pytest

from taipy.data import DataSource, DataSourceEntity, Scope
from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.exceptions import NonExistingTaskEntity
from taipy.exceptions.pipeline import NonExistingPipelineEntity
from taipy.exceptions.scenario import (
    NonExistingScenario,
    NonExistingScenarioEntity,
)
from taipy.pipeline import Pipeline, PipelineEntity, PipelineId
from taipy.scenario import Scenario, ScenarioEntity, ScenarioId, ScenarioManager
from taipy.task import Task, TaskEntity, TaskId, TaskScheduler


def test_register_and_get_scenario():
    name_1 = "scenario_name_1"
    scenario_1 = Scenario(name_1, [])

    input_2 = DataSource("foo", "embedded", data="bar")
    output_2 = DataSource("foo", "embedded", data="bar")
    task_2 = Task("task", [input_2], print, [output_2])
    pipeline_name_2 = "pipeline_name_2"
    pipeline_2 = Pipeline(pipeline_name_2, [task_2])
    name_2 = "scenario_name_2"
    scenario_2 = Scenario(name_2, [pipeline_2])

    scenario_3_with_same_name = Scenario(name_1, [], title="my description")

    # No existing Scenario
    scenario_manager = ScenarioManager()
    assert len(scenario_manager.get_scenarios()) == 0
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(name_1)
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(name_2)

    # Save one scenario. We expect to have only one scenario stored
    scenario_manager.register_scenario(scenario_1)
    assert len(scenario_manager.get_scenarios()) == 1
    assert scenario_manager.get_scenario(name_1) == scenario_1
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(name_2)

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    scenario_manager.register_scenario(scenario_2)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(name_1) == scenario_1
    assert scenario_manager.get_scenario(name_2) == scenario_2

    # We save the first scenario again. We expect nothing to change.
    scenario_manager.register_scenario(scenario_1)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(name_1) == scenario_1
    assert scenario_manager.get_scenario(name_2) == scenario_2
    assert scenario_manager.get_scenario(name_1).properties.get("title") is None

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    scenario_manager.register_scenario(scenario_3_with_same_name)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(name_1) == scenario_3_with_same_name
    assert scenario_manager.get_scenario(name_2) == scenario_2
    assert scenario_manager.get_scenario(name_1).properties.get(
        "title"
    ) == scenario_3_with_same_name.properties.get("title")


def test_save_and_get_scenario_entity():
    scenario_id_1 = ScenarioId("scenario_id_1")
    scenario_1 = ScenarioEntity("scenario_name_1", [], {}, scenario_id_1)

    input_2 = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, "bar")
    output_2 = EmbeddedDataSourceEntity.create("foo", Scope.PIPELINE, "bar")
    task_name = "task"
    task_2 = TaskEntity(task_name, [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_name_2 = "pipeline_name_2"
    pipeline_entity_2 = PipelineEntity(
        pipeline_name_2, {}, [task_2], PipelineId("pipeline_id_2")
    )
    scenario_id_2 = ScenarioId("scenario_id_2")
    scenario_2 = ScenarioEntity(
        "scenario_name_2", [pipeline_entity_2], {}, scenario_id_2
    )

    pipeline_entity_3 = PipelineEntity(
        "pipeline_name_3", {}, [], PipelineId("pipeline_id_3")
    )
    scenario_3_with_same_id = ScenarioEntity(
        "scenario_name_3", [pipeline_entity_3], {}, scenario_id_1
    )

    # No existing scenario entity
    scenario_manager = ScenarioManager()
    assert len(scenario_manager.get_scenario_entities()) == 0
    with pytest.raises(NonExistingScenarioEntity):
        scenario_manager.get_scenario_entity(scenario_id_1)
    with pytest.raises(NonExistingScenarioEntity):
        scenario_manager.get_scenario_entity(scenario_id_2)

    # Save one scenario. We expect to have only one scenario stored
    scenario_manager.save_scenario_entity(scenario_1)
    assert len(scenario_manager.get_scenario_entities()) == 1
    assert scenario_manager.get_scenario_entity(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario_entity(scenario_id_1).name == scenario_1.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_1).pipeline_entities) == 0
    )
    with pytest.raises(NonExistingScenarioEntity):
        scenario_manager.get_scenario_entity(scenario_id_2)

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    scenario_manager.pipeline_manager.task_manager.save_task_entity(task_2)
    scenario_manager.pipeline_manager.save_pipeline_entity(pipeline_entity_2)
    scenario_manager.save_scenario_entity(scenario_2)
    assert len(scenario_manager.get_scenario_entities()) == 2
    assert scenario_manager.get_scenario_entity(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario_entity(scenario_id_1).name == scenario_1.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_1).pipeline_entities) == 0
    )
    assert scenario_manager.get_scenario_entity(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario_entity(scenario_id_2).name == scenario_2.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_2).pipeline_entities) == 1
    )
    assert scenario_manager.task_manager.get_task_entity(task_2.id) == task_2

    # We save the first scenario again. We expect nothing to change
    scenario_manager.save_scenario_entity(scenario_1)
    assert len(scenario_manager.get_scenario_entities()) == 2
    assert scenario_manager.get_scenario_entity(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario_entity(scenario_id_1).name == scenario_1.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_1).pipeline_entities) == 0
    )
    assert scenario_manager.get_scenario_entity(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario_entity(scenario_id_2).name == scenario_2.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_2).pipeline_entities) == 1
    )
    assert scenario_manager.task_manager.get_task_entity(task_2.id) == task_2

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    scenario_manager.pipeline_manager.task_manager.save_task_entity(
        scenario_2.pipeline_entities[pipeline_name_2].task_entities[task_name]
    )
    scenario_manager.pipeline_manager.save_pipeline_entity(pipeline_entity_3)
    scenario_manager.save_scenario_entity(scenario_3_with_same_id)
    assert len(scenario_manager.get_scenario_entities()) == 2
    assert scenario_manager.get_scenario_entity(scenario_id_1).id == scenario_1.id
    assert (
        scenario_manager.get_scenario_entity(scenario_id_1).name
        == scenario_3_with_same_id.name
    )
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_1).pipeline_entities) == 1
    )
    assert scenario_manager.get_scenario_entity(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario_entity(scenario_id_2).name == scenario_2.name
    assert (
        len(scenario_manager.get_scenario_entity(scenario_id_2).pipeline_entities) == 1
    )
    assert scenario_manager.task_manager.get_task_entity(task_2.id) == task_2


def test_submit():
    data_source_1 = DataSourceEntity("foo", Scope.PIPELINE, "s1")
    data_source_2 = DataSourceEntity("bar", Scope.PIPELINE, "s2")
    data_source_3 = DataSourceEntity("baz", Scope.PIPELINE, "s3")
    data_source_4 = DataSourceEntity("qux", Scope.PIPELINE, "s4")
    data_source_5 = DataSourceEntity("quux", Scope.PIPELINE, "s5")
    data_source_6 = DataSourceEntity("quuz", Scope.PIPELINE, "s6")
    data_source_7 = DataSourceEntity("corge", Scope.PIPELINE, "s7")
    data_source_8 = DataSourceEntity("fum", Scope.PIPELINE, "s8")
    task_1 = TaskEntity(
        "grault",
        [data_source_1, data_source_2],
        print,
        [data_source_3, data_source_4],
        TaskId("t1"),
    )
    task_2 = TaskEntity("garply", [data_source_3], print, [data_source_5], TaskId("t2"))
    task_3 = TaskEntity(
        "waldo", [data_source_5, data_source_4], print, [data_source_6], TaskId("t3")
    )
    task_4 = TaskEntity("fred", [data_source_4], print, [data_source_7], TaskId("t4"))
    task_5 = TaskEntity("thud", [data_source_6], print, [data_source_8], TaskId("t5"))
    pipeline_entity_1 = PipelineEntity(
        "plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1")
    )
    pipeline_entity_2 = PipelineEntity("xyzzy", {}, [task_5], PipelineId("p2"))

    scenario_entity = ScenarioEntity(
        "scenario_name",
        [pipeline_entity_2, pipeline_entity_1],
        {},
        ScenarioId("sce_id"),
    )

    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager

    class MockTaskScheduler(TaskScheduler):
        submit_calls = []

        def submit(self, task: TaskEntity):
            self.submit_calls.append(task)
            return super().submit(task)

    pipeline_manager.task_scheduler = MockTaskScheduler()

    # scenario does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingScenarioEntity):
        scenario_manager.submit(scenario_entity.id)

    # scenario does exist, but pipeline does not exist.
    # We expect an exception to be raised
    scenario_manager.save_scenario_entity(scenario_entity)
    with pytest.raises(NonExistingPipelineEntity):
        scenario_manager.submit(scenario_entity.id)

    # scenario and pipeline do exist, but tasks does not exist.
    # We expect an exception to be raised
    pipeline_manager.save_pipeline_entity(pipeline_entity_1)
    pipeline_manager.save_pipeline_entity(pipeline_entity_2)
    with pytest.raises(NonExistingTaskEntity):
        scenario_manager.submit(scenario_entity.id)

    # scenario, pipeline, and tasks do exist.
    # We expect all the tasks to be submitted once,
    # and respecting specific constraints on the order
    task_manager.save_task_entity(task_1)
    task_manager.save_task_entity(task_2)
    task_manager.save_task_entity(task_3)
    task_manager.save_task_entity(task_4)
    task_manager.save_task_entity(task_5)
    scenario_manager.submit(scenario_entity.id)
    submit_calls = pipeline_manager.task_scheduler.submit_calls
    assert len(submit_calls) == 5
    assert set(submit_calls) == {task_1, task_2, task_4, task_3, task_5}
    assert submit_calls.index(task_2) < submit_calls.index(task_3)
    assert submit_calls.index(task_1) < submit_calls.index(task_3)
    assert submit_calls.index(task_1) < submit_calls.index(task_2)
    assert submit_calls.index(task_1) < submit_calls.index(task_4)


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_scenario_manager_only_creates_data_source_entity_once():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSource("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSource("bar", "embedded", Scope.SCENARIO, data=0)
    ds_6 = DataSource("baz", "embedded", Scope.PIPELINE, data=0)
    ds_4 = DataSource("qux", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = Task("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = Task("mult by 3", [ds_2], mult_by_3, ds_6)
    task_mult_by_4 = Task("mult by 4", [ds_1], mult_by_4, ds_4)
    pipeline_1 = Pipeline("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6
    pipeline_2 = Pipeline("by 4", [task_mult_by_4])
    # ds_1 ---> mult by 4 ---> ds_4
    scenario = Scenario("Awesome scenario", [pipeline_1, pipeline_2])
    scenario_manager.register_scenario(scenario)

    assert len(data_manager.get_data_source_entities()) == 0
    assert len(task_manager.task_entities) == 0
    assert len(pipeline_manager.get_pipeline_entities()) == 0
    assert len(scenario_manager.get_scenario_entities()) == 0

    scenario_entity = scenario_manager.create_scenario_entity(scenario)

    assert len(data_manager.get_data_source_entities()) == 4
    assert len(task_manager.task_entities) == 3
    assert len(pipeline_manager.get_pipeline_entities()) == 2
    assert len(scenario_manager.get_scenario_entities()) == 1
    assert scenario_entity.foo.get() == 1
    assert scenario_entity.bar.get() == 0
    assert scenario_entity.baz.get() == 0
    assert scenario_entity.qux.get() == 0
    assert (
        scenario_entity.by_6.get_sorted_task_entities()[0][0].name
        == task_mult_by_2.name
    )
    assert (
        scenario_entity.by_6.get_sorted_task_entities()[1][0].name
        == task_mult_by_3.name
    )
    assert (
        scenario_entity.by_4.get_sorted_task_entities()[0][0].name
        == task_mult_by_4.name
    )


def test_get_set_data():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSource("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSource("bar", "embedded", Scope.SCENARIO, data=0)
    ds_6 = DataSource("baz", "embedded", Scope.PIPELINE, data=0)
    ds_4 = DataSource("qux", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = Task("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = Task("mult by 3", [ds_2], mult_by_3, ds_6)
    task_mult_by_4 = Task("mult by 4", [ds_1], mult_by_4, ds_4)
    pipeline_1 = Pipeline("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6
    pipeline_2 = Pipeline("by 4", [task_mult_by_4])
    # ds_1 ---> mult by 4 ---> ds_4
    scenario = Scenario("Awesome scenario", [pipeline_1, pipeline_2])
    scenario_manager.register_scenario(scenario)

    scenario_entity = scenario_manager.create_scenario_entity(scenario)

    assert scenario_entity.foo.get() == 1
    assert scenario_entity.bar.get() == 0
    assert scenario_entity.baz.get() == 0
    assert scenario_entity.qux.get() == 0

    scenario_manager.submit(scenario_entity.id)
    assert scenario_entity.foo.get() == 1
    assert scenario_entity.bar.get() == 2
    assert scenario_entity.baz.get() == 6
    assert scenario_entity.qux.get() == 4

    scenario_entity.foo.write("new data value")
    assert scenario_entity.foo.get() == "new data value"
    assert scenario_entity.bar.get() == 2
    assert scenario_entity.baz.get() == 6
    assert scenario_entity.qux.get() == 4

    scenario_entity.baz.write(158)
    assert scenario_entity.foo.get() == "new data value"
    assert scenario_entity.bar.get() == 2
    assert scenario_entity.baz.get() == 158
    assert scenario_entity.qux.get() == 4
