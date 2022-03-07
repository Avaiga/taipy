from datetime import datetime, timedelta
from multiprocessing import Process

import pytest

from taipy.core.common import _utils
from taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from taipy.core.common.frequency import Frequency
from taipy.core.config.config import Config
from taipy.core.cycle.cycle_manager import CycleManager
from taipy.core.data.data_manager import DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.data.scope import Scope
from taipy.core.exceptions.pipeline import NonExistingPipeline
from taipy.core.exceptions.scenario import (
    DeletingMasterScenario,
    DifferentScenarioConfigs,
    InsufficientScenarioToCompare,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
    UnauthorizedTagError,
)
from taipy.core.exceptions.task import NonExistingTask
from taipy.core.job.job_manager import JobManager
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_manager import ScenarioManager
from taipy.core.scheduler.scheduler import Scheduler
from taipy.core.scheduler.scheduler_factory import SchedulerFactory
from taipy.core.task.task import Task
from taipy.core.task.task_manager import TaskManager
from tests.core.utils.NotifyMock import NotifyMock


def test_set_and_get_scenario(cycle):
    scenario_id_1 = ScenarioId("scenario_id_1")
    scenario_1 = Scenario("scenario_name_1", [], {}, scenario_id_1)

    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_name = "task"
    task_2 = Task(task_name, print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_name_2 = "pipeline_name_2"
    pipeline_2 = Pipeline(pipeline_name_2, {}, [task_2], PipelineId("pipeline_id_2"))
    scenario_id_2 = ScenarioId("scenario_id_2")
    scenario_2 = Scenario("scenario_name_2", [pipeline_2], {}, scenario_id_2, datetime.now(), True, cycle)

    pipeline_3 = Pipeline("pipeline_name_3", {}, [], PipelineId("pipeline_id_3"))
    scenario_3_with_same_id = Scenario("scenario_name_3", [pipeline_3], {}, scenario_id_1, datetime.now(), False, cycle)

    # No existing scenario
    assert len(ScenarioManager._get_all()) == 0
    assert ScenarioManager._get(scenario_id_1) is None
    assert ScenarioManager._get(scenario_1) is None
    assert ScenarioManager._get(scenario_id_2) is None
    assert ScenarioManager._get(scenario_2) is None

    # Save one scenario. We expect to have only one scenario stored
    ScenarioManager._set(scenario_1)
    assert len(ScenarioManager._get_all()) == 1
    assert ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert ScenarioManager._get(scenario_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_1).pipelines) == 0
    assert ScenarioManager._get(scenario_id_2) is None
    assert ScenarioManager._get(scenario_2) is None

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    TaskManager._set(task_2)
    PipelineManager._set(pipeline_2)
    CycleManager._set(cycle)
    ScenarioManager._set(scenario_2)
    assert len(ScenarioManager._get_all()) == 2
    assert ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert ScenarioManager._get(scenario_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_1).pipelines) == 0
    assert ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert ScenarioManager._get(scenario_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_2).pipelines) == 1
    assert TaskManager._get(task_2.id).id == task_2.id
    assert ScenarioManager._get(scenario_id_2).cycle == cycle
    assert ScenarioManager._get(scenario_2).cycle == cycle
    assert CycleManager._get(cycle.id).id == cycle.id

    # We save the first scenario again. We expect nothing to change
    ScenarioManager._set(scenario_1)
    assert len(ScenarioManager._get_all()) == 2
    assert ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert ScenarioManager._get(scenario_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(ScenarioManager._get(scenario_1).pipelines) == 0
    assert ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert ScenarioManager._get(scenario_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_2).pipelines) == 1
    assert TaskManager._get(task_2.id).id == task_2.id
    assert CycleManager._get(cycle.id).id == cycle.id

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    TaskManager._set(scenario_2.pipelines[pipeline_name_2].tasks[task_name])
    PipelineManager._set(pipeline_3)
    ScenarioManager._set(scenario_3_with_same_id)
    assert len(ScenarioManager._get_all()) == 2
    assert ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_id_1).config_id == scenario_3_with_same_id.config_id
    assert len(ScenarioManager._get(scenario_id_1).pipelines) == 1
    assert ScenarioManager._get(scenario_id_1).cycle == cycle
    assert ScenarioManager._get(scenario_1).id == scenario_1.id
    assert ScenarioManager._get(scenario_1).config_id == scenario_3_with_same_id.config_id
    assert len(ScenarioManager._get(scenario_1).pipelines) == 1
    assert ScenarioManager._get(scenario_1).cycle == cycle
    assert ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert ScenarioManager._get(scenario_2).id == scenario_2.id
    assert ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(ScenarioManager._get(scenario_2).pipelines) == 1
    assert TaskManager._get(task_2.id).id == task_2.id


def test_create_scenario_does_not_modify_config():
    creation_date_1 = datetime.now()
    display_name_1 = "display_name_1"
    scenario_config = Config.add_scenario("sc", [], Frequency.DAILY)
    assert scenario_config.properties.get("display_name") is None
    assert len(scenario_config.properties) == 0

    scenario = ScenarioManager.create(scenario_config, creation_date=creation_date_1, display_name=display_name_1)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 1
    assert scenario.properties.get("display_name") == display_name_1

    scenario.properties["foo"] = "bar"
    ScenarioManager._set(scenario)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 2
    assert scenario.properties.get("foo") == "bar"
    assert scenario.properties.get("display_name") == display_name_1


def test_create_and_delete_scenario():
    creation_date_1 = datetime.now()
    creation_date_2 = creation_date_1 + timedelta(minutes=10)

    display_name_1 = "display_name_1"

    ScenarioManager._delete_all()
    assert len(ScenarioManager._get_all()) == 0

    scenario_config = Config.add_scenario("sc", [], Frequency.DAILY)

    scenario_1 = ScenarioManager.create(scenario_config, creation_date=creation_date_1, display_name=display_name_1)
    assert scenario_1.config_id == "sc"
    assert scenario_1.pipelines == {}
    assert scenario_1.cycle.frequency == Frequency.DAILY
    assert scenario_1.is_master
    assert scenario_1.cycle.creation_date == creation_date_1
    assert scenario_1.cycle.start_date.date() == creation_date_1.date()
    assert scenario_1.cycle.end_date.date() == creation_date_1.date()
    assert scenario_1.creation_date == creation_date_1
    assert scenario_1.display_name == display_name_1
    assert scenario_1.properties["display_name"] == display_name_1
    assert scenario_1.tags == set()

    with pytest.raises(DeletingMasterScenario):
        ScenarioManager._delete(scenario_1.id)

    scenario_2 = ScenarioManager.create(scenario_config, creation_date=creation_date_2)
    assert scenario_2.config_id == "sc"
    assert scenario_2.pipelines == {}
    assert scenario_2.cycle.frequency == Frequency.DAILY
    assert not scenario_2.is_master
    assert scenario_2.cycle.creation_date == creation_date_1
    assert scenario_2.cycle.start_date.date() == creation_date_2.date()
    assert scenario_2.cycle.end_date.date() == creation_date_2.date()
    assert scenario_2.properties.get("display_name") is None
    assert scenario_2.tags == set()

    assert scenario_1 != scenario_2
    assert scenario_1.cycle == scenario_2.cycle

    assert len(ScenarioManager._get_all()) == 2
    ScenarioManager._delete(scenario_2.id)
    assert len(ScenarioManager._get_all()) == 1
    with pytest.raises(DeletingMasterScenario):
        ScenarioManager._delete(scenario_1.id)
    assert ScenarioManager._get(scenario_2) is None


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_scenario_manager_only_creates_data_node_once():
    dn_config_1 = Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.add_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.add_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_4 = Config.add_data_node("qux", "in_memory", Scope.PIPELINE, default_data=0)

    task_mult_by_2_config = Config.add_task("mult by 2", mult_by_2, [dn_config_1], dn_config_2)
    task_mult_by_3_config = Config.add_task("mult by 3", mult_by_3, [dn_config_2], dn_config_6)
    task_mult_by_4_config = Config.add_task("mult by 4", mult_by_4, [dn_config_1], dn_config_4)
    pipeline_config_1 = Config.add_pipeline("by 6", [task_mult_by_2_config, task_mult_by_3_config])
    # dn_1 ---> mult by 2 ---> dn_2 ---> mult by 3 ---> dn_6
    pipeline_config_2 = Config.add_pipeline("by 4", [task_mult_by_4_config])
    # dn_1 ---> mult by 4 ---> dn_4
    scenario_config = Config.add_scenario("Awesome scenario", [pipeline_config_1, pipeline_config_2], Frequency.DAILY)

    assert len(DataManager._get_all()) == 0
    assert len(TaskManager._get_all()) == 0
    assert len(PipelineManager._get_all()) == 0
    assert len(ScenarioManager._get_all()) == 0
    assert len(CycleManager._get_all()) == 0

    scenario = ScenarioManager.create(scenario_config)

    assert len(DataManager._get_all()) == 5
    assert len(TaskManager._get_all()) == 3
    assert len(PipelineManager._get_all()) == 2
    assert len(ScenarioManager._get_all()) == 1
    assert scenario.foo.read() == 1
    assert scenario.bar.read() == 0
    assert scenario.baz.read() == 0
    assert scenario.qux.read() == 0
    assert scenario.by_6.get_sorted_tasks()[0][0].config_id == task_mult_by_2_config.id
    assert scenario.by_6.get_sorted_tasks()[1][0].config_id == task_mult_by_3_config.id
    assert scenario.by_4.get_sorted_tasks()[0][0].config_id == task_mult_by_4_config.id
    assert scenario.cycle.frequency == Frequency.DAILY


def test_notification_subscribe(mocker):
    mocker.patch("taipy.core.common._reload.reload", side_effect=lambda m, o: o)

    scenario_config = Config.add_scenario(
        "Awesome scenario",
        [
            Config.add_pipeline(
                "by 6",
                [
                    Config.add_task(
                        "mult by 2",
                        mult_by_2,
                        [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.add_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    scenario = ScenarioManager.create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)
    mocker.patch.object(_utils, "_load_fct", side_effect=[notify_1, notify_1, notify_2])
    # test subscribing notification
    ScenarioManager.subscribe(notify_1, scenario)
    ScenarioManager.submit(scenario.id)
    notify_1.assert_called_3_times()

    notify_1.reset()

    # test unsubscribing notification
    # test notis subscribe only on new jobs
    ScenarioManager.unsubscribe(notify_1, scenario)
    ScenarioManager.subscribe(notify_2, scenario)
    ScenarioManager.submit(scenario.id)

    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def test_notification_unsubscribe(mocker):
    mocker.patch("taipy.core.common._reload.reload", side_effect=lambda m, o: o)

    scenario_config = Config.add_scenario(
        "Awesome scenario",
        [
            Config.add_pipeline(
                "by 6",
                [
                    Config.add_task(
                        "mult by 2",
                        mult_by_2,
                        [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.add_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    scenario = ScenarioManager.create(scenario_config)

    notify_1 = notify1
    notify_2 = notify2

    # test subscribing notification
    ScenarioManager.subscribe(notify_1, scenario)
    ScenarioManager.unsubscribe(notify_1, scenario)
    ScenarioManager.subscribe(notify_2, scenario)
    ScenarioManager.submit(scenario.id)

    with pytest.raises(KeyError):
        ScenarioManager.unsubscribe(notify_1, scenario)
    ScenarioManager.unsubscribe(notify_2, scenario)


def test_scenario_notification_subscribe_all():
    scenario_config = Config.add_scenario(
        "Awesome scenario",
        [
            Config.add_pipeline(
                "by 6",
                [
                    Config.add_task(
                        "mult by 2",
                        mult_by_2,
                        [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.add_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    scenario = ScenarioManager.create(scenario_config)
    scenario_config.id = "other scenario"

    other_scenario = ScenarioManager.create(scenario_config)

    notify_1 = NotifyMock(scenario)

    ScenarioManager.subscribe(notify_1)

    assert len(ScenarioManager._get(scenario.id).subscribers) == 1
    assert len(ScenarioManager._get(other_scenario.id).subscribers) == 1


def test_get_set_master_scenario():
    cycle_1 = CycleManager.create(Frequency.DAILY)

    scenario_1 = Scenario("sc_1", [], {}, ScenarioId("sc_1"), is_master=False, cycle=cycle_1)
    scenario_2 = Scenario("sc_2", [], {}, ScenarioId("sc_2"), is_master=False, cycle=cycle_1)

    ScenarioManager._delete_all()
    CycleManager._delete_all()

    assert len(ScenarioManager._get_all()) == 0
    assert len(CycleManager._get_all()) == 0

    CycleManager._set(cycle_1)

    ScenarioManager._set(scenario_1)
    ScenarioManager._set(scenario_2)

    assert len(ScenarioManager.get_all_masters()) == 0
    assert len(ScenarioManager.get_all_by_cycle(cycle_1)) == 2

    ScenarioManager.set_master(scenario_1)

    assert len(ScenarioManager.get_all_masters()) == 1
    assert len(ScenarioManager.get_all_by_cycle(cycle_1)) == 2
    assert ScenarioManager.get_master(cycle_1) == scenario_1

    ScenarioManager.set_master(scenario_2)

    assert len(ScenarioManager.get_all_masters()) == 1
    assert len(ScenarioManager.get_all_by_cycle(cycle_1)) == 2
    assert ScenarioManager.get_master(cycle_1) == scenario_2


def test_hard_delete():
    dn_input_config = Config.add_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.add_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.add_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.add_pipeline("pipeline_config", [task_config])
    scenario_config = Config.add_scenario("scenario_config", [pipeline_config])
    scenario = ScenarioManager.create(scenario_config)
    ScenarioManager.submit(scenario.id)

    # test delete relevant entities with scenario scope
    assert len(TaskManager._get_all()) == 1
    assert len(PipelineManager._get_all()) == 1
    assert len(ScenarioManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 1
    ScenarioManager.hard_delete(scenario.id)
    assert len(ScenarioManager._get_all()) == 0
    assert len(PipelineManager._get_all()) == 0
    assert len(TaskManager._get_all()) == 0
    assert len(DataManager._get_all()) == 0
    assert len(JobManager._get_all()) == 0

    ScenarioManager._delete_all()
    PipelineManager._delete_all()
    DataManager._delete_all()
    TaskManager._delete_all()
    JobManager._delete_all()

    dn_input_config_1 = Config.add_data_node("my_input_1", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config_1 = Config.add_data_node("my_output_1", "in_memory", scope=Scope.PIPELINE)
    task_config_1 = Config.add_task("task_config_1", print, dn_input_config_1, dn_output_config_1)
    pipeline_config_1 = Config.add_pipeline("pipeline_config_2", [task_config_1])
    scenario_config_1 = Config.add_scenario("scenario_config_2", [pipeline_config_1])
    scenario_1 = ScenarioManager.create(scenario_config_1)
    ScenarioManager.submit(scenario_1.id)

    # test delete relevant entities with pipeline scope
    assert len(TaskManager._get_all()) == 1
    assert len(PipelineManager._get_all()) == 1
    assert len(ScenarioManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 1
    ScenarioManager.hard_delete(scenario_1.id)
    assert len(ScenarioManager._get_all()) == 0
    assert len(PipelineManager._get_all()) == 0
    assert len(TaskManager._get_all()) == 0
    assert len(DataManager._get_all()) == 0
    assert len(JobManager._get_all()) == 0

    dn_input_config_2 = Config.add_data_node("my_input_2", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config_2 = Config.add_data_node("my_output_2", "in_memory", scope=Scope.SCENARIO)
    task_config_2 = Config.add_task("task_config_2", print, dn_input_config_2, dn_output_config_2)
    pipeline_config_2 = Config.add_pipeline("pipeline_config_2", [task_config_2])
    scenario_config_2 = Config.add_scenario("scenario_config_2", [pipeline_config_2])
    scenario_2 = ScenarioManager.create(scenario_config_2)
    ScenarioManager.submit(scenario_2.id)

    # test delete relevant entities with pipeline scope
    assert len(TaskManager._get_all()) == 1
    assert len(PipelineManager._get_all()) == 1
    assert len(ScenarioManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 1
    ScenarioManager.hard_delete(scenario_2.id)  # Do not delete because of pipeline scope
    assert len(ScenarioManager._get_all()) == 0
    assert len(PipelineManager._get_all()) == 0
    assert len(TaskManager._get_all()) == 0
    assert len(DataManager._get_all()) == 1
    assert len(JobManager._get_all()) == 0

    ScenarioManager._delete_all()
    PipelineManager._delete_all()
    DataManager._delete_all()
    TaskManager._delete_all()
    JobManager._delete_all()

    dn_input_config_3 = Config.add_data_node("my_input_3", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config_3 = Config.add_data_node("my_output_3", "in_memory", scope=Scope.CYCLE)
    task_config_3 = Config.add_task("task_config", print, dn_input_config_3, dn_output_config_3)
    pipeline_config_3 = Config.add_pipeline("pipeline_config", [task_config_3])
    scenario_config_3 = Config.add_scenario("scenario_config_3", [pipeline_config_3])
    scenario_3 = ScenarioManager.create(scenario_config_3)
    scenario_4 = ScenarioManager.create(scenario_config_3)
    ScenarioManager.submit(scenario_3.id)
    ScenarioManager.submit(scenario_4.id)

    # test delete relevant entities with cycle scope
    assert len(ScenarioManager._get_all()) == 2
    assert len(PipelineManager._get_all()) == 1
    assert len(TaskManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 2
    ScenarioManager.hard_delete(scenario_3.id)  # Only delete scenario 3
    assert len(ScenarioManager._get_all()) == 1
    assert len(PipelineManager._get_all()) == 1
    assert len(TaskManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 2
    assert ScenarioManager._get(scenario_4.id) is not None

    ScenarioManager._delete_all()
    PipelineManager._delete_all()
    DataManager._delete_all()
    TaskManager._delete_all()
    JobManager._delete_all()

    dn_input_config_4 = Config.add_data_node("my_input_4", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_output_config_4 = Config.add_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.add_task("task_config_4", print, dn_input_config_4, dn_output_config_4)
    pipeline_config_4 = Config.add_pipeline("pipeline_config", [task_config_4])
    scenario_config_4 = Config.add_scenario("scenario_config_4", [pipeline_config_4])
    scenario_5 = ScenarioManager.create(scenario_config_4)
    scenario_6 = ScenarioManager.create(scenario_config_4)
    ScenarioManager.submit(scenario_5.id)
    ScenarioManager.submit(scenario_6.id)

    # test delete relevant entities with global scope
    assert len(ScenarioManager._get_all()) == 2
    assert len(PipelineManager._get_all()) == 1
    assert len(TaskManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 2
    ScenarioManager.hard_delete(scenario_5.id)  # Only delete scenario 5
    assert len(ScenarioManager._get_all()) == 1
    assert len(PipelineManager._get_all()) == 1
    assert len(TaskManager._get_all()) == 1
    assert len(DataManager._get_all()) == 2
    assert len(JobManager._get_all()) == 2
    assert ScenarioManager._get(scenario_6.id) is not None


def test_submit():
    data_node_1 = InMemoryDataNode("foo", Scope.PIPELINE, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.PIPELINE, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.PIPELINE, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.PIPELINE, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.PIPELINE, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.PIPELINE, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.PIPELINE, "s7")
    data_node_8 = InMemoryDataNode("fum", Scope.PIPELINE, "s8")
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
    task_5 = Task("thud", print, [data_node_6], [data_node_8], TaskId("t5"))
    pipeline_1 = Pipeline("plugh", {}, [task_4, task_2, task_1, task_3], PipelineId("p1"))
    pipeline_2 = Pipeline("xyzzy", {}, [task_5], PipelineId("p2"))

    scenario = Scenario(
        "scenario_name",
        [pipeline_2, pipeline_1],
        {},
        ScenarioId("sce_id"),
    )

    class MockScheduler(Scheduler):
        submit_calls = []

        def submit_task(self, task: Task, callbacks=None, force=False):
            self.submit_calls.append(task.id)
            return super().submit_task(task, callbacks)

    TaskManager.scheduler = MockScheduler

    with pytest.raises(NonExistingScenario):
        ScenarioManager.submit(scenario.id)
    with pytest.raises(NonExistingScenario):
        ScenarioManager.submit(scenario)

    # scenario does exist, but pipeline does not exist.
    # We expect an exception to be raised
    ScenarioManager._set(scenario)
    with pytest.raises(NonExistingPipeline):
        ScenarioManager.submit(scenario.id)
    with pytest.raises(NonExistingPipeline):
        ScenarioManager.submit(scenario)

    # scenario and pipeline do exist, but tasks does not exist.
    # We expect an exception to be raised
    PipelineManager._set(pipeline_1)
    PipelineManager._set(pipeline_2)
    with pytest.raises(NonExistingTask):
        ScenarioManager.submit(scenario.id)
    with pytest.raises(NonExistingTask):
        ScenarioManager.submit(scenario)

    # scenario, pipeline, and tasks do exist.
    # We expect all the tasks to be submitted once,
    # and respecting specific constraints on the order
    TaskManager._set(task_1)
    TaskManager._set(task_2)
    TaskManager._set(task_3)
    TaskManager._set(task_4)
    TaskManager._set(task_5)
    ScenarioManager.submit(scenario.id)
    submit_calls = TaskManager.scheduler().submit_calls
    assert len(submit_calls) == 5
    assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
    assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)

    ScenarioManager.submit(scenario)
    submit_calls = TaskManager.scheduler().submit_calls
    assert len(submit_calls) == 10
    assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
    assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)

    TaskManager.scheduler = SchedulerFactory.build_scheduler


def test_scenarios_comparison():
    def subtraction(inp, out):
        return inp - out

    def addition(inp, out):
        return inp + out

    ScenarioManager._delete_all()
    PipelineManager._delete_all()
    DataManager._delete_all()
    TaskManager._delete_all()

    scenario_config = Config.add_scenario(
        "Awesome scenario",
        [
            Config.add_pipeline(
                "by 6",
                [
                    Config.add_task(
                        "mult by 2",
                        mult_by_2,
                        [Config.add_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.add_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
        comparators={"bar": [subtraction], "foo": [subtraction, addition]},
    )

    assert scenario_config.comparators is not None

    scenario_1 = ScenarioManager.create(scenario_config)
    scenario_2 = ScenarioManager.create(scenario_config)

    with pytest.raises(InsufficientScenarioToCompare):
        ScenarioManager.compare(scenario_1, data_node_config_id="bar")

    scenario_3 = Scenario("awesome_scenario_config", [], {})
    with pytest.raises(DifferentScenarioConfigs):
        ScenarioManager.compare(scenario_1, scenario_3, data_node_config_id="bar")

    ScenarioManager.submit(scenario_1.id)
    ScenarioManager.submit(scenario_2.id)

    bar_comparison = ScenarioManager.compare(scenario_1, scenario_2, data_node_config_id="bar")["bar"]
    assert bar_comparison["subtraction"] == 0

    foo_comparison = ScenarioManager.compare(scenario_1, scenario_2, data_node_config_id="foo")["foo"]
    assert len(foo_comparison.keys()) == 2
    assert foo_comparison["addition"] == 2
    assert foo_comparison["subtraction"] == 0

    assert len(ScenarioManager.compare(scenario_1, scenario_2).keys()) == 2

    with pytest.raises(NonExistingScenarioConfig):
        ScenarioManager.compare(scenario_3, scenario_3)

    with pytest.raises(NonExistingComparator):
        ScenarioManager.compare(scenario_1, scenario_2, data_node_config_id="abc")


def test_automatic_reload():
    scenario_config = Config.add_scenario(
        "Awesome scenario",
        [
            Config.add_pipeline(
                "by 6",
                [
                    Config.add_task(
                        "mult by 2",
                        mult_by_2,
                        [Config.add_data_node("foo", "pickle", Scope.PIPELINE, default_data=1)],
                        Config.add_data_node("bar", "pickle", Scope.SCENARIO),
                    )
                ],
            )
        ],
    )
    scenario = ScenarioManager.create(scenario_config)
    p = Process(target=ScenarioManager.submit, args=(scenario,))
    p.start()
    p.join()

    assert 2 == scenario.bar.read()


def test_tags():
    cycle_1 = CycleManager.create(Frequency.DAILY, name="today", creation_date=datetime.now())
    cycle_2 = CycleManager.create(Frequency.DAILY, name="tomorrow", creation_date=datetime.now() + timedelta(days=1))
    cycle_3 = CycleManager.create(Frequency.DAILY, name="yesterday", creation_date=datetime.now() + timedelta(days=-1))

    scenario_no_tag = Scenario("SCENARIO_no_tag", [], {}, ScenarioId("SCENARIO_no_tag"), cycle=cycle_1)
    scenario_1_tag = Scenario("SCENARIO_1_tag", [], {}, ScenarioId("SCENARIO_1_tag"), cycle=cycle_1, tags={"fst"})
    scenario_2_tags = Scenario(
        "SCENARIO_2_tags", [], {}, ScenarioId("SCENARIO_2_tags"), cycle=cycle_2, tags={"fst", "scd"}
    )

    # Test has_tag
    assert len(scenario_no_tag.tags) == 0
    assert not scenario_no_tag.has_tag("fst")
    assert not scenario_no_tag.has_tag("scd")

    assert len(scenario_1_tag.tags) == 1
    assert scenario_1_tag.has_tag("fst")
    assert not scenario_1_tag.has_tag("scd")

    assert len(scenario_2_tags.tags) == 2
    assert scenario_2_tags.has_tag("fst")
    assert scenario_2_tags.has_tag("scd")

    # test get and set serialize/deserialize tags
    CycleManager._set(cycle_1)
    CycleManager._set(cycle_2)
    CycleManager._set(cycle_3)
    ScenarioManager._set(scenario_no_tag)
    ScenarioManager._set(scenario_1_tag)
    ScenarioManager._set(scenario_2_tags)

    assert len(ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).tags) == 0
    assert not ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).has_tag("fst")
    assert not ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).has_tag("scd")

    assert len(ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags) == 1
    assert "fst" in ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags
    assert "scd" not in ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags

    assert len(ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags) == 2
    assert "fst" in ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags
    assert "scd" in ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags

    # Test tag & untag

    ScenarioManager.tag(scenario_no_tag, "thd")  # add new tag
    ScenarioManager.untag(scenario_1_tag, "NOT_EXISTING_TAG")  # remove not existing tag does nothing
    ScenarioManager.untag(scenario_1_tag, "fst")  # remove `fst` tag

    assert len(scenario_no_tag.tags) == 1
    assert not scenario_no_tag.has_tag("fst")
    assert not scenario_no_tag.has_tag("scd")
    assert scenario_no_tag.has_tag("thd")

    assert len(scenario_1_tag.tags) == 0
    assert not scenario_1_tag.has_tag("fst")
    assert not scenario_1_tag.has_tag("scd")
    assert not scenario_1_tag.has_tag("thd")

    assert len(scenario_2_tags.tags) == 2
    assert scenario_2_tags.has_tag("fst")
    assert scenario_2_tags.has_tag("scd")
    assert not scenario_2_tags.has_tag("thd")

    ScenarioManager.untag(scenario_no_tag, "thd")
    ScenarioManager._set(scenario_no_tag)
    ScenarioManager.tag(scenario_1_tag, "fst")
    ScenarioManager._set(scenario_1_tag)

    # test getters
    assert not ScenarioManager.get_by_tag(cycle_3, "fst")
    assert not ScenarioManager.get_by_tag(cycle_3, "scd")
    assert not ScenarioManager.get_by_tag(cycle_3, "thd")

    assert ScenarioManager.get_by_tag(cycle_2, "fst") == scenario_2_tags
    assert ScenarioManager.get_by_tag(cycle_2, "scd") == scenario_2_tags
    assert not ScenarioManager.get_by_tag(cycle_2, "thd")

    assert ScenarioManager.get_by_tag(cycle_1, "fst") == scenario_1_tag
    assert not ScenarioManager.get_by_tag(cycle_1, "scd")
    assert not ScenarioManager.get_by_tag(cycle_1, "thd")

    assert len(ScenarioManager.get_all_by_tag("NOT_EXISTING")) == 0
    assert scenario_1_tag in ScenarioManager.get_all_by_tag("fst")
    assert scenario_2_tags in ScenarioManager.get_all_by_tag("fst")
    assert ScenarioManager.get_all_by_tag("scd") == [scenario_2_tags]
    assert len(ScenarioManager.get_all_by_tag("thd")) == 0

    # test tag cycle mgt

    ScenarioManager.tag(scenario_no_tag, "fst")  # tag sc_no_tag should untag sc_1_tag with same cycle but not sc_2_tags

    assert not ScenarioManager.get_by_tag(cycle_3, "fst")
    assert not ScenarioManager.get_by_tag(cycle_3, "scd")
    assert not ScenarioManager.get_by_tag(cycle_3, "thd")

    assert ScenarioManager.get_by_tag(cycle_2, "fst") == scenario_2_tags
    assert ScenarioManager.get_by_tag(cycle_2, "scd") == scenario_2_tags
    assert not ScenarioManager.get_by_tag(cycle_2, "thd")

    assert ScenarioManager.get_by_tag(cycle_1, "fst") == scenario_no_tag
    assert not ScenarioManager.get_by_tag(cycle_1, "scd")
    assert not ScenarioManager.get_by_tag(cycle_1, "thd")

    assert len(ScenarioManager.get_all_by_tag("NOT_EXISTING")) == 0
    assert len(ScenarioManager.get_all_by_tag("fst")) == 2
    assert scenario_2_tags in ScenarioManager.get_all_by_tag("fst")
    assert scenario_no_tag in ScenarioManager.get_all_by_tag("fst")
    assert ScenarioManager.get_all_by_tag("scd") == [scenario_2_tags]
    assert len(ScenarioManager.get_all_by_tag("thd")) == 0


def test_authorized_tags():
    scenario = Scenario("SCENARIO_1", [], {"authorized_tags": ["foo", "bar"]}, ScenarioId("SCENARIO_1"))
    scenario_2_cfg = Config.add_scenario("SCENARIO_2", [], Frequency.DAILY, authorized_tags=["foo", "bar"])
    scenario_2 = ScenarioManager.create(scenario_2_cfg)
    ScenarioManager._set(scenario)

    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    with pytest.raises(UnauthorizedTagError):
        ScenarioManager.tag(scenario, "baz")
        ScenarioManager.tag(scenario_2, "baz")
    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    ScenarioManager.tag(scenario, "foo")
    ScenarioManager.tag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1

    ScenarioManager.tag(scenario, "bar")
    ScenarioManager.tag(scenario_2, "bar")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    ScenarioManager.tag(scenario, "foo")
    ScenarioManager.tag(scenario_2, "foo")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    ScenarioManager.untag(scenario, "foo")
    ScenarioManager.untag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1
