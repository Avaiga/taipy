import json
from multiprocessing import Process
from pathlib import Path
from unittest import mock

import pytest

from taipy.core.common import utils
from taipy.core.common.alias import PipelineId, TaskId
from taipy.core.config.config import Config
from taipy.core.data.data_manager import DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.pipeline import NonExistingPipeline
from taipy.core.exceptions.task import NonExistingTask
from taipy.core.job.job_manager import JobManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario_manager import ScenarioManager
from taipy.core.scheduler.scheduler import Scheduler
from taipy.core.scheduler.scheduler_factory import SchedulerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager
from tests.core.utils.NotifyMock import NotifyMock


@pytest.fixture()
def airflow_config():
    Config.set_job_config(mode=Config.job_config().MODE_VALUE_AIRFLOW, hostname="http://localhost:8080")
    yield
    Config.set_job_config(mode=Config.job_config().DEFAULT_MODE)


def test_set_and_get_pipeline():
    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_2 = Task("task", print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = Pipeline("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    assert PipelineManager.get(pipeline_id_1) is None
    assert PipelineManager.get(pipeline_1) is None
    assert PipelineManager.get(pipeline_id_2) is None
    assert PipelineManager.get(pipeline_2) is None

    # Save one pipeline. We expect to have only one pipeline stored
    PipelineManager.set(pipeline_1)
    assert PipelineManager.get(pipeline_id_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_id_1).tasks) == 0
    assert PipelineManager.get(pipeline_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_1).tasks) == 0
    assert PipelineManager.get(pipeline_id_2) is None
    assert PipelineManager.get(pipeline_2) is None

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    TaskManager.set(task_2)
    PipelineManager.set(pipeline_2)
    assert PipelineManager.get(pipeline_id_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_id_1).tasks) == 0
    assert PipelineManager.get(pipeline_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_1).tasks) == 0
    assert PipelineManager.get(pipeline_id_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_id_2).tasks) == 1
    assert PipelineManager.get(pipeline_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_2).tasks) == 1
    assert TaskManager.get(task_2.id).id == task_2.id

    # We save the first pipeline again. We expect nothing to change
    PipelineManager.set(pipeline_1)
    assert PipelineManager.get(pipeline_id_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_id_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_id_1).tasks) == 0
    assert PipelineManager.get(pipeline_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_1).config_name == pipeline_1.config_name
    assert len(PipelineManager.get(pipeline_1).tasks) == 0
    assert PipelineManager.get(pipeline_id_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_id_2).tasks) == 1
    assert PipelineManager.get(pipeline_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_2).tasks) == 1
    assert TaskManager.get(task_2.id).id == task_2.id

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    PipelineManager.set(pipeline_3_with_same_id)
    assert PipelineManager.get(pipeline_id_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_id_1).config_name == pipeline_3_with_same_id.config_name
    assert len(PipelineManager.get(pipeline_id_1).tasks) == 0
    assert PipelineManager.get(pipeline_1).id == pipeline_1.id
    assert PipelineManager.get(pipeline_1).config_name == pipeline_3_with_same_id.config_name
    assert len(PipelineManager.get(pipeline_1).tasks) == 0
    assert PipelineManager.get(pipeline_id_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_id_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_id_2).tasks) == 1
    assert PipelineManager.get(pipeline_2).id == pipeline_2.id
    assert PipelineManager.get(pipeline_2).config_name == pipeline_2.config_name
    assert len(PipelineManager.get(pipeline_2).tasks) == 1
    assert TaskManager.get(task_2.id).id == task_2.id


def test_submit():
    data_node_1 = InMemoryDataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.PIPELINE, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.PIPELINE, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.PIPELINE, "s7")
    task_1 = Task(
        "grault",
        print,
        [data_node_1, data_node_2],
        [data_node_3, data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))

    class MockScheduler(Scheduler):
        submit_calls = []

        def submit_task(self, task: Task, callbacks=None, force=False):
            self.submit_calls.append(task)
            return None

    TaskManager.scheduler = MockScheduler

    # pipeline does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingPipeline):
        PipelineManager.submit(pipeline.id)
    with pytest.raises(NonExistingPipeline):
        PipelineManager.submit(pipeline)

    # pipeline does exist, but tasks does not exist. We expect an exception to be raised
    PipelineManager.set(pipeline)
    with pytest.raises(NonExistingTask):
        PipelineManager.submit(pipeline.id)
    with pytest.raises(NonExistingTask):
        PipelineManager.submit(pipeline)

    # pipeline, and tasks does exist. We expect the tasks to be submitted
    # in a specific order
    TaskManager.set(task_1)
    TaskManager.set(task_2)
    TaskManager.set(task_3)
    TaskManager.set(task_4)

    PipelineManager.submit(pipeline.id)
    calls_ids = [t.id for t in TaskManager.scheduler().submit_calls]
    tasks_ids = [task_1.id, task_2.id, task_4.id, task_3.id]
    assert calls_ids == tasks_ids

    PipelineManager.submit(pipeline)
    calls_ids = [t.id for t in TaskManager.scheduler().submit_calls]
    tasks_ids = tasks_ids * 2
    assert set(calls_ids) == set(tasks_ids)
    TaskManager.scheduler = SchedulerFactory.build_scheduler


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data():
    # only create intermediate data node once

    dn_config_1 = Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.add_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_6 = Config.add_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)

    task_config_mult_by_2 = Config.add_task("mult by 2", mult_by_2, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.add_task("mult by 3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.add_pipeline("by 6", [task_config_mult_by_2, task_config_mult_by_3])
    # dn_1 ---> mult by 2 ---> dn_2 ---> mult by 3 ---> dn_6

    assert len(DataManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 0

    pipeline = PipelineManager.get_or_create(pipeline_config)

    assert len(DataManager.get_all()) == 3
    assert len(TaskManager.get_all()) == 2
    assert len(pipeline.get_sorted_tasks()) == 2
    assert pipeline.foo.read() == 1
    assert pipeline.bar.read() == 0
    assert pipeline.baz.read() == 0
    assert pipeline.get_sorted_tasks()[0][0].config_name == task_config_mult_by_2.name
    assert pipeline.get_sorted_tasks()[1][0].config_name == task_config_mult_by_3.name

    PipelineManager.submit(pipeline.id)
    assert pipeline.foo.read() == 1
    assert pipeline.bar.read() == 2
    assert pipeline.baz.read() == 6

    pipeline.foo.write("new data value")
    assert pipeline.foo.read() == "new data value"
    assert pipeline.bar.read() == 2
    assert pipeline.baz.read() == 6

    pipeline.bar.write(7)
    assert pipeline.foo.read() == "new data value"
    assert pipeline.bar.read() == 7
    assert pipeline.baz.read() == 6

    with pytest.raises(AttributeError):
        pipeline.WRONG.write(7)


def test_create_pipeline_and_modify_properties_does_not_modify_config():
    dn_config_1 = Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.add_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_6 = Config.add_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)

    task_config_mult_by_2 = Config.add_task("mult by 2", mult_by_2, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.add_task("mult by 3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.add_pipeline("by 6", [task_config_mult_by_2, task_config_mult_by_3], foo="bar")

    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"

    pipeline = PipelineManager.get_or_create(pipeline_config, None)
    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"
    assert len(pipeline.properties) == 1
    assert pipeline.properties.get("foo") == "bar"

    pipeline.properties["baz"] = "qux"
    PipelineManager.set(pipeline)
    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"
    assert len(pipeline.properties) == 2
    assert pipeline.properties.get("foo") == "bar"
    assert pipeline.properties.get("baz") == "qux"


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def test_pipeline_notification_subscribe(mocker):
    mocker.patch("taipy.core.common.reload.reload", side_effect=lambda m, o: o)

    pipeline_config = Config.add_pipeline(
        "by 6",
        [
            Config.add_task(
                "mult by 2",
                mult_by_2,
                [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.add_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = PipelineManager.get_or_create(pipeline_config)

    notify_1 = NotifyMock(pipeline)
    notify_1.__name__ = "notify_1"
    notify_1.__module__ = "notify_1"
    notify_2 = NotifyMock(pipeline)
    notify_2.__name__ = "notify_2"
    notify_2.__module__ = "notify_2"
    # Mocking this because NotifyMock is a class that does not loads correctly when getting the pipeline
    # from the storage.
    mocker.patch.object(utils, "load_fct", side_effect=[notify_1, notify_1, notify_2])

    # test subscription
    callback = mock.MagicMock()
    callback.__name__ = "callback"
    callback.__module__ = "callback"
    PipelineManager.submit(pipeline.id, [callback])
    callback.assert_called()

    # test pipeline subscribe notification
    PipelineManager.subscribe(notify_1, pipeline)
    PipelineManager.submit(pipeline.id)

    notify_1.assert_called_3_times()

    notify_1.reset()

    # test pipeline unsubscribe notification
    # test subscribe notification only on new job
    PipelineManager.unsubscribe(notify_1, pipeline)
    PipelineManager.subscribe(notify_2, pipeline)
    PipelineManager.submit(pipeline.id)

    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


def test_pipeline_notification_unsubscribe(mocker):
    mocker.patch("taipy.core.common.reload.reload", side_effect=lambda m, o: o)

    pipeline_config = Config.add_pipeline(
        "by 6",
        [
            Config.add_task(
                "mult by 2",
                mult_by_2,
                [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.add_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = PipelineManager.get_or_create(pipeline_config)

    notify_1 = notify1
    notify_2 = notify2

    PipelineManager.subscribe(notify_1, pipeline)
    PipelineManager.unsubscribe(notify_1, pipeline)
    PipelineManager.subscribe(notify_2, pipeline)
    PipelineManager.submit(pipeline.id)

    with pytest.raises(KeyError):
        PipelineManager.unsubscribe(notify_1, pipeline)
        PipelineManager.unsubscribe(notify_2, pipeline)


def test_pipeline_notification_subscribe_all():
    pipeline_config = Config.add_pipeline(
        "by 6",
        [
            Config.add_task(
                "mult by 2",
                mult_by_2,
                [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.add_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = PipelineManager.get_or_create(pipeline_config)
    pipeline_config.name = "other pipeline"

    other_pipeline = PipelineManager.get_or_create(pipeline_config)

    notify_1 = NotifyMock(pipeline)

    PipelineManager.subscribe(notify_1)

    assert len(PipelineManager.get(pipeline.id).subscribers) == 1
    assert len(PipelineManager.get(other_pipeline.id).subscribers) == 1


def test_get_all_by_config_name():
    input_configs = [Config.add_data_node("my_input", "in_memory")]
    task_config_1 = Config.add_task("task_config_1", print, input_configs, [])
    assert len(PipelineManager._get_all_by_config_name("NOT_EXISTING_CONFIG_NAME")) == 0
    pipeline_config_1 = Config.add_pipeline("foo", [task_config_1])
    assert len(PipelineManager._get_all_by_config_name("foo")) == 0

    PipelineManager.get_or_create(pipeline_config_1)
    assert len(PipelineManager._get_all_by_config_name("foo")) == 1

    pipeline_config_2 = Config.add_pipeline("baz", [task_config_1])
    PipelineManager.get_or_create(pipeline_config_2)
    assert len(PipelineManager._get_all_by_config_name("foo")) == 1
    assert len(PipelineManager._get_all_by_config_name("baz")) == 1

    PipelineManager.get_or_create(pipeline_config_2, "other_scenario")
    assert len(PipelineManager._get_all_by_config_name("foo")) == 1
    assert len(PipelineManager._get_all_by_config_name("baz")) == 2


def test_do_not_recreate_existing_pipeline_except_same_config():
    dn_input_config_scope_scenario = Config.add_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_scenario = Config.add_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.add_task("task_config", print, dn_input_config_scope_scenario, dn_output_config_scope_scenario)
    pipeline_config = Config.add_pipeline("pipeline_config_1", [task_config])

    # Scope is scenario
    pipeline_1 = PipelineManager.get_or_create(pipeline_config)
    assert len(PipelineManager.get_all()) == 1
    pipeline_2 = PipelineManager.get_or_create(pipeline_config)
    assert len(PipelineManager.get_all()) == 1
    assert pipeline_1.id == pipeline_2.id
    pipeline_3 = PipelineManager.get_or_create(pipeline_config, "a_scenario")  # Create even if the config is the same
    assert len(PipelineManager.get_all()) == 2
    assert pipeline_1.id == pipeline_2.id
    assert pipeline_3.id != pipeline_1.id
    assert pipeline_3.id != pipeline_2.id
    pipeline_4 = PipelineManager.get_or_create(pipeline_config, "a_scenario")  # Do not create because existed pipeline
    assert len(PipelineManager.get_all()) == 2
    assert pipeline_3.id == pipeline_4.id

    dn_input_config_scope_scenario_2 = Config.add_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_global_2 = Config.add_data_node("my_output_2", "in_memory", scope=Scope.GLOBAL)
    task_config_2 = Config.add_task(
        "task_config_2", print, dn_input_config_scope_scenario_2, dn_output_config_scope_global_2
    )
    pipeline_config_2 = Config.add_pipeline("pipeline_config_2", [task_config_2])

    # Scope is scenario and global
    pipeline_5 = PipelineManager.get_or_create(pipeline_config_2)
    assert len(PipelineManager.get_all()) == 3
    pipeline_6 = PipelineManager.get_or_create(pipeline_config_2)
    assert len(PipelineManager.get_all()) == 3
    assert pipeline_5.id == pipeline_6.id
    pipeline_7 = PipelineManager.get_or_create(pipeline_config_2, "another_scenario")
    assert len(PipelineManager.get_all()) == 4
    assert pipeline_7.id != pipeline_6.id
    assert pipeline_7.id != pipeline_5.id
    pipeline_8 = PipelineManager.get_or_create(pipeline_config_2, "another_scenario")
    assert len(PipelineManager.get_all()) == 4
    assert pipeline_7.id == pipeline_8.id

    dn_input_config_scope_global_3 = Config.add_data_node("my_input_3", "in_memory", scope=Scope.GLOBAL)
    dn_output_config_scope_global_3 = Config.add_data_node("my_output_3", "in_memory", scope=Scope.GLOBAL)
    task_config_3 = Config.add_task(
        "task_config_3", print, dn_input_config_scope_global_3, dn_output_config_scope_global_3
    )
    pipeline_config_3 = Config.add_pipeline("pipeline_config_3", [task_config_3])

    # Scope is global
    pipeline_9 = PipelineManager.get_or_create(pipeline_config_3)
    assert len(PipelineManager.get_all()) == 5
    pipeline_10 = PipelineManager.get_or_create(pipeline_config_3)
    assert len(PipelineManager.get_all()) == 5
    assert pipeline_9.id == pipeline_10.id
    pipeline_11 = PipelineManager.get_or_create(
        pipeline_config_3, "another_new_scenario"
    )  # Do not create because scope is global
    assert len(PipelineManager.get_all()) == 5
    assert pipeline_11.id == pipeline_10.id
    assert pipeline_11.id == pipeline_9.id

    dn_input_config_scope_pipeline_4 = Config.add_data_node("my_input_4", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_global_4 = Config.add_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.add_task(
        "task_config_4", print, dn_input_config_scope_pipeline_4, dn_output_config_scope_global_4
    )
    pipeline_config_4 = Config.add_pipeline("pipeline_config_4", [task_config_4])

    # Scope is global and pipeline
    pipeline_12 = PipelineManager.get_or_create(pipeline_config_4)
    assert len(PipelineManager.get_all()) == 6
    pipeline_13 = PipelineManager.get_or_create(pipeline_config_4)  # Create a new pipeline because new pipeline ID
    assert len(PipelineManager.get_all()) == 7
    assert pipeline_12.id != pipeline_13.id
    pipeline_14 = PipelineManager.get_or_create(pipeline_config_4, "another_new_scenario_2")
    assert len(PipelineManager.get_all()) == 8
    assert pipeline_14.id != pipeline_12.id
    assert pipeline_14.id != pipeline_13.id
    pipeline_15 = PipelineManager.get_or_create(
        pipeline_config_4, "another_new_scenario_2"
    )  # Don't create because scope is pipeline
    assert len(PipelineManager.get_all()) == 9
    assert pipeline_15.id != pipeline_14.id
    assert pipeline_15.id != pipeline_13.id
    assert pipeline_15.id != pipeline_12.id

    dn_input_config_scope_pipeline_5 = Config.add_data_node("my_input_5", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_scenario_5 = Config.add_data_node("my_output_5", "in_memory", scope=Scope.SCENARIO)
    task_config_5 = Config.add_task(
        "task_config_5", print, dn_input_config_scope_pipeline_5, dn_output_config_scope_scenario_5
    )
    pipeline_config_5 = Config.add_pipeline("pipeline_config_5", [task_config_5])

    # Scope is scenario and pipeline
    pipeline_16 = PipelineManager.get_or_create(pipeline_config_5)
    assert len(PipelineManager.get_all()) == 10
    pipeline_17 = PipelineManager.get_or_create(pipeline_config_5)
    assert len(PipelineManager.get_all()) == 11
    assert pipeline_16.id != pipeline_17.id
    pipeline_18 = PipelineManager.get_or_create(
        pipeline_config_5, "random_scenario"
    )  # Create because scope is pipeline
    assert len(PipelineManager.get_all()) == 12
    assert pipeline_18.id != pipeline_17.id
    assert pipeline_18.id != pipeline_16.id

    # create a second pipeline from the same config
    dn_input_config_scope_pipeline_6 = Config.add_data_node("my_input_6", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_pipeline_6 = Config.add_data_node("my_output_6", "in_memory", scope=Scope.PIPELINE)
    task_config_6 = Config.add_task(
        "task_config_6", print, dn_input_config_scope_pipeline_6, dn_output_config_scope_pipeline_6
    )
    pipeline_config_6 = Config.add_pipeline("pipeline_config_6", [task_config_6])

    pipeline_19 = PipelineManager.get_or_create(pipeline_config_6)
    assert len(PipelineManager.get_all()) == 13
    pipeline_20 = PipelineManager.get_or_create(pipeline_config_6)
    assert len(PipelineManager.get_all()) == 14
    assert pipeline_19.id != pipeline_20.id


def test_hard_delete():
    #  test hard delete with pipeline at pipeline level
    dn_input_config_1 = Config.add_data_node("my_input_1", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config_1 = Config.add_data_node("my_output_1", "in_memory", scope=Scope.PIPELINE, default_data="works !")
    task_config_1 = Config.add_task("task_config_1", print, dn_input_config_1, dn_output_config_1)
    pipeline_config_1 = Config.add_pipeline("pipeline_config_1", [task_config_1])
    pipeline_1 = PipelineManager.get_or_create(pipeline_config_1)
    PipelineManager.submit(pipeline_1.id)

    assert len(PipelineManager.get_all()) == 1
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1
    PipelineManager.hard_delete(pipeline_1.id)
    assert len(PipelineManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 0
    assert len(DataManager.get_all()) == 0
    assert len(JobManager.get_all()) == 0

    #  test hard delete with pipeline at scenario level
    dn_input_config_2 = Config.add_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config_2 = Config.add_data_node("my_output_2", "in_memory", scope=Scope.SCENARIO)
    task_config_2 = Config.add_task("task_config_2", print, dn_input_config_2, dn_output_config_2)
    pipeline_config_2 = Config.add_pipeline("pipeline_config_2", [task_config_2])
    pipeline_2 = PipelineManager.get_or_create(pipeline_config_2)
    PipelineManager.submit(pipeline_2.id)

    assert len(PipelineManager.get_all()) == 1
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1
    PipelineManager.hard_delete(pipeline_2.id)
    assert len(PipelineManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1

    ScenarioManager.delete_all()
    PipelineManager.delete_all()
    DataManager.delete_all()
    TaskManager.delete_all()
    JobManager.delete_all()

    #  test hard delete with pipeline at business level
    dn_input_config_3 = Config.add_data_node("my_input_3", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config_3 = Config.add_data_node("my_output_3", "in_memory", scope=Scope.CYCLE)
    task_config_3 = Config.add_task("task_config_3", print, dn_input_config_3, dn_output_config_3)
    pipeline_config_3 = Config.add_pipeline("pipeline_config_3", [task_config_3])
    pipeline_3 = PipelineManager.get_or_create(pipeline_config_3)
    PipelineManager.submit(pipeline_3.id)

    assert len(PipelineManager.get_all()) == 1
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1
    PipelineManager.hard_delete(pipeline_3.id)
    assert len(PipelineManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1

    ScenarioManager.delete_all()
    PipelineManager.delete_all()
    DataManager.delete_all()
    TaskManager.delete_all()
    JobManager.delete_all()

    #  test hard delete with pipeline at global level
    dn_input_config_4 = Config.add_data_node("my_input_4", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_output_config_4 = Config.add_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.add_task("task_config_4", print, dn_input_config_4, dn_output_config_4)
    pipeline_config_4 = Config.add_pipeline("pipeline_config_4", [task_config_4])
    pipeline_4 = PipelineManager.get_or_create(pipeline_config_4)
    PipelineManager.submit(pipeline_4.id)

    assert len(PipelineManager.get_all()) == 1
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1
    PipelineManager.hard_delete(pipeline_4.id)
    assert len(PipelineManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1

    ScenarioManager.delete_all()
    PipelineManager.delete_all()
    DataManager.delete_all()
    TaskManager.delete_all()
    JobManager.delete_all()

    dn_input_config_5 = Config.add_data_node("my_input_5", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config_5 = Config.add_data_node("my_output_5", "in_memory", scope=Scope.GLOBAL)
    task_config_5 = Config.add_task("task_config_5", print, dn_input_config_5, dn_output_config_5)
    pipeline_config_5 = Config.add_pipeline("pipeline_config_5", [task_config_5])
    pipeline_5 = PipelineManager.get_or_create(pipeline_config_5)
    PipelineManager.submit(pipeline_5.id)

    assert len(PipelineManager.get_all()) == 1
    assert len(TaskManager.get_all()) == 1
    assert len(DataManager.get_all()) == 2
    assert len(JobManager.get_all()) == 1
    PipelineManager.hard_delete(pipeline_5.id)
    assert len(PipelineManager.get_all()) == 0
    assert len(TaskManager.get_all()) == 0
    assert len(DataManager.get_all()) == 1
    assert len(JobManager.get_all()) == 0


def test_automatic_reload():
    dn_input_config = Config.add_data_node("input", "pickle", scope=Scope.PIPELINE, default_data=1)
    dn_output_config = Config.add_data_node("output", "pickle")
    task_config = Config.add_task("task_config", mult_by_2, dn_input_config, dn_output_config)
    pipeline_config = Config.add_pipeline("pipeline_config", [task_config])
    pipeline = PipelineManager.get_or_create(pipeline_config)

    p1 = Process(target=PipelineManager.submit, args=(pipeline,))
    p1.start()
    p1.join()

    assert 2 == pipeline.output.read()
