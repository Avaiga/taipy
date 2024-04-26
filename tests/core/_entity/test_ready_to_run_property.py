# Copyright 2021-2024 Avaiga Private Limited
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

from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core._entity._ready_to_run_property import _ReadyToRunProperty
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.pickle import PickleDataNode
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def test_scenario_is_ready_to_run_property():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    assert len(scenario_manager._get_all()) == 0

    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2", 10)
    dn_config_3 = Config.configure_in_memory_data_node("dn_3", 10)
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("sc", {task_config}, set(), Frequency.DAILY)
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2
    dn_3 = scenario.dn_3

    assert len(scenario_manager._get_all()) == 1
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert scenario_manager._is_submittable(scenario)
    assert scenario_manager._is_submittable(scenario.id)
    assert not scenario_manager._is_submittable("Scenario_temp")

    dn_1.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {
        f"DataNode {dn_1.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not scenario_manager._is_submittable(scenario.id)

    dn_1.edit_in_progress = False
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert scenario_manager._is_submittable(scenario.id)

    dn_1.last_edit_date = None
    dn_2.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {f"DataNode {dn_1.id} is not written"}
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not scenario_manager._is_submittable(scenario.id)

    dn_1.last_edit_date = datetime.now()
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not scenario_manager._is_submittable(scenario.id)

    dn_2.edit_in_progress = False
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert scenario_manager._is_submittable(scenario)
    assert scenario_manager._is_submittable(scenario.id)

    dn_3.edit_in_progress = True
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_3.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert scenario_manager._is_submittable(scenario.id)


def test_sequence_is_ready_to_run_property():
    data_manager = _DataManagerFactory._build_manager()
    scenario_manager = _ScenarioManagerFactory._build_manager()
    task_manager = _TaskManagerFactory._build_manager()
    sequence_manager = _SequenceManagerFactory._build_manager()

    task_id = "TASK_task_id"
    scenario_id = "SCENARIO_scenario_id"
    dn_1 = PickleDataNode("dn_1", Scope.SCENARIO, parent_ids={task_id, scenario_id}, properties={"default_data": 10})
    dn_2 = PickleDataNode("dn_2", Scope.SCENARIO, parent_ids={task_id, scenario_id}, properties={"default_data": 10})
    dn_3 = PickleDataNode("dn_3", Scope.SCENARIO, parent_ids={task_id, scenario_id}, properties={"default_data": 10})
    task = Task("task", {}, print, [dn_1, dn_2], [dn_3], id=task_id, parent_ids={scenario_id})
    scenario = Scenario("scenario", {task}, {}, set(), scenario_id=scenario_id)
    data_manager._set(dn_1)
    data_manager._set(dn_2)
    data_manager._set(dn_3)
    task_manager._set(task)
    scenario_manager._set(scenario)

    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2
    dn_3 = scenario.dn_3

    scenario.add_sequences({"sequence": [task]})
    sequence = scenario.sequences["sequence"]
    assert len(sequence_manager._get_all()) == 1
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence_manager._is_submittable(sequence)
    assert sequence_manager._is_submittable(sequence.id)
    assert scenario_manager._is_submittable(scenario)
    assert not sequence_manager._is_submittable("Sequence_temp")
    assert not sequence_manager._is_submittable("SEQUENCE_temp_SCENARIO_scenario")

    dn_1.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[sequence.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert sequence.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {
        f"DataNode {dn_1.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[sequence.id][dn_1.id] == {
        f"DataNode {dn_1.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not sequence_manager._is_submittable(sequence)
    assert not sequence_manager._is_submittable(sequence.id)

    dn_1.edit_in_progress = False
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert sequence_manager._is_submittable(sequence)
    assert sequence_manager._is_submittable(sequence.id)
    assert scenario_manager._is_submittable(scenario)

    dn_1.last_edit_date = None
    dn_2.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[sequence.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[sequence.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert sequence.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert sequence.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {f"DataNode {dn_1.id} is not written"}
    assert _ReadyToRunProperty._submittable_id_datanodes[sequence.id][dn_1.id] == {f"DataNode {dn_1.id} is not written"}
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[sequence.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not sequence_manager._is_submittable(sequence)
    assert not sequence_manager._is_submittable(sequence.id)

    dn_1.last_edit_date = datetime.now()
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id not in _ReadyToRunProperty._submittable_id_datanodes[sequence.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[sequence.id]
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert sequence.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[sequence.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert not scenario_manager._is_submittable(scenario)
    assert not sequence_manager._is_submittable(sequence)
    assert not sequence_manager._is_submittable(sequence.id)

    dn_2.edit_in_progress = False
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_2.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert sequence_manager._is_submittable(sequence)
    assert sequence_manager._is_submittable(sequence.id)

    dn_3.edit_in_progress = True
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_3.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert sequence_manager._is_submittable(sequence)
    assert sequence_manager._is_submittable(sequence.id)


def test_task_is_ready_to_run_property():
    task_manager = _TaskManagerFactory._build_manager()
    scenario_manager = _ScenarioManagerFactory._build_manager()

    assert len(task_manager._get_all()) == 0

    dn_config_1 = Config.configure_pickle_data_node("dn_1", default_data=10)
    dn_config_2 = Config.configure_pickle_data_node("dn_2", default_data=15)
    dn_config_3 = Config.configure_pickle_data_node("dn_3", default_data=20)
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("scenario", [task_config])

    scenario = scenario_manager._create(scenario_config)
    task = scenario.tasks["task"]
    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2
    dn_3 = scenario.dn_3

    assert len(task_manager._get_all()) == 1
    assert len(scenario_manager._get_all()) == 1

    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert task_manager._is_submittable(task)
    assert task_manager._is_submittable(task.id)
    assert scenario_manager._is_submittable(scenario)
    assert scenario_manager._is_submittable(scenario.id)
    assert not task_manager._is_submittable("Task_temp")

    dn_1.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[task.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert task.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {
        f"DataNode {dn_1.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[task.id][dn_1.id] == {f"DataNode {dn_1.id} is being edited"}
    assert not scenario_manager._is_submittable(scenario)
    assert not task_manager._is_submittable(task)
    assert not task_manager._is_submittable(task.id)

    dn_1.edit_in_progress = False
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert task_manager._is_submittable(task)
    assert task_manager._is_submittable(task.id)

    dn_1.last_edit_date = None
    dn_2.edit_in_progress = True
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[task.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[task.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert task.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert task.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {f"DataNode {dn_1.id} is not written"}
    assert _ReadyToRunProperty._submittable_id_datanodes[task.id][dn_1.id] == {f"DataNode {dn_1.id} is not written"}
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[task.id][dn_2.id] == {f"DataNode {dn_2.id} is being edited"}
    assert not scenario_manager._is_submittable(scenario)
    assert not task_manager._is_submittable(task)
    assert not task_manager._is_submittable(task.id)

    dn_1.last_edit_date = datetime.now()
    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id not in _ReadyToRunProperty._submittable_id_datanodes[task.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[task.id]
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert task.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id] == {
        f"DataNode {dn_2.id} is being edited"
    }
    assert _ReadyToRunProperty._submittable_id_datanodes[task.id][dn_2.id] == {f"DataNode {dn_2.id} is being edited"}
    assert not scenario_manager._is_submittable(scenario)
    assert not task_manager._is_submittable(task)
    assert not task_manager._is_submittable(task.id)

    dn_2.edit_in_progress = False
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_2.id not in _ReadyToRunProperty._datanode_id_submittables
    assert scenario_manager._is_submittable(scenario)
    assert task_manager._is_submittable(task)
    assert task_manager._is_submittable(task.id)

    dn_3.edit_in_progress = True
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert task.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert scenario_manager._is_submittable(scenario)
    assert task_manager._is_submittable(task)
    assert task_manager._is_submittable(task.id)
