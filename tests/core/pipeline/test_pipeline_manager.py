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

from unittest import mock
from unittest.mock import ANY

import pytest

from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.common import _utils
from src.taipy.core.common._utils import Subscriber
from src.taipy.core.common.alias import PipelineId, TaskId
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import NonExistingPipeline, NonExistingTask
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from taipy.config import JobConfig
from taipy.config.config import Config
from taipy.config.data_node.scope import Scope
from tests.core.utils.NotifyMock import NotifyMock


def test_set_and_get_pipeline():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline("name_1", {}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    output_2 = InMemoryDataNode("foo", Scope.PIPELINE)
    task_2 = Task("task", print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline("name_2", {}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = Pipeline("name_3", {}, [], pipeline_id_1)

    # No existing Pipeline
    assert _PipelineManager._get(pipeline_id_1) is None
    assert _PipelineManager._get(pipeline_1) is None
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save one pipeline. We expect to have only one pipeline stored
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    _TaskManager._set(task_2)
    _PipelineManager._set(pipeline_2)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save the first pipeline again. We expect nothing to change
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_1.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    _PipelineManager._set(pipeline_3_with_same_id)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).config_id == pipeline_3_with_same_id.config_id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_1).config_id == pipeline_3_with_same_id.config_id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_id_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert _PipelineManager._get(pipeline_2).config_id == pipeline_2.config_id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


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

    class MockScheduler(_Scheduler):
        submit_calls = []

        @classmethod
        def _submit_task(cls, task: Task, submit_id: str, callbacks=None, force=False, wait=False, timeout=None):
            cls.submit_calls.append(task)
            return None

    _TaskManager._scheduler = MockScheduler

    # pipeline does not exists. We expect an exception to be raised
    with pytest.raises(NonExistingPipeline):
        _PipelineManager._submit(pipeline.id)
    with pytest.raises(NonExistingPipeline):
        _PipelineManager._submit(pipeline)

    # pipeline does exist, but tasks does not exist. We expect an exception to be raised
    _PipelineManager._set(pipeline)
    with pytest.raises(NonExistingTask):
        _PipelineManager._submit(pipeline.id)
    with pytest.raises(NonExistingTask):
        _PipelineManager._submit(pipeline)

    # pipeline, and tasks does exist. We expect the tasks to be submitted
    # in a specific order
    _TaskManager._set(task_1)
    _TaskManager._set(task_2)
    _TaskManager._set(task_3)
    _TaskManager._set(task_4)

    _PipelineManager._submit(pipeline.id)
    calls_ids = [t.id for t in _TaskManager._scheduler().submit_calls]
    tasks_ids = [task_1.id, task_2.id, task_4.id, task_3.id]
    assert calls_ids == tasks_ids

    _PipelineManager._submit(pipeline)
    calls_ids = [t.id for t in _TaskManager._scheduler().submit_calls]
    tasks_ids = tasks_ids * 2
    assert set(calls_ids) == set(tasks_ids)
    _TaskManager._scheduler = _SchedulerFactory._build_scheduler


g = 0


def mock_function_no_input_no_output():
    global g
    g += 1


def mock_function_one_input_no_output(inp):
    global g
    g += inp


def mock_function_no_input_one_output():
    global g
    return g


def test_submit_scenario_from_tasks_with_one_or_no_input_output():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    # test no input and no output Task
    task_no_input_no_output = Task("task_no_input_no_output", mock_function_no_input_no_output)
    pipeline_1 = Pipeline("my_pipeline", {}, [task_no_input_no_output])

    _TaskManager._set(task_no_input_no_output)
    _PipelineManager._set(pipeline_1)
    assert len(pipeline_1._get_sorted_tasks()) == 1

    _PipelineManager._submit(pipeline_1)
    assert g == 1

    # test one input and no output Task
    data_node_input = InMemoryDataNode("input_dn", Scope.PIPELINE, properties={"default_data": 2})
    task_one_input_no_output = Task(
        "task_one_input_no_output", mock_function_one_input_no_output, input=[data_node_input]
    )
    pipeline_2 = Pipeline("my_pipeline_2", {}, [task_one_input_no_output])

    _DataManager._set(data_node_input)
    data_node_input.unlock_edition()

    _TaskManager._set(task_one_input_no_output)
    _PipelineManager._set(pipeline_2)
    assert len(pipeline_2._get_sorted_tasks()) == 1

    _PipelineManager._submit(pipeline_2)
    assert g == 3

    # test no input and one output Task
    data_node_output = InMemoryDataNode("output_dn", Scope.PIPELINE, properties={"default_data": None})
    task_no_input_one_output = Task(
        "task_no_input_one_output", mock_function_no_input_one_output, output=[data_node_output]
    )
    pipeline_3 = Pipeline("my_pipeline_3", {}, [task_no_input_one_output])

    _DataManager._set(data_node_output)
    assert data_node_output.read() is None

    _TaskManager._set(task_no_input_one_output)
    _PipelineManager._set(pipeline_3)
    assert len(pipeline_2._get_sorted_tasks()) == 1

    _PipelineManager._submit(pipeline_3)
    assert data_node_output.read() == 3


def mult_by_two(nb: int):
    return nb * 2


def mult_by_3(nb: int):
    return nb * 3


def test_get_or_create_data():
    # only create intermediate data node once
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.configure_pipeline("by_6", [task_config_mult_by_two, task_config_mult_by_3])
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0

    pipeline = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 3
    assert len(_TaskManager._get_all()) == 2
    assert len(pipeline._get_sorted_tasks()) == 2
    assert pipeline.foo.read() == 1
    assert pipeline.bar.read() == 0
    assert pipeline.baz.read() == 0
    assert pipeline._get_sorted_tasks()[0][0].config_id == task_config_mult_by_two.id
    assert pipeline._get_sorted_tasks()[1][0].config_id == task_config_mult_by_3.id

    _PipelineManager._submit(pipeline.id)
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
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.PIPELINE, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    pipeline_config = Config.configure_pipeline("by_6", [task_config_mult_by_two, task_config_mult_by_3], foo="bar")

    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"

    pipeline = _PipelineManager._get_or_create(pipeline_config, None)
    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"
    assert len(pipeline.properties) == 1
    assert pipeline.properties.get("foo") == "bar"

    pipeline.properties["baz"] = "qux"
    _PipelineManager._set(pipeline)
    assert len(pipeline_config.properties) == 1
    assert pipeline_config.properties.get("foo") == "bar"
    assert len(pipeline.properties) == 2
    assert pipeline.properties.get("foo") == "bar"
    assert pipeline.properties.get("baz") == "qux"


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def notify_multi_param(*args, **kwargs):
    ...


def test_pipeline_notification_subscribe(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    pipeline_config = Config.configure_pipeline(
        "by_6",
        [
            Config.configure_task(
                "mult_by_two",
                mult_by_two,
                [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = _PipelineManager._get_or_create(pipeline_config)

    notify_1 = NotifyMock(pipeline)
    notify_1.__name__ = "notify_1"
    notify_1.__module__ = "notify_1"
    notify_2 = NotifyMock(pipeline)
    notify_2.__name__ = "notify_2"
    notify_2.__module__ = "notify_2"
    # Mocking this because NotifyMock is a class that does not loads correctly when getting the pipeline
    # from the storage.
    mocker.patch.object(_utils, "_load_fct", side_effect=[notify_1, notify_2])

    # test subscription
    callback = mock.MagicMock()
    _PipelineManager._submit(pipeline.id, [callback])
    callback.assert_called()

    # test pipeline subscribe notification
    _PipelineManager._subscribe(callback=notify_1, pipeline=pipeline)
    _PipelineManager._submit(pipeline.id)

    notify_1.assert_called_3_times()

    notify_1.reset()

    # test pipeline unsubscribe notification
    # test subscribe notification only on new job
    _PipelineManager._unsubscribe(callback=notify_1, pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_2, pipeline=pipeline)
    _PipelineManager._submit(pipeline.id)

    notify_1.assert_not_called()
    notify_2.assert_called_3_times()


def test_pipeline_notification_subscribe_multi_param(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    pipeline_config = Config.configure_pipeline(
        "by_6",
        [
            Config.configure_task(
                "mult_by_two",
                mult_by_two,
                [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = _PipelineManager._get_or_create(pipeline_config)
    notify = mocker.Mock()

    # test pipeline subscribe notification
    _PipelineManager._subscribe(callback=notify, params=["foobar", 123, 1.2], pipeline=pipeline)
    mocker.patch.object(_PipelineManager, "_get", return_value=pipeline)

    _PipelineManager._submit(pipeline.id)

    # as the callback is called with Pipeline/Scenario and Job objects
    # we can assert that is called with params plus a pipeline object that we know
    # of and a job object that is represented by ANY in this case
    notify.assert_called_with("foobar", 123, 1.2, pipeline, ANY)


def test_pipeline_notification_unsubscribe(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    mocker.patch("src.taipy.core.common._reload._reload", side_effect=lambda m, o: o)

    pipeline_config = Config.configure_pipeline(
        "by_6",
        [
            Config.configure_task(
                "mult_by_two",
                mult_by_two,
                [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = _PipelineManager._get_or_create(pipeline_config)

    notify_1 = notify1
    notify_2 = notify2

    _PipelineManager._subscribe(callback=notify_1, pipeline=pipeline)
    _PipelineManager._unsubscribe(callback=notify_1, pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_2, pipeline=pipeline)
    _PipelineManager._submit(pipeline.id)

    with pytest.raises(ValueError):
        _PipelineManager._unsubscribe(callback=notify_1, pipeline=pipeline)
        _PipelineManager._unsubscribe(callback=notify_2, pipeline=pipeline)


def test_pipeline_notification_unsubscribe_multi_param():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    pipeline_config = Config.configure_pipeline(
        "by_6",
        [
            Config.configure_task(
                "mult_by_two",
                mult_by_two,
                [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = _PipelineManager._get_or_create(pipeline_config)

    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 0], pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 1], pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 2], pipeline=pipeline)

    assert len(pipeline.subscribers) == 3

    pipeline.unsubscribe(notify_multi_param)
    assert len(pipeline.subscribers) == 2
    assert Subscriber(notify_multi_param, ["foobar", 123, 0]) not in pipeline.subscribers

    pipeline.unsubscribe(notify_multi_param, ["foobar", 123, 2])
    assert len(pipeline.subscribers) == 1
    assert Subscriber(notify_multi_param, ["foobar", 123, 2]) not in pipeline.subscribers

    with pytest.raises(ValueError):
        pipeline.unsubscribe(notify_multi_param, ["foobar", 123, 10000])


def test_pipeline_notification_subscribe_all():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    pipeline_config = Config.configure_pipeline(
        "by_6",
        [
            Config.configure_task(
                "mult_by_two",
                mult_by_two,
                [Config.configure_data_node("foo", "in_memory", Scope.PIPELINE, default_data=1)],
                Config.configure_data_node("bar", "in_memory", Scope.PIPELINE, default_data=0),
            )
        ],
    )

    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline_config.id = "other_pipeline"

    other_pipeline = _PipelineManager._get_or_create(pipeline_config)

    notify_1 = NotifyMock(pipeline)

    _PipelineManager._subscribe(notify_1)

    assert len(_PipelineManager._get(pipeline.id).subscribers) == 1
    assert len(_PipelineManager._get(other_pipeline.id).subscribers) == 1


def test_do_not_recreate_existing_pipeline_except_same_config():
    dn_input_config_scope_scenario = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_scenario = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task(
        "task_config", print, dn_input_config_scope_scenario, dn_output_config_scope_scenario
    )
    pipeline_config = Config.configure_pipeline("pipeline_config_1", [task_config])

    # Scope is scenario
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    assert len(_PipelineManager._get_all()) == 1
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
    assert len(_PipelineManager._get_all()) == 1
    assert pipeline_1.id == pipeline_2.id
    pipeline_3 = _PipelineManager._get_or_create(pipeline_config, "a_scenario")  # Create even if the config is the same
    assert len(_PipelineManager._get_all()) == 2
    assert pipeline_1.id == pipeline_2.id
    assert pipeline_3.id != pipeline_1.id
    assert pipeline_3.id != pipeline_2.id
    pipeline_4 = _PipelineManager._get_or_create(
        pipeline_config, "a_scenario"
    )  # Do not create because existed pipeline
    assert len(_PipelineManager._get_all()) == 2
    assert pipeline_3.id == pipeline_4.id

    dn_input_config_scope_scenario_2 = Config.configure_data_node("my_input_2", "in_memory", scope=Scope.SCENARIO)
    dn_output_config_scope_global_2 = Config.configure_data_node("my_output_2", "in_memory", scope=Scope.GLOBAL)
    task_config_2 = Config.configure_task(
        "task_config_2", print, dn_input_config_scope_scenario_2, dn_output_config_scope_global_2
    )
    pipeline_config_2 = Config.configure_pipeline("pipeline_config_2", [task_config_2])

    # Scope is scenario and global
    pipeline_5 = _PipelineManager._get_or_create(pipeline_config_2)
    assert len(_PipelineManager._get_all()) == 3
    pipeline_6 = _PipelineManager._get_or_create(pipeline_config_2)
    assert len(_PipelineManager._get_all()) == 3
    assert pipeline_5.id == pipeline_6.id
    pipeline_7 = _PipelineManager._get_or_create(pipeline_config_2, "another_scenario")
    assert len(_PipelineManager._get_all()) == 4
    assert pipeline_7.id != pipeline_6.id
    assert pipeline_7.id != pipeline_5.id
    pipeline_8 = _PipelineManager._get_or_create(pipeline_config_2, "another_scenario")
    assert len(_PipelineManager._get_all()) == 4
    assert pipeline_7.id == pipeline_8.id

    dn_input_config_scope_global_3 = Config.configure_data_node("my_input_3", "in_memory", scope=Scope.GLOBAL)
    dn_output_config_scope_global_3 = Config.configure_data_node("my_output_3", "in_memory", scope=Scope.GLOBAL)
    task_config_3 = Config.configure_task(
        "task_config_3", print, dn_input_config_scope_global_3, dn_output_config_scope_global_3
    )
    pipeline_config_3 = Config.configure_pipeline("pipeline_config_3", [task_config_3])

    # Scope is global
    pipeline_9 = _PipelineManager._get_or_create(pipeline_config_3)
    assert len(_PipelineManager._get_all()) == 5
    pipeline_10 = _PipelineManager._get_or_create(pipeline_config_3)
    assert len(_PipelineManager._get_all()) == 5
    assert pipeline_9.id == pipeline_10.id
    pipeline_11 = _PipelineManager._get_or_create(
        pipeline_config_3, "another_new_scenario"
    )  # Do not create because scope is global
    assert len(_PipelineManager._get_all()) == 5
    assert pipeline_11.id == pipeline_10.id
    assert pipeline_11.id == pipeline_9.id

    dn_input_config_scope_pipeline_4 = Config.configure_data_node("my_input_4", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_global_4 = Config.configure_data_node("my_output_4", "in_memory", scope=Scope.GLOBAL)
    task_config_4 = Config.configure_task(
        "task_config_4", print, dn_input_config_scope_pipeline_4, dn_output_config_scope_global_4
    )
    pipeline_config_4 = Config.configure_pipeline("pipeline_config_4", [task_config_4])

    # Scope is global and pipeline
    pipeline_12 = _PipelineManager._get_or_create(pipeline_config_4)
    assert len(_PipelineManager._get_all()) == 6
    pipeline_13 = _PipelineManager._get_or_create(pipeline_config_4)  # Create a new pipeline because new pipeline ID
    assert len(_PipelineManager._get_all()) == 7
    assert pipeline_12.id != pipeline_13.id
    pipeline_14 = _PipelineManager._get_or_create(pipeline_config_4, "another_new_scenario_2")
    assert len(_PipelineManager._get_all()) == 8
    assert pipeline_14.id != pipeline_12.id
    assert pipeline_14.id != pipeline_13.id
    pipeline_15 = _PipelineManager._get_or_create(
        pipeline_config_4, "another_new_scenario_2"
    )  # Don't create because scope is pipeline
    assert len(_PipelineManager._get_all()) == 9
    assert pipeline_15.id != pipeline_14.id
    assert pipeline_15.id != pipeline_13.id
    assert pipeline_15.id != pipeline_12.id

    dn_input_config_scope_pipeline_5 = Config.configure_data_node("my_input_5", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_scenario_5 = Config.configure_data_node("my_output_5", "in_memory", scope=Scope.SCENARIO)
    task_config_5 = Config.configure_task(
        "task_config_5", print, dn_input_config_scope_pipeline_5, dn_output_config_scope_scenario_5
    )
    pipeline_config_5 = Config.configure_pipeline("pipeline_config_5", [task_config_5])

    # Scope is scenario and pipeline
    pipeline_16 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 10
    pipeline_17 = _PipelineManager._get_or_create(pipeline_config_5)
    assert len(_PipelineManager._get_all()) == 11
    assert pipeline_16.id != pipeline_17.id
    pipeline_18 = _PipelineManager._get_or_create(
        pipeline_config_5, "random_scenario"
    )  # Create because scope is pipeline
    assert len(_PipelineManager._get_all()) == 12
    assert pipeline_18.id != pipeline_17.id
    assert pipeline_18.id != pipeline_16.id

    # create a second pipeline from the same config
    dn_input_config_scope_pipeline_6 = Config.configure_data_node("my_input_6", "in_memory", scope=Scope.PIPELINE)
    dn_output_config_scope_pipeline_6 = Config.configure_data_node("my_output_6", "in_memory", scope=Scope.PIPELINE)
    task_config_6 = Config.configure_task(
        "task_config_6", print, dn_input_config_scope_pipeline_6, dn_output_config_scope_pipeline_6
    )
    pipeline_config_6 = Config.configure_pipeline("pipeline_config_6", [task_config_6])

    pipeline_19 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 13
    pipeline_20 = _PipelineManager._get_or_create(pipeline_config_6)
    assert len(_PipelineManager._get_all()) == 14
    assert pipeline_19.id != pipeline_20.id


def test_hard_delete_one_single_pipeline_with_pipeline_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node(
        "my_output", "in_memory", scope=Scope.PIPELINE, default_data="works !"
    )
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    pipeline = _PipelineManager._get_or_create(pipeline_config)
    _PipelineManager._submit(pipeline.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 0
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_single_pipeline_with_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_one_single_pipeline_with_cycle_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_one_single_pipeline_with_pipeline_and_global_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    pipeline = _PipelineManager._get_or_create(pipeline_config)
    pipeline.submit()

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1
    _PipelineManager._hard_delete(pipeline.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0
    assert len(_DataManager._get_all()) == 1
    assert len(_JobManager._get_all()) == 0


def test_hard_delete_one_pipeline_among_two_with_pipeline_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_config])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
    _PipelineManager._submit(pipeline_1.id)
    _PipelineManager._submit(pipeline_2.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
    assert len(_JobManager._get_all()) == 2
    _PipelineManager._hard_delete(pipeline_1.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 1
    assert len(_DataManager._get_all()) == 2
    assert len(_JobManager._get_all()) == 1


def test_hard_delete_shared_entities():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._build_dispatcher()

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)
    _PipelineManager._submit(pipeline_1.id)
    _PipelineManager._submit(pipeline_2.id)

    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 2
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4
    _PipelineManager._hard_delete(pipeline_1.id)
    assert len(_ScenarioManager._get_all()) == 0
    assert len(_PipelineManager._get_all()) == 1
    assert len(_TaskManager._get_all()) == 2
    assert len(_DataManager._get_all()) == 3
    assert len(_JobManager._get_all()) == 3


def test_data_node_creation_pipeline():
    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.PIPELINE)
    input_global_dn = Config.configure_data_node("my_global_input", "in_memory", scope=Scope.GLOBAL)
    input_global_dn_2 = Config.configure_data_node("my_global_input_2", "in_memory", scope=Scope.GLOBAL)
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.PIPELINE)
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.PIPELINE)
    task_1 = Config.configure_task("task_1", print, [input_dn, input_global_dn, input_global_dn_2], intermediate_dn)
    task_2 = Config.configure_task("task_2", print, [input_dn, intermediate_dn], output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 8
    assert pipeline_1.my_input.id != pipeline_2.my_input.id
    assert pipeline_1.my_global_input.id == pipeline_2.my_global_input.id
    assert pipeline_1.my_global_input_2.id == pipeline_2.my_global_input_2.id
    assert pipeline_1.my_inter.id != pipeline_2.my_inter.id
    assert pipeline_1.my_output.id != pipeline_2.my_output.id


def test_data_node_creation_scenario():
    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    input_global_dn = Config.configure_data_node("my_global_input", "in_memory", scope=Scope.GLOBAL)
    input_global_dn_2 = Config.configure_data_node("my_global_input_2", "in_memory", scope=Scope.GLOBAL)
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.SCENARIO)
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_1 = Config.configure_task("task_1", print, [input_dn, input_global_dn, input_global_dn_2], intermediate_dn)
    task_2 = Config.configure_task("task_2", print, [input_dn, intermediate_dn], output_dn)
    pipeline_config = Config.configure_pipeline("pipeline_config", [task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create(pipeline_config)
    pipeline_2 = _PipelineManager._get_or_create(pipeline_config)

    assert len(_DataManager._get_all()) == 5
    assert pipeline_1.my_input.id == pipeline_2.my_input.id
    assert pipeline_1.my_global_input.id == pipeline_2.my_global_input.id
    assert pipeline_1.my_global_input_2.id == pipeline_2.my_global_input_2.id
    assert pipeline_1.my_inter.id == pipeline_2.my_inter.id
    assert pipeline_1.my_output.id == pipeline_2.my_output.id
