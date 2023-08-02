# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Callable, Iterable, Optional
from unittest import mock
from unittest.mock import ANY

import pytest

from src.taipy.core._orchestrator._orchestrator import _Orchestrator
from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.common import _utils
from src.taipy.core.common._utils import _Subscriber
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.in_memory import InMemoryDataNode
from src.taipy.core.exceptions.exceptions import NonExistingPipeline, NonExistingTask
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline
from src.taipy.core.pipeline.pipeline_id import PipelineId
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.task._task_manager import _TaskManager
from src.taipy.core.task.task import Task
from src.taipy.core.task.task_id import TaskId
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from tests.core.utils.NotifyMock import NotifyMock


def test_set_and_get_pipeline():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    pipeline_id_1 = PipelineId("id1")
    pipeline_1 = Pipeline({}, [], pipeline_id_1)

    pipeline_id_2 = PipelineId("id2")
    input_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    output_2 = InMemoryDataNode("foo", Scope.SCENARIO)
    task_2 = Task("task", {}, print, [input_2], [output_2], TaskId("task_id_2"))
    pipeline_2 = Pipeline({}, [task_2], pipeline_id_2)

    pipeline_3_with_same_id = Pipeline({}, [], pipeline_id_1)

    # No existing Pipeline
    assert _PipelineManager._get(pipeline_id_1) is None
    assert _PipelineManager._get(pipeline_1) is None
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save one pipeline. We expect to have only one pipeline stored
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2) is None
    assert _PipelineManager._get(pipeline_2) is None

    # Save a second pipeline. Now, we expect to have a total of two pipelines stored
    _TaskManager._set(task_2)
    _PipelineManager._set(pipeline_2)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save the first pipeline again. We expect nothing to change
    _PipelineManager._set(pipeline_1)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id

    # We save a third pipeline with same id as the first one.
    # We expect the first pipeline to be updated
    _PipelineManager._set(pipeline_3_with_same_id)
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_1.id
    assert _PipelineManager._get(pipeline_id_1).id == pipeline_3_with_same_id.id
    assert len(_PipelineManager._get(pipeline_id_1).tasks) == 0
    assert _PipelineManager._get(pipeline_1).id == pipeline_1.id
    assert len(_PipelineManager._get(pipeline_1).tasks) == 0
    assert _PipelineManager._get(pipeline_id_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_id_2).tasks) == 1
    assert _PipelineManager._get(pipeline_2).id == pipeline_2.id
    assert len(_PipelineManager._get(pipeline_2).tasks) == 1
    assert _TaskManager._get(task_2.id).id == task_2.id


def test_get_all_on_multiple_versions_environment():
    # Create 5 pipelines with 2 versions each
    for version in range(1, 3):
        for i in range(5):
            _PipelineManager._set(Pipeline({}, [], PipelineId(f"id_{i}_v{version}"), version=f"{version}.0"))

    _VersionManager._set_experiment_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0

    _VersionManager._set_experiment_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v2"}])) == 1

    _VersionManager._set_development_version("1.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v1"}])) == 1
    assert len(_PipelineManager._get_all_by(filters=[{"version": "1.0", "id": "id_1_v2"}])) == 0

    _VersionManager._set_development_version("2.0")
    assert len(_PipelineManager._get_all()) == 5
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v1"}])) == 0
    assert len(_PipelineManager._get_all_by(filters=[{"version": "2.0", "id": "id_1_v2"}])) == 1


def test_is_submittable():
    assert len(_PipelineManager._get_all()) == 0
    pipeline = _PipelineManager._get_or_create("pipeline", [])

    assert len(_PipelineManager._get_all()) == 1
    assert _PipelineManager._is_submittable(pipeline)
    assert _PipelineManager._is_submittable(pipeline.id)
    assert not _PipelineManager._is_submittable("Pipeline_temp")


def test_submit():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    data_node_1 = InMemoryDataNode("foo", Scope.SCENARIO, "s1")
    data_node_2 = InMemoryDataNode("bar", Scope.SCENARIO, "s2")
    data_node_3 = InMemoryDataNode("baz", Scope.SCENARIO, "s3")
    data_node_4 = InMemoryDataNode("qux", Scope.SCENARIO, "s4")
    data_node_5 = InMemoryDataNode("quux", Scope.SCENARIO, "s5")
    data_node_6 = InMemoryDataNode("quuz", Scope.SCENARIO, "s6")
    data_node_7 = InMemoryDataNode("corge", Scope.SCENARIO, "s7")
    task_1 = Task(
        "grault",
        {},
        print,
        [data_node_1, data_node_2],
        [data_node_3, data_node_4],
        TaskId("t1"),
    )
    task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
    pipeline = Pipeline({}, [task_4, task_2, task_1, task_3], PipelineId("p1"))

    class MockOrchestrator(_Orchestrator):
        submit_calls = []

        @classmethod
        def _submit_task(
            cls,
            task: Task,
            submit_id: Optional[str] = None,
            submit_entity_id: Optional[str] = None,
            callbacks: Optional[Iterable[Callable]] = None,
            force: bool = False,
        ):
            cls.submit_calls.append(task)
            return None  # type: ignore

    with mock.patch("src.taipy.core.task._task_manager._TaskManager._orchestrator", new=MockOrchestrator):
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
        calls_ids = [t.id for t in _TaskManager._orchestrator().submit_calls]
        tasks_ids = [task_1.id, task_2.id, task_4.id, task_3.id]
        assert calls_ids == tasks_ids

        _PipelineManager._submit(pipeline)
        calls_ids = [t.id for t in _TaskManager._orchestrator().submit_calls]
        tasks_ids = tasks_ids * 2
        assert set(calls_ids) == set(tasks_ids)


def test_assign_pipeline_as_parent_of_task():
    dn_config_1 = Config.configure_data_node("dn_1", "in_memory", scope=Scope.SCENARIO)
    dn_config_2 = Config.configure_data_node("dn_2", "in_memory", scope=Scope.SCENARIO)
    dn_config_3 = Config.configure_data_node("dn_3", "in_memory", scope=Scope.SCENARIO)
    task_config_1 = Config.configure_task("task_1", print, [dn_config_1], [dn_config_2])
    task_config_2 = Config.configure_task("task_2", print, [dn_config_2], [dn_config_3])
    task_config_3 = Config.configure_task("task_3", print, [dn_config_2], [dn_config_3])

    p1_tasks = _TaskManager._bulk_get_or_create([task_config_1, task_config_2], "scenario_id")
    p2_tasks = _TaskManager._bulk_get_or_create([task_config_1, task_config_3], "scenario_id")
    pipeline_1 = _PipelineManager._get_or_create("pipeline_1", p1_tasks, "scenario_id")
    pipeline_2 = _PipelineManager._get_or_create("pipeline_2", p2_tasks, "scenario_id")

    tasks_1 = list(pipeline_1.tasks.values())
    tasks_2 = list(pipeline_2.tasks.values())

    assert len(tasks_1) == 2
    assert len(tasks_2) == 2

    assert tasks_1[0].parent_ids == {pipeline_1.id, pipeline_2.id}
    assert tasks_2[0].parent_ids == {pipeline_1.id, pipeline_2.id}
    assert tasks_1[1].parent_ids == {pipeline_1.id}
    assert tasks_2[1].parent_ids == {pipeline_2.id}


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


def test_submit_pipeline_from_tasks_with_one_or_no_input_output():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._build_dispatcher()

    # test no input and no output Task
    task_no_input_no_output = Task("task_no_input_no_output", {}, mock_function_no_input_no_output)
    pipeline_1 = Pipeline({}, [task_no_input_no_output], "my_pipeline_1")

    _TaskManager._set(task_no_input_no_output)
    _PipelineManager._set(pipeline_1)
    assert len(pipeline_1._get_sorted_tasks()) == 1

    _PipelineManager._submit(pipeline_1)
    assert g == 1

    # test one input and no output Task
    data_node_input = InMemoryDataNode("input_dn", Scope.SCENARIO, properties={"default_data": 2})
    task_one_input_no_output = Task(
        "task_one_input_no_output", {}, mock_function_one_input_no_output, input=[data_node_input]
    )
    pipeline_2 = Pipeline({}, [task_one_input_no_output], "my_pipeline_2")

    _DataManager._set(data_node_input)
    data_node_input.unlock_edition()

    _TaskManager._set(task_one_input_no_output)
    _PipelineManager._set(pipeline_2)
    assert len(pipeline_2._get_sorted_tasks()) == 1

    _PipelineManager._submit(pipeline_2)
    assert g == 3

    # test no input and one output Task
    data_node_output = InMemoryDataNode("output_dn", Scope.SCENARIO, properties={"default_data": None})
    task_no_input_one_output = Task(
        "task_no_input_one_output", {}, mock_function_no_input_one_output, output=[data_node_output]
    )
    pipeline_3 = Pipeline({}, [task_no_input_one_output], "my_pipeline_3")

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

    dn_config_1 = Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)
    dn_config_2 = Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0)
    dn_config_6 = Config.configure_data_node("baz", "in_memory", Scope.SCENARIO, default_data=0)

    task_config_mult_by_two = Config.configure_task("mult_by_two", mult_by_two, [dn_config_1], dn_config_2)
    task_config_mult_by_3 = Config.configure_task("mult_by_3", mult_by_3, [dn_config_2], dn_config_6)
    # dn_1 ---> mult_by_two ---> dn_2 ---> mult_by_3 ---> dn_6

    _OrchestratorFactory._build_dispatcher()

    assert len(_DataManager._get_all()) == 0
    assert len(_TaskManager._get_all()) == 0

    p_tasks = _TaskManager._bulk_get_or_create([task_config_mult_by_two, task_config_mult_by_3])

    pipeline = _PipelineManager._get_or_create("by_6", p_tasks)

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


def notify1(*args, **kwargs):
    ...


def notify2(*args, **kwargs):
    ...


def notify_multi_param(*args, **kwargs):
    ...


def test_pipeline_notification_subscribe(mocker):
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    mocker.patch("src.taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create(task_configs=task_configs)
    pipeline = _PipelineManager._get_or_create("by_1", tasks)

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

    mocker.patch("src.taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    pipeline = _PipelineManager._get_or_create("by_6", tasks)
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

    mocker.patch("src.taipy.core._entity._reload._Reloader._reload", side_effect=lambda m, o: o)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    pipeline = _PipelineManager._get_or_create("by_6", tasks)

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

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    pipeline = _PipelineManager._get_or_create("by_6", tasks)

    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 0], pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 1], pipeline=pipeline)
    _PipelineManager._subscribe(callback=notify_multi_param, params=["foobar", 123, 2], pipeline=pipeline)

    assert len(pipeline.subscribers) == 3

    pipeline.unsubscribe(notify_multi_param)
    assert len(pipeline.subscribers) == 2
    assert _Subscriber(notify_multi_param, ["foobar", 123, 0]) not in pipeline.subscribers

    pipeline.unsubscribe(notify_multi_param, ["foobar", 123, 2])
    assert len(pipeline.subscribers) == 1
    assert _Subscriber(notify_multi_param, ["foobar", 123, 2]) not in pipeline.subscribers

    with pytest.raises(ValueError):
        pipeline.unsubscribe(notify_multi_param, ["foobar", 123, 10000])


def test_pipeline_notification_subscribe_all():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    task_configs = [
        Config.configure_task(
            "mult_by_two",
            mult_by_two,
            [Config.configure_data_node("foo", "in_memory", Scope.SCENARIO, default_data=1)],
            Config.configure_data_node("bar", "in_memory", Scope.SCENARIO, default_data=0),
        )
    ]

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create(task_configs)
    pipeline = _PipelineManager._get_or_create("by_6", tasks)
    other_pipeline = _PipelineManager._get_or_create("other_pipeline", tasks)

    notify_1 = NotifyMock(pipeline)

    _PipelineManager._subscribe(notify_1)

    assert len(_PipelineManager._get(pipeline.id).subscribers) == 1
    assert len(_PipelineManager._get(other_pipeline.id).subscribers) == 1


def test_hard_delete_one_single_pipeline_with_scenario_data_nodes():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    pipeline = _PipelineManager._get_or_create("pipeline", tasks)
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

    dn_input_config = Config.configure_data_node("my_input", "in_memory", scope=Scope.CYCLE, default_data="testing")
    dn_output_config = Config.configure_data_node("my_output", "in_memory", scope=Scope.CYCLE)
    task_config = Config.configure_task("task_config", print, dn_input_config, dn_output_config)

    _OrchestratorFactory._build_dispatcher()

    tasks = _TaskManager._bulk_get_or_create([task_config])
    pipeline = _PipelineManager._get_or_create("pipeline", tasks)
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


def test_hard_delete_shared_entities():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO, default_data="testing")
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.GLOBAL, default_data="testing")
    task_1 = Config.configure_task("task_1", print, input_dn, intermediate_dn)
    task_2 = Config.configure_task("task_2", print, intermediate_dn, output_dn)

    _OrchestratorFactory._build_dispatcher()

    tasks_scenario_1 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_1")
    tasks_scenario_2 = _TaskManager._bulk_get_or_create([task_1, task_2], scenario_id="scenario_id_2")
    pipeline_1 = _PipelineManager._get_or_create("pipeline", tasks_scenario_1, scenario_id="scenario_id_1")
    pipeline_2 = _PipelineManager._get_or_create("pipeline", tasks_scenario_2, scenario_id="scenario_id_2")
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
    assert len(_TaskManager._get_all()) == 3
    assert len(_DataManager._get_all()) == 4
    assert len(_JobManager._get_all()) == 4


def test_data_node_creation_scenario():
    input_dn = Config.configure_data_node("my_input", "in_memory", scope=Scope.SCENARIO)
    input_global_dn = Config.configure_data_node("my_global_input", "in_memory", scope=Scope.GLOBAL)
    input_global_dn_2 = Config.configure_data_node("my_global_input_2", "in_memory", scope=Scope.GLOBAL)
    intermediate_dn = Config.configure_data_node("my_inter", "in_memory", scope=Scope.SCENARIO)
    output_dn = Config.configure_data_node("my_output", "in_memory", scope=Scope.SCENARIO)
    task_1 = Config.configure_task("task_1", print, [input_dn, input_global_dn, input_global_dn_2], intermediate_dn)
    task_2 = Config.configure_task("task_2", print, [input_dn, intermediate_dn], output_dn)

    tasks_pipeline_1 = _TaskManager._bulk_get_or_create([task_1, task_2])
    tasks_pipeline_2 = _TaskManager._bulk_get_or_create([task_1, task_2])
    pipeline_1 = _PipelineManager._get_or_create("pipeline", tasks_pipeline_1)
    pipeline_2 = _PipelineManager._get_or_create("pipeline", tasks_pipeline_2)

    assert len(_DataManager._get_all()) == 5
    assert pipeline_1.my_input.id == pipeline_2.my_input.id
    assert pipeline_1.my_global_input.id == pipeline_2.my_global_input.id
    assert pipeline_1.my_global_input_2.id == pipeline_2.my_global_input_2.id
    assert pipeline_1.my_inter.id == pipeline_2.my_inter.id
    assert pipeline_1.my_output.id == pipeline_2.my_output.id


def my_print(a, b):
    print(a + b)


def test_submit_task_with_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_path="wrong_path.pickle")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)

    tasks = _TaskManager._bulk_get_or_create([task_cfg, task_2_cfg])
    pip_manager = _PipelineManagerFactory._build_manager()
    pipeline = pip_manager._get_or_create("pipeline", tasks)
    pip_manager._submit(pipeline)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in pipeline.get_inputs()
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in pipeline.data_nodes.values()
        if input_dn not in pipeline.get_inputs()
    ]
    assert all([expected_output in stdout for expected_output in expected_outputs])
    assert all([expected_output not in stdout for expected_output in not_expected_outputs])


def test_submit_task_with_one_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_data="value")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    json_dn_cfg = Config.configure_parquet_data_node("wrong_json_file_path", default_path="wrong_path.json")
    task_cfg = Config.configure_task("task", my_print, [csv_dn_cfg, pickle_dn_cfg], parquet_dn_cfg)
    task_2_cfg = Config.configure_task("task2", my_print, [csv_dn_cfg, parquet_dn_cfg], json_dn_cfg)

    tasks = _TaskManager._bulk_get_or_create([task_cfg, task_2_cfg])
    pip_manager = _PipelineManagerFactory._build_manager()
    pipeline = pip_manager._get_or_create("pipeline", tasks)
    pip_manager._submit(pipeline)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in pipeline.get_inputs()
        if input_dn.config_id == "wrong_csv_file_path"
    ]
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in pipeline.data_nodes.values()
        if input_dn.config_id != "wrong_csv_file_path"
    ]
    assert all([expected_output in stdout for expected_output in expected_outputs])
    assert all([expected_output not in stdout for expected_output in not_expected_outputs])
