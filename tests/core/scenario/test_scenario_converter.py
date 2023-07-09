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

from datetime import datetime
from typing import List

from src.taipy.core.data._data_manager_factory import _DataManagerFactory
from src.taipy.core.data.in_memory import DataNode, InMemoryDataNode
from src.taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from src.taipy.core.pipeline.pipeline import Pipeline, PipelineId
from src.taipy.core.scenario._scenario_converter import _ScenarioConverter
from src.taipy.core.scenario.scenario import Scenario, ScenarioId, _ScenarioModel
from src.taipy.core.task._task_manager_factory import _TaskManagerFactory
from src.taipy.core.task.task import Task, TaskId
from taipy.config.common.scope import Scope


def test_preserve_tasks_and_data_nodes_old_scenario_with_pipeline():
    dn_manager = _DataManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()
    pipeline_manager = _PipelineManagerFactory._build_manager()
    creation_date = datetime.now()

    def _save_entities(data_nodes: List[DataNode], tasks: List[Task], pipelines: List[Pipeline]):
        for dn in data_nodes:
            dn_manager._set(dn)
        for t in tasks:
            task_manager._set(t)
        for p in pipelines:
            pipeline_manager._set(p)

    def _assert_equal(tasks_a, tasks_b) -> bool:
        if len(tasks_a) != len(tasks_b):
            return False
        for i in range(len(tasks_a)):
            task_a, task_b = tasks_a[i], tasks_b[i]
            if isinstance(task_a, list) and isinstance(task_b, list):
                if not _assert_equal(task_a, task_b):
                    return False
            elif isinstance(task_a, list) or isinstance(task_b, list):
                return False
            else:
                index_task_b = tasks_b.index(task_a)
                if any([isinstance(task_b, list) for task_b in tasks_b[i : index_task_b + 1]]):
                    return False
        return True

    # d1 ---> t1

    d1 = InMemoryDataNode("d1", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("d2", Scope.SCENARIO, "d2")
    task_1 = Task("task_1", {}, print, [d1], [d2], "t1")
    pipeline_1 = Pipeline(
        "pipeline_1", {"description": "description"}, [task_1], PipelineId("pipeline_1"), owner_id="owner_id"
    )
    _save_entities([d1, d2], [task_1], [pipeline_1])

    scenario_model_1 = _ScenarioModel(
        ScenarioId("scenario_id_1"),
        "scenario_config_1",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id],
    )
    scenario_1 = _ScenarioConverter._model_to_entity(scenario_model_1)

    assert scenario_1.id == "scenario_id_1"
    assert scenario_1.config_id == "scenario_config_1"
    assert len(scenario_1.tasks) == 1
    assert len(scenario_1.additional_data_nodes) == 0
    assert len(scenario_1.data_nodes) == 2
    assert scenario_1.tasks.keys() == {task_1.config_id}
    assert scenario_1.additional_data_nodes == {}
    assert scenario_1.data_nodes == {d1.config_id: d1, d2.config_id: d2}
    assert scenario_1._get_inputs() == {d1}
    assert scenario_1._get_set_of_tasks() == {task_1}
    _assert_equal(scenario_1._get_sorted_tasks(), [[task_1]])

    # d1 ---> t1 ---> d2
    # d3 ---> t2 ---> d4

    d1 = InMemoryDataNode("d1", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("d2", Scope.SCENARIO, "d2")
    d3 = InMemoryDataNode("d3", Scope.SCENARIO, "d3")
    d4 = InMemoryDataNode("d4", Scope.SCENARIO, "d4")
    task_1 = Task("task_1", {}, print, [d1], [d2], "t1")
    task_2 = Task("task_2", {}, print, [d3], [d4], "t2")
    pipeline_1 = Pipeline(
        "pipeline_1", {"description": "description"}, [task_1], PipelineId("pipeline_1"), owner_id="owner_id"
    )
    pipeline_2 = Pipeline(
        "pipeline_2", {"description": "description"}, [task_2], PipelineId("pipeline_2"), owner_id="owner_id"
    )
    _save_entities([d1, d2, d3, d4], [task_1, task_2], [pipeline_1, pipeline_2])

    scenario_model_2 = _ScenarioModel(
        ScenarioId("scenario_id_2"),
        "scenario_config_2",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id, pipeline_2.id],
    )
    scenario_2 = _ScenarioConverter._model_to_entity(scenario_model_2)

    assert scenario_2.id == "scenario_id_2"
    assert scenario_2.config_id == "scenario_config_2"
    assert len(scenario_2.tasks) == 2
    assert len(scenario_2.additional_data_nodes) == 0
    assert len(scenario_2.data_nodes) == 4
    assert scenario_2.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_2.additional_data_nodes == {}
    assert scenario_2.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d3.config_id: d3,
        d4.config_id: d4,
    }
    assert scenario_2._get_inputs() == {d1, d3}
    assert scenario_2._get_set_of_tasks() == {task_1, task_2}
    _assert_equal(scenario_2._get_sorted_tasks(), [[task_1, task_2]])

    # d1 ---> t1 ---> d2
    # d3 ---> t2 ---> d4

    d1 = InMemoryDataNode("d1", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("d2", Scope.SCENARIO, "d2")
    d3 = InMemoryDataNode("d3", Scope.SCENARIO, "d3")
    d4 = InMemoryDataNode("d4", Scope.SCENARIO, "d4")
    task_1 = Task("task_1", {}, print, [d1], [d2], "t1")
    task_2 = Task("task_2", {}, print, [d3], [d4], "t2")
    pipeline_1 = Pipeline(
        "pipeline_3", {"description": "description"}, [task_1, task_2], PipelineId("pipeline_3"), owner_id="owner_id"
    )
    _save_entities([d1, d2, d3, d4], [task_1, task_2], [pipeline_1])

    scenario_model_3 = _ScenarioModel(
        ScenarioId("scenario_id_3"),
        "scenario_config_3",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id],
    )
    scenario_3 = _ScenarioConverter._model_to_entity(scenario_model_3)

    assert scenario_3.id == "scenario_id_3"
    assert scenario_3.config_id == "scenario_config_3"
    assert len(scenario_3.tasks) == 2
    assert len(scenario_3.additional_data_nodes) == 0
    assert len(scenario_3.data_nodes) == 4
    assert scenario_3.tasks.keys() == {task_1.config_id, task_2.config_id}
    assert scenario_3.additional_data_nodes == {}
    assert scenario_3.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d3.config_id: d3,
        d4.config_id: d4,
    }
    assert scenario_3._get_inputs() == {d1, d3}
    assert scenario_3._get_set_of_tasks() == {task_1, task_2}
    _assert_equal(scenario_3._get_sorted_tasks(), [[task_1, task_2]])

    # d1 ---             ---> d3 ---> t2 ---> d5 ----
    #       |           |                           |
    #       |---> t1 ---|      -------------------------> t3 ---> d6
    #       |           |      |
    # d2 ---             ---> d4 ---> t4 ---> d7

    d1 = InMemoryDataNode("foo", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("bar", Scope.SCENARIO, "d2")
    d3 = InMemoryDataNode("baz", Scope.SCENARIO, "d3")
    d4 = InMemoryDataNode("qux", Scope.SCENARIO, "d4")
    d5 = InMemoryDataNode("quux", Scope.SCENARIO, "d5")
    d6 = InMemoryDataNode("quuz", Scope.SCENARIO, "d6")
    d7 = InMemoryDataNode("corge", Scope.SCENARIO, "d7")
    task_1 = Task("grault", {}, print, [d1, d2], [d3, d4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [d3], [d5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [d5, d4], [d6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [d4], [d7], TaskId("t4"))
    pipeline_1 = Pipeline("plugh", {}, [task_1, task_2, task_3], PipelineId("p1"))
    pipeline_2 = Pipeline("xyzzy", {}, [task_3, task_4], PipelineId("p2"))
    _save_entities([d1, d2, d3, d4, d5, d6, d7], [task_1, task_2, task_3, task_4], [pipeline_1, pipeline_2])

    scenario_model_4 = _ScenarioModel(
        ScenarioId("scenario_id_4"),
        "scenario_config_4",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id, pipeline_2.id],
    )
    scenario_4 = _ScenarioConverter._model_to_entity(scenario_model_4)

    assert scenario_4.id == "scenario_id_4"
    assert scenario_4.config_id == "scenario_config_4"
    assert len(scenario_4.tasks) == 4
    assert len(scenario_4.additional_data_nodes) == 0
    assert len(scenario_4.data_nodes) == 7
    assert scenario_4.tasks.keys() == {task_1.config_id, task_2.config_id, task_3.config_id, task_4.config_id}
    assert scenario_4.additional_data_nodes == {}
    assert scenario_4.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d3.config_id: d3,
        d4.config_id: d4,
        d5.config_id: d5,
        d6.config_id: d6,
        d7.config_id: d7,
    }
    assert scenario_4._get_inputs() == {d1, d2}
    assert scenario_4._get_set_of_tasks() == {task_1, task_2, task_3, task_4}
    _assert_equal(scenario_4._get_sorted_tasks(), [[task_1], [task_2, task_4], [task_3]])

    # d1 ---      t2 ---> d5 ------
    #       |                     |
    #       |---> t1 ---|      -----> t3 ---> d6
    #       |           |      |
    # d2 ---             ---> d4 ---> t4 ---> d7

    d1 = InMemoryDataNode("foo", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("bar", Scope.SCENARIO, "d2")
    d4 = InMemoryDataNode("qux", Scope.SCENARIO, "d4")
    d5 = InMemoryDataNode("quux", Scope.SCENARIO, "d5")
    d6 = InMemoryDataNode("quuz", Scope.SCENARIO, "d6")
    d7 = InMemoryDataNode("corge", Scope.SCENARIO, "d7")
    task_1 = Task("grault", {}, print, [d1, d2], [d4], TaskId("t1"))
    task_2 = Task("garply", {}, print, None, [d5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [d5, d4], [d6], TaskId("t3"))
    task_4 = Task("fred", {}, print, [d4], [d7], TaskId("t4"))
    pipeline_1 = Pipeline("plugh", {}, [task_1, task_2, task_3], PipelineId("p1"))
    pipeline_2 = Pipeline("xyzzy", {}, [task_3, task_4], PipelineId("p2"))
    _save_entities([d1, d2, d4, d5, d6, d7], [task_1, task_2, task_3, task_4], [pipeline_1, pipeline_2])

    scenario_model_5 = _ScenarioModel(
        ScenarioId("scenario_id_5"),
        "scenario_config_5",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id, pipeline_2.id],
    )
    scenario_5 = _ScenarioConverter._model_to_entity(scenario_model_5)

    assert scenario_5.id == "scenario_id_5"
    assert scenario_5.config_id == "scenario_config_5"
    assert len(scenario_5.tasks) == 4
    assert len(scenario_5.additional_data_nodes) == 0
    assert len(scenario_5.data_nodes) == 6
    assert scenario_5.tasks.keys() == {task_1.config_id, task_2.config_id, task_3.config_id, task_4.config_id}
    assert scenario_5.additional_data_nodes == {}
    assert scenario_5.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d4.config_id: d4,
        d5.config_id: d5,
        d6.config_id: d6,
        d7.config_id: d7,
    }
    assert scenario_5._get_inputs() == {d1, d2}
    assert scenario_5._get_set_of_tasks() == {task_1, task_2, task_3, task_4}
    _assert_equal(scenario_5._get_sorted_tasks(), [[task_1, task_2], [task_3, task_4]])

    # d1 ---      d6 ---> t2 ---> d5
    #       |                     |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # d2 ---             ---> d4 ---> t4 ---> d7 ---> t6
    #                                              |
    # d8 -------> t5 -------> d9 ------------------

    d1 = InMemoryDataNode("foo", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("bar", Scope.SCENARIO, "d2")
    d4 = InMemoryDataNode("qux", Scope.SCENARIO, "d4")
    d5 = InMemoryDataNode("quux", Scope.SCENARIO, "d5")
    d6 = InMemoryDataNode("quuz", Scope.SCENARIO, "d6")
    d7 = InMemoryDataNode("corge", Scope.SCENARIO, "d7")
    d8 = InMemoryDataNode("d8", Scope.SCENARIO, "d8")
    d9 = InMemoryDataNode("d9", Scope.SCENARIO, "d9")
    task_1 = Task("grault", {}, print, [d1, d2], [d4], TaskId("t1"))
    task_2 = Task("garply", {}, print, [d6], [d5], TaskId("t2"))
    task_3 = Task("waldo", {}, print, [d5, d4], id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [d4], [d7], TaskId("t4"))
    task_5 = Task("t5", {}, print, [d8], [d9], TaskId("t5"))
    task_6 = Task("t6", {}, print, [d7, d9], id=TaskId("t6"))
    pipeline_1 = Pipeline("plugh", {}, [task_1, task_2, task_3], PipelineId("p1"))
    pipeline_2 = Pipeline("xyzzy", {}, [task_3, task_4], PipelineId("p2"))
    pipeline_3 = Pipeline("thud", {}, [task_5, task_6], PipelineId("p3"))
    _save_entities(
        [d1, d2, d4, d5, d6, d7, d8, d9],
        [task_1, task_2, task_3, task_4, task_5, task_6],
        [pipeline_1, pipeline_2, pipeline_3],
    )

    scenario_model_6 = _ScenarioModel(
        ScenarioId("scenario_id_6"),
        "scenario_config_6",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id, pipeline_2.id, pipeline_3.id],
    )
    scenario_6 = _ScenarioConverter._model_to_entity(scenario_model_6)

    assert scenario_6.id == "scenario_id_6"
    assert scenario_6.config_id == "scenario_config_6"
    assert len(scenario_6.tasks) == 6
    assert len(scenario_6.additional_data_nodes) == 0
    assert len(scenario_6.data_nodes) == 8
    assert scenario_6.tasks.keys() == {
        task_1.config_id,
        task_2.config_id,
        task_3.config_id,
        task_4.config_id,
        task_5.config_id,
        task_6.config_id,
    }
    assert scenario_6.additional_data_nodes == {}
    assert scenario_6.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d4.config_id: d4,
        d5.config_id: d5,
        d6.config_id: d6,
        d7.config_id: d7,
        d8.config_id: d8,
        d9.config_id: d9,
    }
    assert scenario_6._get_inputs() == {d1, d2, d6, d8}
    assert scenario_6._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5, task_6}
    _assert_equal(scenario_6._get_sorted_tasks(), [[task_1, task_2, task_5], [task_3, task_4], [task_6]])

    # d1 ---
    #       |
    #       |---> t1 ---|      -----> t3
    #       |           |      |
    # d2 ---             ---> d4 ---> t4 ---> d7
    # t2 ---> d5                   |
    # d8 ---> t5              d6 --|

    d1 = InMemoryDataNode("foo", Scope.SCENARIO, "d1")
    d2 = InMemoryDataNode("bar", Scope.SCENARIO, "d2")
    d4 = InMemoryDataNode("qux", Scope.SCENARIO, "d4")
    d5 = InMemoryDataNode("quux", Scope.SCENARIO, "d5")
    d6 = InMemoryDataNode("quuz", Scope.SCENARIO, "d6")
    d7 = InMemoryDataNode("corge", Scope.SCENARIO, "d7")
    d8 = InMemoryDataNode("hugh", Scope.SCENARIO, "d8")
    task_1 = Task("grault", {}, print, [d1, d2], [d4], TaskId("t1"))
    task_2 = Task("garply", {}, print, output=[d5], id=TaskId("t2"))
    task_3 = Task("waldo", {}, print, [d4], None, id=TaskId("t3"))
    task_4 = Task("fred", {}, print, [d4, d6], [d7], TaskId("t4"))
    task_5 = Task("bob", {}, print, [d8], None, TaskId("t5"))
    pipeline_1 = Pipeline("plugh", {}, [task_1, task_2, task_3], PipelineId("p1"))
    pipeline_2 = Pipeline("xyzzy", {}, [task_3, task_4], PipelineId("p2"))
    pipeline_3 = Pipeline("p3", {}, [task_5], PipelineId("p3"))
    _save_entities(
        [d1, d2, d4, d5, d6, d7, d8], [task_1, task_2, task_3, task_4, task_5], [pipeline_1, pipeline_2, pipeline_3]
    )

    scenario_model_7 = _ScenarioModel(
        ScenarioId("scenario_id_7"),
        "scenario_config_7",
        [],
        [],
        {},
        creation_date.isoformat(),
        False,
        [],
        [],
        "version",
        [pipeline_1.id, pipeline_2.id, pipeline_3.id],
    )
    scenario_7 = _ScenarioConverter._model_to_entity(scenario_model_7)

    assert scenario_7.id == "scenario_id_7"
    assert scenario_7.config_id == "scenario_config_7"
    assert len(scenario_7.tasks) == 5
    assert len(scenario_7.additional_data_nodes) == 0
    assert len(scenario_7.data_nodes) == 7
    assert scenario_7.tasks.keys() == {
        task_1.config_id,
        task_2.config_id,
        task_3.config_id,
        task_4.config_id,
        task_5.config_id,
    }
    assert scenario_7.additional_data_nodes == {}
    assert scenario_7.data_nodes == {
        d1.config_id: d1,
        d2.config_id: d2,
        d4.config_id: d4,
        d5.config_id: d5,
        d6.config_id: d6,
        d7.config_id: d7,
        d8.config_id: d8,
    }
    assert scenario_7._get_inputs() == {d1, d2, d6, d8}
    assert scenario_7._get_set_of_tasks() == {task_1, task_2, task_3, task_4, task_5}
    _assert_equal(scenario_7._get_sorted_tasks(), [[task_1, task_2, task_5], [task_3, task_4]])
