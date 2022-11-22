# Copyright 2022 Avaiga Private Limited
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
from unittest.mock import ANY

import pytest

from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.common import _utils
from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.common.alias import PipelineId, ScenarioId, TaskId
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import (
    DeletingPrimaryScenario,
    DifferentScenarioConfigs,
    InsufficientScenarioToCompare,
    NonExistingComparator,
    NonExistingPipeline,
    NonExistingScenario,
    NonExistingScenarioConfig,
    NonExistingTask,
    UnauthorizedTagError,
)
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.scenario.scenario import Scenario
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from tests.core.utils import assert_true_after_1_minute_max
from tests.core.utils.NotifyMock import NotifyMock


def test_set_and_get_scenario(cycle):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

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
    assert len(_ScenarioManager._get_all()) == 0
    assert _ScenarioManager._get(scenario_id_1) is None
    assert _ScenarioManager._get(scenario_1) is None
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save one scenario. We expect to have only one scenario stored
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2) is None
    assert _ScenarioManager._get(scenario_2) is None

    # Save a second scenario. Now, we expect to have a total of two scenarios stored
    _TaskManager._set(task_2)
    _PipelineManager._set(pipeline_2)
    _CycleManager._set(cycle)
    _ScenarioManager._set(scenario_2)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _ScenarioManager._get(scenario_id_2).cycle == cycle
    assert _ScenarioManager._get(scenario_2).cycle == cycle
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save the first scenario again. We expect nothing to change
    _ScenarioManager._set(scenario_1)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_1.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 0
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id
    assert _CycleManager._get(cycle.id).id == cycle.id

    # We save a third scenario with same id as the first one.
    # We expect the first scenario to be updated
    _TaskManager._set(scenario_2.pipelines[pipeline_name_2].tasks[task_name])
    _PipelineManager._set(pipeline_3)
    _ScenarioManager._set(scenario_3_with_same_id)
    assert len(_ScenarioManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_id_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_id_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_id_1).pipelines) == 1
    assert _ScenarioManager._get(scenario_id_1).cycle == cycle
    assert _ScenarioManager._get(scenario_1).id == scenario_1.id
    assert _ScenarioManager._get(scenario_1).config_id == scenario_3_with_same_id.config_id
    assert len(_ScenarioManager._get(scenario_1).pipelines) == 1
    assert _ScenarioManager._get(scenario_1).cycle == cycle
    assert _ScenarioManager._get(scenario_id_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_id_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_id_2).pipelines) == 1
    assert _ScenarioManager._get(scenario_2).id == scenario_2.id
    assert _ScenarioManager._get(scenario_2).config_id == scenario_2.config_id
    assert len(_ScenarioManager._get(scenario_2).pipelines) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


def test_create_scenario_does_not_modify_config():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    creation_date_1 = datetime.now()
    name_1 = "name_1"
    scenario_config = Config.configure_scenario("sc", [], Frequency.DAILY)
    assert scenario_config.properties.get("name") is None
    assert len(scenario_config.properties) == 0

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 1
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario.properties["foo"] = "bar"
    _ScenarioManager._set(scenario)
    assert len(scenario_config.properties) == 0
    assert len(scenario.properties) == 2
    assert scenario.properties.get("foo") == "bar"
    assert scenario.properties.get("name") == name_1
    assert scenario.name == name_1

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1)
    assert scenario_2.name is None


def test_create_and_delete_scenario():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    creation_date_1 = datetime.now()
    creation_date_2 = creation_date_1 + timedelta(minutes=10)

    name_1 = "name_1"

    _ScenarioManager._delete_all()
    assert len(_ScenarioManager._get_all()) == 0

    scenario_config = Config.configure_scenario("sc", [], Frequency.DAILY)

    _SchedulerFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)
    assert scenario_1.config_id == "sc"
    assert scenario_1.pipelines == {}
    assert scenario_1.cycle.frequency == Frequency.DAILY
    assert scenario_1.is_primary
    assert scenario_1.cycle.creation_date == creation_date_1
    assert scenario_1.cycle.start_date.date() == creation_date_1.date()
    assert scenario_1.cycle.end_date.date() == creation_date_1.date()
    assert scenario_1.creation_date == creation_date_1
    assert scenario_1.name == name_1
    assert scenario_1.properties["name"] == name_1
    assert scenario_1.tags == set()

    cycle_id_1 = scenario_1.cycle.id
    assert _CycleManager._get(cycle_id_1).id == cycle_id_1
    _ScenarioManager._delete(scenario_1.id)
    assert _ScenarioManager._get(scenario_1.id) is None
    assert _CycleManager._get(cycle_id_1) is None

    # Recreate scenario_1
    scenario_1 = _ScenarioManager._create(scenario_config, creation_date=creation_date_1, name=name_1)

    scenario_2 = _ScenarioManager._create(scenario_config, creation_date=creation_date_2)
    assert scenario_2.config_id == "sc"
    assert scenario_2.pipelines == {}
    assert scenario_2.cycle.frequency == Frequency.DAILY
    assert not scenario_2.is_primary
    assert scenario_2.cycle.creation_date == creation_date_1
    assert scenario_2.cycle.start_date.date() == creation_date_2.date()
    assert scenario_2.cycle.end_date.date() == creation_date_2.date()
    assert scenario_2.properties.get("name") is None
    assert scenario_2.tags == set()

    assert scenario_1 != scenario_2
    assert scenario_1.cycle == scenario_2.cycle

    assert len(_ScenarioManager._get_all()) == 2
    with pytest.raises(DeletingPrimaryScenario):
        _ScenarioManager._delete(
            scenario_1.id,
        )

    _ScenarioManager._delete(
        scenario_2.id,
    )
    assert len(_ScenarioManager._get_all()) == 1
    _ScenarioManager._delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 0


def test_assign_scenario_as_parent_of_pipeline():
    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.SCENARIO)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.SCENARIO)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])
    pipeline_config_1 = Config.configure_pipeline("pipeline_1", [task_config_1, task_config_2])
    pipeline_config_2 = Config.configure_pipeline("pipeline_2", [task_config_1, task_config_3])

    scenario_config_1 = Config.configure_scenario("scenario_1", [pipeline_config_1])
    scenario_config_2 = Config.configure_scenario("scenario_2", [pipeline_config_1, pipeline_config_2])

    pipeline = _PipelineManager._get_or_create(pipeline_config_1, "scenario_id")

    assert pipeline.parent_ids == {"scenario_id"}
    assert all([task.parent_ids == {pipeline.id} for task in pipeline.tasks.values()])

    _PipelineManager._delete_all()

    scenario = _ScenarioManager._create(scenario_config_1)
    pipelines = scenario.pipelines.values()
    assert all([pipeline.parent_ids == {scenario.id} for pipeline in pipelines])
    for pipeline in pipelines:
        assert all([task.parent_ids == {pipeline.id} for task in pipeline.tasks.values()])

    scenario = _ScenarioManager._create(scenario_config_2)
    pipelines = scenario.pipelines
    assert all([pipeline.parent_ids == {scenario.id} for pipeline in pipelines.values()])
    tasks = {}
    for pipeline in pipelines.values():
        tasks.update(pipeline.tasks)
    assert tasks["task_1"].parent_ids == {pipelines["pipeline_1"].id, pipelines["pipeline_2"].id}
    assert tasks["task_2"].parent_ids == {pipelines["pipeline_1"].id}
    assert tasks["task_3"].parent_ids == {pipelines["pipeline_2"].id}

    _ScenarioManager._hard_delete(scenario.id)

    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.GLOBAL)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.GLOBAL)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.GLOBAL)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])
    pipeline_config_1 = Config.configure_pipeline("pipeline_1", [task_config_1, task_config_2])
    pipeline_config_2 = Config.configure_pipeline("pipeline_2", [task_config_1, task_config_3])

    scenario_config_1 = Config.configure_scenario("scenario_1", [pipeline_config_1])
    scenario_config_2 = Config.configure_scenario("scenario_2", [pipeline_config_1, pipeline_config_2])

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    assert scenario_1.pipelines["pipeline_1"].parent_ids == {scenario_1.id}
    tasks = {}
    for pipeline in scenario_1.pipelines.values():
        tasks.update(pipeline.tasks)
    assert tasks["task_1"].parent_ids == {scenario_1.pipelines["pipeline_1"].id}
    assert tasks["task_2"].parent_ids == {scenario_1.pipelines["pipeline_1"].id}

    scenario_2 = _ScenarioManager._create(scenario_config_2)
    assert scenario_1.pipelines["pipeline_1"].parent_ids == {scenario_1.id, scenario_2.id}
    assert scenario_2.pipelines["pipeline_1"].parent_ids == {scenario_1.id, scenario_2.id}
    assert scenario_2.pipelines["pipeline_2"].parent_ids == {scenario_2.id}

    tasks = {}
    for pipeline in scenario_2.pipelines.values():
        tasks.update(pipeline.tasks)

    assert tasks["task_1"].parent_ids == {scenario_2.pipelines["pipeline_1"].id, scenario_2.pipelines["pipeline_2"].id}
    assert tasks["task_2"].parent_ids == {scenario_2.pipelines["pipeline_1"].id}
    assert tasks["task_3"].parent_ids == {scenario_2.pipelines["pipeline_2"].id}


def mult_by_2(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def mult_by_4(nb: int):
    return nb * 4


def test_scenario_manager_only_creates_data_node_once():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_4 = Config.configure_data_node("qux", "in_memory", Scope.PIPELINE, default_data=0)

    task_mult_by_2_config = Config.configure_task("mult_by_2", mult_by_2, [dn_config_1], dn_config_2)
    task_mult_by_3_config = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    task_mult_by_4_config = Config.configure_task("mult_by_4", mult_by_4, [dn_config_1], dn_config_4)
    pipeline_config_1 = Config.configure_pipeline("by_6", [task_mult_by_2_config, task_mult_by_3_config])
    # dn_1 ---> mult_by_2 ---> dn_2 ---> mult_by_3 ---> dn_6
    pipeline_config_2 = Config.configure_pipeline("by_4", [task_mult_by_4_config])
    # dn_1 ---> mult_by_4 ---> dn_4
    scenario_config = Config.configure_scenario(
        "awesome_scenario", [pipeline_config_1, pipeline_config_2], Frequency.DAILY
    )

    _SchedulerFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_CycleManager._get_all()) == 0

    scenario = _ScenarioManager._create(scenario_config)

    assert len(_DataManager._get_all()) == 5
    assert len(_TaskManager._get_all()) == 3
    assert len(_PipelineManager._get_all()) == 2
    assert len(_ScenarioManager._get_all()) == 1
    assert scenario.foo.read() == 1
    assert scenario.bar.read() == 0
    assert scenario.baz.read() == 0
    assert scenario.qux.read() == 0
    assert scenario.by_6._get_sorted_tasks()[0][0].config_id == task_mult_by_2_config.id
    assert scenario.by_6._get_sorted_tasks()[1][0].config_id == task_mult_by_3_config.id
    assert scenario.by_4._get_sorted_tasks()[0][0].config_id == task_mult_by_4_config.id
    assert scenario.cycle.frequency == Frequency.DAILY


def test_notification_subscribe(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)

    notify_1 = NotifyMock(scenario)
    notify_2 = NotifyMock(scenario)
    mocker.patch.object(_utils, "_load_fct", side_effect=[notify_1, notify_2])

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._submit(scenario)
    notify_1.assert_called_3_times()

    notify_1.reset()

    # test unsubscribing notification
    # test notis subscribe only on new jobs
    # _ScenarioManager._get(scenario)
    _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_2, scenario=scenario)
    _ScenarioManager._submit(scenario)

    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


class Notify:
    def __call__(self, *args, **kwargs):
        self.args = args

    def assert_called_with(self, args):
        assert args in self.args


def test_notification_subscribe_multiple_params(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )
    notify = mocker.Mock()

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._subscribe(callback=notify, params=["foobar", 123, 1.2], scenario=scenario)
    mocker.patch.object(_ScenarioManager, "_get", return_value=scenario)

    _ScenarioManager._submit(scenario)

    notify.assert_called_with("foobar", 123, 1.2, scenario, ANY)


def notify_multi_param(param, *args):
    assert len(param) == 3


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def test_notification_unsubscribe(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)

    notify_1 = notify1
    notify_2 = notify2

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_2, scenario=scenario)
    _ScenarioManager._submit(scenario.id)

    with pytest.raises(ValueError):
        _ScenarioManager._unsubscribe(callback=notify_1, scenario=scenario)
    _ScenarioManager._unsubscribe(callback=notify_2, scenario=scenario)


def test_notification_unsubscribe_multi_param():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)

    # test subscribing notification
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 0], scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 1], scenario=scenario)
    _ScenarioManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 2], scenario=scenario)

    assert len(scenario.subscribers) == 3

    # if no params are passed, removes the first occurrence of the subscriber when theres more than one copy
    scenario.unsubscribe(notify_multi_param)
    assert len(scenario.subscribers) == 2
    assert _Subscriber(notify_multi_param, ["foobar", 123, 0]) not in scenario.subscribers

    # If params are passed, find the corresponding pair of callback and params to remove
    scenario.unsubscribe(notify_multi_param, ["foobar", 123, 2])
    assert len(scenario.subscribers) == 1
    assert _Subscriber(notify_multi_param, ["foobar", 123, 2]) not in scenario.subscribers

    # If params are passed but is not on the list of subscribers, throws a ValueErrors
    with pytest.raises(ValueError):
        scenario.unsubscribe(notify_multi_param, ["foobar", 123, 10000])


def test_scenario_notification_subscribe_all():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    scenario_config = Config.configure_scenario(
        "awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
    )

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    scenario_config.id = "other_scenario"

    other_scenario = _ScenarioManager._create(scenario_config)

    notify_1 = NotifyMock(scenario)

    _ScenarioManager._subscribe(notify_1)

    assert len(_ScenarioManager._get(scenario.id).subscribers) == 1
    assert len(_ScenarioManager._get(other_scenario.id).subscribers) == 1


def test_get_set_primary_scenario():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    cycle_1 = _CycleManager._create(Frequency.DAILY, name="foo")

    scenario_1 = Scenario("sc_1", [], {}, ScenarioId("sc_1"), is_primary=False, cycle=cycle_1)
    scenario_2 = Scenario("sc_2", [], {}, ScenarioId("sc_2"), is_primary=False, cycle=cycle_1)

    _ScenarioManager._delete_all()
    _CycleManager._delete_all()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_CycleManager._get_all()) == 0

    _CycleManager._set(cycle_1)

    _ScenarioManager._set(scenario_1)
    _ScenarioManager._set(scenario_2)

    assert len(_ScenarioManager._get_primary_scenarios()) == 0
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2

    _ScenarioManager._set_primary(scenario_1)

    assert len(_ScenarioManager._get_primary_scenarios()) == 1
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2
    assert _ScenarioManager._get_primary(cycle_1) == scenario_1

    _ScenarioManager._set_primary(scenario_2)

    assert len(_ScenarioManager._get_primary_scenarios()) == 1
    assert len(_ScenarioManager._get_all_by_cycle(cycle_1)) == 2
    assert _ScenarioManager._get_primary(cycle_1) == scenario_2


def test_hard_delete_one_single_scenario_with_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario.id)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _ScenarioManager._hard_delete(scenario.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_single_scenario_with_pipeline_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario.id)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _ScenarioManager._hard_delete(scenario.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_single_scenario_with_one_pipeline_and_one_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario.id)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _ScenarioManager._hard_delete(scenario.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_single_scenario_with_one_pipeline_and_one_global_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario.id)

    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _ScenarioManager._hard_delete(scenario.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 0

    scenario_2 = _ScenarioManager._create(scenario_config)
    scenario_2.submit()
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1

    _ScenarioManager._hard_delete(scenario_2.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_scenario_among_two_with_one_pipeline_and_one_global_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
    assert len(_JobManager._get_all()) == 2
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_2.id) is not None


def test_hard_delete_one_scenario_among_two_with_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 2
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    assert _ScenarioManager._get(scenario_2.id) is not None


def test_hard_delete_one_scenario_among_two_with_cycle_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    scenario_config = Config.configure_scenario("scenario_config", [pipeline_config])

    _SchedulerFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)
    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 2
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 2
    assert _ScenarioManager._get(scenario_2.id) is not None


def test_hard_delete_shared_entities():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_config_1 = Config.configure_data_node("my_input_1", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_config_2 = Config.configure_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_config_3 = Config.configure_data_node("my_input_3", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    dn_config_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_config_1 = Config.configure_task("task_config_1", print, dn_config_1, dn_config_2)
    task_config_2 = Config.configure_task("task_config_2", print, dn_config_2, dn_config_3)
    task_config_3 = Config.configure_task("task_config_3", print, dn_config_3, dn_config_4)  # scope = global
    pipeline_config_1 = Config.configure_pipeline("pipeline_config_1", [task_config_1, task_config_2])
    pipeline_config_2 = Config.configure_pipeline("pipeline_config_2", [task_config_1, task_config_2])
    pipeline_config_3 = Config.configure_pipeline("pipeline_config_3", [task_config_3])  # scope = global
    scenario_config_1 = Config.configure_scenario(
        "scenario_config_1", [pipeline_config_1, pipeline_config_2, pipeline_config_3]
    )

    _SchedulerFactory._build_dispatcher()

    scenario_1 = _ScenarioManager._create(scenario_config_1)
    scenario_2 = _ScenarioManager._create(scenario_config_1)
    scenario_1.submit()
    scenario_2.submit()

    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 5
    assert len(_TaskManager._get_all()) == 7
    assert len(_DataManager._get_all()) == 8
    assert len(_JobManager._get_all()) == 10
    _ScenarioManager._hard_delete(scenario_1.id)
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 4
    assert len(_DataManager._get_all()) == 5
    assert len(_JobManager._get_all()) == 6


def test_submit():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

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

    class MockScheduler(_Scheduler):
        submit_calls = []

        @classmethod
        def _submit_task(cls, task: Task, submit_id: str, callbacks=None, force=False, wait=False, timeout=None):
            cls.submit_calls.append(task.id)
            return super()._submit_task(task, submit_id, callbacks, force)

    _TaskManager._scheduler = MockScheduler

    with pytest.raises(NonExistingScenario):
        _ScenarioManager._submit(scenario.id)
    with pytest.raises(NonExistingScenario):
        _ScenarioManager._submit(scenario)

    # scenario does exist, but pipeline does not exist.
    # We expect an exception to be raised
    _ScenarioManager._set(scenario)
    with pytest.raises(NonExistingPipeline):
        _ScenarioManager._submit(scenario.id)
    with pytest.raises(NonExistingPipeline):
        _ScenarioManager._submit(scenario)

    # scenario and pipeline do exist, but tasks does not exist.
    # We expect an exception to be raised
    _PipelineManager._set(pipeline_1)
    _PipelineManager._set(pipeline_2)
    with pytest.raises(NonExistingTask):
        _ScenarioManager._submit(scenario.id)
    with pytest.raises(NonExistingTask):
        _ScenarioManager._submit(scenario)

    # scenario, pipeline, and tasks do exist.
    # We expect all the tasks to be submitted once,
    # and respecting specific constraints on the order
    _TaskManager._set(task_1)
    _TaskManager._set(task_2)
    _TaskManager._set(task_3)
    _TaskManager._set(task_4)
    _TaskManager._set(task_5)
    _ScenarioManager._submit(scenario.id)
    submit_calls = _TaskManager._scheduler().submit_calls
    assert len(submit_calls) == 5
    assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
    assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)

    _ScenarioManager._submit(scenario)
    submit_calls = _TaskManager._scheduler().submit_calls
    assert len(submit_calls) == 10
    assert set(submit_calls) == {task_1.id, task_2.id, task_4.id, task_3.id, task_5.id}
    assert submit_calls.index(task_2.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_3.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_2.id)
    assert submit_calls.index(task_1.id) < submit_calls.index(task_4.id)

    _TaskManager._scheduler = _SchedulerFactory._build_scheduler


def subtraction(n1, n2):
    return n1 - n2


def addition(n1, n2):
    return n1 + n2


def test_scenarios_comparison_development_mode():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    scenario_config = Config.configure_scenario(
        "Awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
        comparators={"bar": [subtraction], "foo": [subtraction, addition]},
    )

    _SchedulerFactory._build_dispatcher()

    assert scenario_config.comparators is not None
    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)

    with pytest.raises(InsufficientScenarioToCompare):
        _ScenarioManager._compare(scenario_1, data_node_config_id="bar")

    scenario_3 = Scenario("awesome_scenario_config", [], {})
    with pytest.raises(DifferentScenarioConfigs):
        _ScenarioManager._compare(scenario_1, scenario_3, data_node_config_id="bar")

    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    bar_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="bar")["bar"]
    assert bar_comparison["subtraction"] == 0

    foo_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="foo")["foo"]
    assert len(foo_comparison.keys()) == 2
    assert foo_comparison["addition"] == 2
    assert foo_comparison["subtraction"] == 0

    assert len(_ScenarioManager._compare(scenario_1, scenario_2).keys()) == 2

    with pytest.raises(NonExistingScenarioConfig):
        _ScenarioManager._compare(scenario_3, scenario_3)

    with pytest.raises(NonExistingComparator):
        _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="abc")


def test_scenarios_comparison_standalone_mode():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)

    scenario_config = Config.configure_scenario(
        "Awesome_scenario",
        [
            Config.configure_pipeline(
                "by_6",
                [
                    Config.configure_task(
                        "mult_by_2",
                        mult_by_2,
                        [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                        Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
                    )
                ],
            )
        ],
        comparators={"bar": [subtraction], "foo": [subtraction, addition]},
    )

    _SchedulerFactory._build_dispatcher()

    assert scenario_config.comparators is not None
    scenario_1 = _ScenarioManager._create(scenario_config)
    scenario_2 = _ScenarioManager._create(scenario_config)

    with pytest.raises(InsufficientScenarioToCompare):
        _ScenarioManager._compare(scenario_1, data_node_config_id="bar")

    scenario_3 = Scenario("awesome_scenario_config", [], {})
    with pytest.raises(DifferentScenarioConfigs):
        _ScenarioManager._compare(scenario_1, scenario_3, data_node_config_id="bar")

    _ScenarioManager._submit(scenario_1.id)
    _ScenarioManager._submit(scenario_2.id)

    bar_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="bar")["bar"]
    assert_true_after_1_minute_max(lambda: bar_comparison["subtraction"] == 0)

    foo_comparison = _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="foo")["foo"]
    assert_true_after_1_minute_max(lambda: len(foo_comparison.keys()) == 2)
    assert_true_after_1_minute_max(lambda: foo_comparison["addition"] == 2)
    assert_true_after_1_minute_max(lambda: foo_comparison["subtraction"] == 0)

    assert_true_after_1_minute_max(lambda: len(_ScenarioManager._compare(scenario_1, scenario_2).keys()) == 2)

    with pytest.raises(NonExistingScenarioConfig):
        _ScenarioManager._compare(scenario_3, scenario_3)

    with pytest.raises(NonExistingComparator):
        _ScenarioManager._compare(scenario_1, scenario_2, data_node_config_id="abc")


def test_tags():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    cycle_1 = _CycleManager._create(Frequency.DAILY, name="today", creation_date=datetime.now())
    cycle_2 = _CycleManager._create(
        Frequency.DAILY,
        name="tomorrow",
        creation_date=datetime.now() + timedelta(days=1),
    )
    cycle_3 = _CycleManager._create(
        Frequency.DAILY,
        name="yesterday",
        creation_date=datetime.now() + timedelta(days=-1),
    )

    scenario_no_tag = Scenario("SCENARIO_no_tag", [], {}, ScenarioId("SCENARIO_no_tag"), cycle=cycle_1)
    scenario_1_tag = Scenario(
        "SCENARIO_1_tag",
        [],
        {},
        ScenarioId("SCENARIO_1_tag"),
        cycle=cycle_1,
        tags={"fst"},
    )
    scenario_2_tags = Scenario(
        "SCENARIO_2_tags",
        [],
        {},
        ScenarioId("SCENARIO_2_tags"),
        cycle=cycle_2,
        tags={"fst", "scd"},
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
    _CycleManager._set(cycle_1)
    _CycleManager._set(cycle_2)
    _CycleManager._set(cycle_3)
    _ScenarioManager._set(scenario_no_tag)
    _ScenarioManager._set(scenario_1_tag)
    _ScenarioManager._set(scenario_2_tags)

    assert len(_ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).tags) == 0
    assert not _ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).has_tag("fst")
    assert not _ScenarioManager._get(ScenarioId("SCENARIO_no_tag")).has_tag("scd")

    assert len(_ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags) == 1
    assert "fst" in _ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags
    assert "scd" not in _ScenarioManager._get(ScenarioId("SCENARIO_1_tag")).tags

    assert len(_ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags) == 2
    assert "fst" in _ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags
    assert "scd" in _ScenarioManager._get(ScenarioId("SCENARIO_2_tags")).tags

    # Test tag & untag

    _ScenarioManager._tag(scenario_no_tag, "thd")  # add new tag
    _ScenarioManager._untag(scenario_1_tag, "NOT_EXISTING_TAG")  # remove not existing tag does nothing
    _ScenarioManager._untag(scenario_1_tag, "fst")  # remove `fst` tag

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

    _ScenarioManager._untag(scenario_no_tag, "thd")
    _ScenarioManager._set(scenario_no_tag)
    _ScenarioManager._tag(scenario_1_tag, "fst")
    _ScenarioManager._set(scenario_1_tag)

    # test getters
    assert not _ScenarioManager._get_by_tag(cycle_3, "fst")
    assert not _ScenarioManager._get_by_tag(cycle_3, "scd")
    assert not _ScenarioManager._get_by_tag(cycle_3, "thd")

    assert _ScenarioManager._get_by_tag(cycle_2, "fst") == scenario_2_tags
    assert _ScenarioManager._get_by_tag(cycle_2, "scd") == scenario_2_tags
    assert not _ScenarioManager._get_by_tag(cycle_2, "thd")

    assert _ScenarioManager._get_by_tag(cycle_1, "fst") == scenario_1_tag
    assert not _ScenarioManager._get_by_tag(cycle_1, "scd")
    assert not _ScenarioManager._get_by_tag(cycle_1, "thd")

    assert len(_ScenarioManager._get_all_by_tag("NOT_EXISTING")) == 0
    assert scenario_1_tag in _ScenarioManager._get_all_by_tag("fst")
    assert scenario_2_tags in _ScenarioManager._get_all_by_tag("fst")
    assert _ScenarioManager._get_all_by_tag("scd") == [scenario_2_tags]
    assert len(_ScenarioManager._get_all_by_tag("thd")) == 0

    # test tag cycle mgt

    _ScenarioManager._tag(
        scenario_no_tag, "fst"
    )  # tag sc_no_tag should untag sc_1_tag with same cycle but not sc_2_tags

    assert not _ScenarioManager._get_by_tag(cycle_3, "fst")
    assert not _ScenarioManager._get_by_tag(cycle_3, "scd")
    assert not _ScenarioManager._get_by_tag(cycle_3, "thd")

    assert _ScenarioManager._get_by_tag(cycle_2, "fst") == scenario_2_tags
    assert _ScenarioManager._get_by_tag(cycle_2, "scd") == scenario_2_tags
    assert not _ScenarioManager._get_by_tag(cycle_2, "thd")

    assert _ScenarioManager._get_by_tag(cycle_1, "fst") == scenario_no_tag
    assert not _ScenarioManager._get_by_tag(cycle_1, "scd")
    assert not _ScenarioManager._get_by_tag(cycle_1, "thd")

    assert len(_ScenarioManager._get_all_by_tag("NOT_EXISTING")) == 0
    assert len(_ScenarioManager._get_all_by_tag("fst")) == 2
    assert scenario_2_tags in _ScenarioManager._get_all_by_tag("fst")
    assert scenario_no_tag in _ScenarioManager._get_all_by_tag("fst")
    assert _ScenarioManager._get_all_by_tag("scd") == [scenario_2_tags]
    assert len(_ScenarioManager._get_all_by_tag("thd")) == 0


def test_authorized_tags():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    scenario = Scenario("SCENARIO_1", [], {"authorized_tags": ["foo", "bar"]}, ScenarioId("SCENARIO_1"))
    scenario_2_cfg = Config.configure_scenario("SCENARIO_2", [], Frequency.DAILY, authorized_tags=["foo", "bar"])

    _SchedulerFactory._build_dispatcher()

    scenario_2 = _ScenarioManager._create(scenario_2_cfg)
    _ScenarioManager._set(scenario)

    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    with pytest.raises(UnauthorizedTagError):
        _ScenarioManager._tag(scenario, "baz")
        _ScenarioManager._tag(scenario_2, "baz")
    assert len(scenario.tags) == 0
    assert len(scenario_2.tags) == 0

    _ScenarioManager._tag(scenario, "foo")
    _ScenarioManager._tag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1

    _ScenarioManager._tag(scenario, "bar")
    _ScenarioManager._tag(scenario_2, "bar")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    _ScenarioManager._tag(scenario, "foo")
    _ScenarioManager._tag(scenario_2, "foo")
    assert len(scenario.tags) == 2
    assert len(scenario_2.tags) == 2

    _ScenarioManager._untag(scenario, "foo")
    _ScenarioManager._untag(scenario_2, "foo")
    assert len(scenario.tags) == 1
    assert len(scenario_2.tags) == 1


def test_scenario_create_from_task_config():
    data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
    data_node_2_config = Config.configure_data_node(
        id="d2", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    data_node_3_config = Config.configure_data_node(
        id="d3", storage_type="in_memory", default_data="abc", scope=Scope.SCENARIO
    )
    task_config_1 = Config.configure_task("t1", print, data_node_1_config, data_node_2_config, scope=Scope.GLOBAL)
    task_config_2 = Config.configure_task("t2", print, data_node_2_config, data_node_3_config, scope=Scope.GLOBAL)
    scenario_config_1 = Config.configure_scenario_from_tasks("s1", task_configs=[task_config_1, task_config_2])

    pipeline_name = "p1"
    scenario_config_2 = Config.configure_scenario_from_tasks(
        "s2", task_configs=[task_config_1, task_config_2], pipeline_id=pipeline_name
    )

    _ScenarioManager._submit(_ScenarioManager._create(scenario_config_1))
    assert len(_ScenarioManager._get_all()) == 1
    assert len(_PipelineManager._get_all()) == 1
    assert len(scenario_config_1.pipeline_configs) == 1
    assert len(scenario_config_1.pipeline_configs[0].task_configs) == 2
    # Should create a default pipeline name
    assert isinstance(scenario_config_1.pipeline_configs[0].id, str)
    assert scenario_config_1.pipeline_configs[0].id == f"{scenario_config_1.id}_pipeline"

    _ScenarioManager._submit(_ScenarioManager._create(scenario_config_2))
    assert len(_ScenarioManager._get_all()) == 2
    assert len(_PipelineManager._get_all()) == 2
    assert scenario_config_2.pipeline_configs[0].id == pipeline_name
