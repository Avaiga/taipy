import pytest

from taipy.config import Config, DataSourceConfig, PipelineConfig, ScenarioConfig, TaskConfig
from taipy.data import DataSource, EmbeddedDataSource, Scope
from taipy.exceptions import NonExistingTask
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.exceptions.scenario import NonExistingScenario
from taipy.pipeline import Pipeline, PipelineId
from taipy.scenario import Scenario, ScenarioId, ScenarioManager
from taipy.task import Task, TaskId, TaskScheduler


def test_save_and_get_scenario_entity():
    scenario_id_1 = ScenarioId("scenario_id_1")
    scenario_1 = Scenario("scenario_name_1", [], {}, scenario_id_1)

    input_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "bar")
    output_2 = EmbeddedDataSource.create("foo", Scope.PIPELINE, "bar")
    task_name = "task"
    task_2 = Task(task_name, [input_2], print, [output_2], TaskId("task_id_2"))
    pipeline_name_2 = "pipeline_name_2"
    pipeline_entity_2 = Pipeline(pipeline_name_2, {}, [task_2], PipelineId("pipeline_id_2"))
    scenario_id_2 = ScenarioId("scenario_id_2")
    scenario_2 = Scenario("scenario_name_2", [pipeline_entity_2], {}, scenario_id_2)

    pipeline_entity_3 = Pipeline("pipeline_name_3", {}, [], PipelineId("pipeline_id_3"))
    scenario_3_with_same_id = Scenario("scenario_name_3", [pipeline_entity_3], {}, scenario_id_1)

    # No existing scenario entity
    scenario_manager = ScenarioManager()
    assert len(scenario_manager.get_scenarios()) == 0
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(scenario_id_1)
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(scenario_id_2)

    # Save one scenario. We expect to have only one scenario stored
    scenario_manager.save(scenario_1)
    assert len(scenario_manager.get_scenarios()) == 1
    assert scenario_manager.get_scenario(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario(scenario_id_1).config_name == scenario_1.config_name
    assert len(scenario_manager.get_scenario(scenario_id_1).pipelines) == 0
    with pytest.raises(NonExistingScenario):
        scenario_manager.get_scenario(scenario_id_2)

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    scenario_manager.pipeline_manager.task_manager.save(task_2)
    scenario_manager.pipeline_manager.save(pipeline_entity_2)
    scenario_manager.save(scenario_2)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario(scenario_id_1).config_name == scenario_1.config_name
    assert len(scenario_manager.get_scenario(scenario_id_1).pipelines) == 0
    assert scenario_manager.get_scenario(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario(scenario_id_2).config_name == scenario_2.config_name
    assert len(scenario_manager.get_scenario(scenario_id_2).pipelines) == 1
    assert scenario_manager.task_manager.get_task(task_2.id) == task_2

    # We save the first scenario again. We expect nothing to change
    scenario_manager.save(scenario_1)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario(scenario_id_1).config_name == scenario_1.config_name
    assert len(scenario_manager.get_scenario(scenario_id_1).pipelines) == 0
    assert scenario_manager.get_scenario(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario(scenario_id_2).config_name == scenario_2.config_name
    assert len(scenario_manager.get_scenario(scenario_id_2).pipelines) == 1
    assert scenario_manager.task_manager.get_task(task_2.id) == task_2

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    scenario_manager.pipeline_manager.task_manager.save(scenario_2.pipelines[pipeline_name_2].tasks[task_name])
    scenario_manager.pipeline_manager.save(pipeline_entity_3)
    scenario_manager.save(scenario_3_with_same_id)
    assert len(scenario_manager.get_scenarios()) == 2
    assert scenario_manager.get_scenario(scenario_id_1).id == scenario_1.id
    assert scenario_manager.get_scenario(scenario_id_1).config_name == scenario_3_with_same_id.config_name
    assert len(scenario_manager.get_scenario(scenario_id_1).pipelines) == 1
    assert scenario_manager.get_scenario(scenario_id_2).id == scenario_2.id
    assert scenario_manager.get_scenario(scenario_id_2).config_name == scenario_2.config_name
    assert len(scenario_manager.get_scenario(scenario_id_2).pipelines) == 1
    assert scenario_manager.task_manager.get_task(task_2.id) == task_2


def test_submit():
    data_source_1 = DataSource("foo", Scope.PIPELINE, "s1")
    data_source_2 = DataSource("bar", Scope.PIPELINE, "s2")
    data_source_3 = DataSource("baz", Scope.PIPELINE, "s3")
    data_source_4 = DataSource("qux", Scope.PIPELINE, "s4")
    data_source_5 = DataSource("quux", Scope.PIPELINE, "s5")
    data_source_6 = DataSource("quuz", Scope.PIPELINE, "s6")
    data_source_7 = DataSource("corge", Scope.PIPELINE, "s7")
    data_source_8 = DataSource("fum", Scope.PIPELINE, "s8")
    task_1 = Task(
        "grault",
        [data_source_1, data_source_2],
        print,
        [data_source_3, data_source_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", [data_source_3], print, [data_source_5], TaskId("t2"))
    task_3 = Task("waldo", [data_source_5, data_source_4], print, [data_source_6], TaskId("t3"))
    task_4 = Task("fred", [data_source_4], print, [data_source_7], TaskId("t4"))
    task_5 = Task("thud", [data_source_6], print, [data_source_8], TaskId("t5"))
    pipeline_entity_1 = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    pipeline_entity_2 = Pipeline("xyzzy", {}, [task_5], PipelineId("p2"))

    scenario_entity = Scenario(
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

        def submit(self, task: Task, callbacks=None):
            self.submit_calls.append(task)
            return super().submit(task, callbacks)

    pipeline_manager.task_scheduler = MockTaskScheduler()

    # scenario does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingScenario):
        scenario_manager.submit(scenario_entity.id)

    # scenario does exist, but pipeline does not exist.
    # We expect an exception to be raised
    scenario_manager.save(scenario_entity)
    with pytest.raises(NonExistingPipeline):
        scenario_manager.submit(scenario_entity.id)

    # scenario and pipeline do exist, but tasks does not exist.
    # We expect an exception to be raised
    pipeline_manager.save(pipeline_entity_1)
    pipeline_manager.save(pipeline_entity_2)
    with pytest.raises(NonExistingTask):
        scenario_manager.submit(scenario_entity.id)

    # scenario, pipeline, and tasks do exist.
    # We expect all the tasks to be submitted once,
    # and respecting specific constraints on the order
    task_manager.save(task_1)
    task_manager.save(task_2)
    task_manager.save(task_3)
    task_manager.save(task_4)
    task_manager.save(task_5)
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

    ds_1 = DataSourceConfig("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSourceConfig("bar", "embedded", Scope.SCENARIO, data=0)
    ds_6 = DataSourceConfig("baz", "embedded", Scope.PIPELINE, data=0)
    ds_4 = DataSourceConfig("qux", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = TaskConfig("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = TaskConfig("mult by 3", [ds_2], mult_by_3, ds_6)
    task_mult_by_4 = TaskConfig("mult by 4", [ds_1], mult_by_4, ds_4)
    pipeline_1 = PipelineConfig("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6
    pipeline_2 = PipelineConfig("by 4", [task_mult_by_4])
    # ds_1 ---> mult by 4 ---> ds_4
    scenario = Config.scenario_configs.create("Awesome scenario", [pipeline_1, pipeline_2])

    assert len(data_manager.get_data_sources()) == 0
    assert len(task_manager.tasks) == 0
    assert len(pipeline_manager.get_pipelines()) == 0
    assert len(scenario_manager.get_scenarios()) == 0

    scenario_entity = scenario_manager.create(scenario)

    assert len(data_manager.get_data_sources()) == 4
    assert len(task_manager.tasks) == 3
    assert len(pipeline_manager.get_pipelines()) == 2
    assert len(scenario_manager.get_scenarios()) == 1
    assert scenario_entity.foo.get() == 1
    assert scenario_entity.bar.get() == 0
    assert scenario_entity.baz.get() == 0
    assert scenario_entity.qux.get() == 0
    assert scenario_entity.by_6.get_sorted_tasks()[0][0].config_name == task_mult_by_2.name
    assert scenario_entity.by_6.get_sorted_tasks()[1][0].config_name == task_mult_by_3.name
    assert scenario_entity.by_4.get_sorted_tasks()[0][0].config_name == task_mult_by_4.name


def test_get_set_data():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    ds_1 = DataSourceConfig("foo", "embedded", Scope.PIPELINE, data=1)
    ds_2 = DataSourceConfig("bar", "embedded", Scope.SCENARIO, data=0)
    ds_6 = DataSourceConfig("baz", "embedded", Scope.PIPELINE, data=0)
    ds_4 = DataSourceConfig("qux", "embedded", Scope.PIPELINE, data=0)

    task_mult_by_2 = TaskConfig("mult by 2", [ds_1], mult_by_2, ds_2)
    task_mult_by_3 = TaskConfig("mult by 3", [ds_2], mult_by_3, ds_6)
    task_mult_by_4 = TaskConfig("mult by 4", [ds_1], mult_by_4, ds_4)
    pipeline_1 = PipelineConfig("by 6", [task_mult_by_2, task_mult_by_3])
    # ds_1 ---> mult by 2 ---> ds_2 ---> mult by 3 ---> ds_6
    pipeline_2 = PipelineConfig("by 4", [task_mult_by_4])
    # ds_1 ---> mult by 4 ---> ds_4
    scenario = Config.scenario_configs.create("Awesome scenario", [pipeline_1, pipeline_2])

    scenario_entity = scenario_manager.create(scenario)

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


class NotifyMock:
    def __init__(self, scenario):
        self.scenario = scenario
        self.nb_called = 0

    def __call__(self, scenario, job):
        assert scenario == self.scenario
        if self.nb_called == 0:
            assert job.is_pending()
        if self.nb_called == 1:
            assert job.is_running()
        if self.nb_called == 2:
            assert job.is_finished()
        self.nb_called += 1

    def assert_called_3_times(self):
        assert self.nb_called == 3

    def assert_not_called(self):
        assert self.nb_called == 0

    def reset(self):
        self.nb_called = 0


def test_notification():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    scenario_config = ScenarioConfig(
        "Awesome scenario",
        [
            PipelineConfig(
                "by 6",
                [
                    TaskConfig(
                        "mult by 2",
                        [DataSourceConfig("foo", "embedded", Scope.PIPELINE, data=1)],
                        mult_by_2,
                        DataSourceConfig("bar", "embedded", Scope.SCENARIO, data=0),
                    )
                ],
            )
        ],
    )
    scenario = scenario_manager.create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)
    scenario_manager.subscribe(notify_1)
    scenario_manager.subscribe(notify_2)

    scenario_manager.submit(scenario.id)
    notify_1.assert_called_3_times()
    notify_2.assert_called_3_times()
    scenario_manager.unsubscribe(notify_1)
    scenario_manager.unsubscribe(notify_2)


def test_notification_subscribe_unsubscribe():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    scenario_config = ScenarioConfig(
        "Awesome scenario",
        [
            PipelineConfig(
                "by 6",
                [
                    TaskConfig(
                        "mult by 2",
                        [DataSourceConfig("foo", "embedded", Scope.PIPELINE, data=1)],
                        mult_by_2,
                        DataSourceConfig("bar", "embedded", Scope.SCENARIO, data=0),
                    )
                ],
            )
        ],
    )

    scenario = scenario_manager.create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)

    scenario_manager.subscribe(notify_1)
    scenario_manager.subscribe(notify_2)

    scenario_manager.unsubscribe(notify_2)
    scenario_manager.submit(scenario.id)

    notify_1.assert_called_3_times()
    notify_2.assert_not_called()
    scenario_manager.unsubscribe(notify_1)

    with pytest.raises(KeyError):
        scenario_manager.unsubscribe(notify_2)


def test_notification_subscribe_only_on_new_jobs():
    scenario_manager = ScenarioManager()
    pipeline_manager = scenario_manager.pipeline_manager
    task_manager = scenario_manager.task_manager
    data_manager = scenario_manager.data_manager
    scenario_manager.delete_all()
    pipeline_manager.delete_all()
    data_manager.delete_all()
    task_manager.delete_all()

    scenario_config = ScenarioConfig(
        "Awesome scenario",
        [
            PipelineConfig(
                "by 6",
                [
                    TaskConfig(
                        "mult by 2",
                        [DataSourceConfig("foo", "embedded", Scope.PIPELINE, data=1)],
                        mult_by_2,
                        DataSourceConfig("bar", "embedded", Scope.SCENARIO, data=0),
                    )
                ],
            )
        ],
    )

    scenario = scenario_manager.create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)
    scenario_manager.subscribe(notify_1)

    scenario_manager.submit(scenario.id)

    scenario_manager.subscribe(notify_2)

    notify_1.assert_called_3_times()
    notify_2.assert_not_called()

    notify_1.reset()

    scenario_manager.submit(scenario.id)
    notify_1.assert_called_3_times()
    notify_2.assert_called_3_times()

    scenario_manager.unsubscribe(notify_1)
    scenario_manager.unsubscribe(notify_2)
