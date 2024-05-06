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

from taipy import ScenarioId, SequenceId, TaskId
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.core import taipy
from taipy.core._entity._ready_to_run_property import _ReadyToRunProperty
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.pickle import PickleDataNode
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def test_non_existing_submittable_is_not_ready_to_run():
    assert not _ScenarioManagerFactory._build_manager()._is_submittable(ScenarioId("wrong_id"))
    assert not _SequenceManagerFactory._build_manager()._is_submittable(SequenceId("wrong_id"))
    assert not _TaskManagerFactory._build_manager()._is_submittable(TaskId("wrong_id"))


def test_scenario_without_input_is_ready_to_run():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    task_config = Config.configure_task("task", print, [], [])
    scenario_config = Config.configure_scenario("sc", [task_config], [], Frequency.DAILY)
    scenario = scenario_manager._create(scenario_config)

    assert scenario_manager._is_submittable(scenario)
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes


def test_scenario_submittable_with_inputs_is_ready_to_run():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2", 10)
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2], [])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = scenario_manager._create(scenario_config)

    assert scenario_manager._is_submittable(scenario)
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes


def test_scenario_submittable_even_with_output_not_ready_to_run():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2", 10)
    dn_config_3 = Config.configure_in_memory_data_node("dn_3")
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = scenario_manager._create(scenario_config)
    dn_3 = scenario.dn_3

    assert not dn_3.is_ready_for_reading
    assert scenario_manager._is_submittable(scenario)
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes


def test_scenario_not_submittable_not_in_property_because_it_is_lazy():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2")
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2], [])
    scenario_config = Config.configure_scenario("sc", [task_config], [], Frequency.DAILY)
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2

    assert dn_1.is_ready_for_reading
    assert not dn_2.is_ready_for_reading
    assert not scenario_manager._is_submittable(scenario)

    # Since it is a lazy property, the scenario and the datanodes is not yet in the dictionary
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id not in _ReadyToRunProperty._datanode_id_submittables


def test_scenario_not_submittable_if_one_input_edit_in_progress():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    task_config = Config.configure_task("task", print, [dn_config_1], [])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1
    dn_1.lock_edit()

    assert not dn_1.is_ready_for_reading
    assert not scenario_manager._is_submittable(scenario)

    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {f"DataNode {dn_1.id} is being edited"}


def test_scenario_not_submittable_for_multiple_reasons():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2")
    dn_config_3 = Config.configure_in_memory_data_node("dn_3", 10)
    task_config = Config.configure_task("task", print, [dn_config_1, dn_config_2, dn_config_3], [])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1
    dn_1.lock_edit()
    dn_2 = scenario.dn_2
    dn_2.lock_edit()

    assert not dn_1.is_ready_for_reading
    assert not dn_2.is_ready_for_reading
    assert not scenario_manager._is_submittable(scenario)

    assert scenario.id in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_2.id in _ReadyToRunProperty._submittable_id_datanodes[scenario.id]
    assert dn_1.id in _ReadyToRunProperty._datanode_id_submittables
    assert dn_2.id in _ReadyToRunProperty._datanode_id_submittables
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_1.id]
    assert _ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id] == {f"DataNode {dn_1.id} is being edited"}
    assert scenario.id in _ReadyToRunProperty._datanode_id_submittables[dn_2.id]
    assert (_ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_2.id]
            == {f"DataNode {dn_2.id} is being edited"}, f"DataNode {dn_2.id} is not written")


def test_writing_input_remove_reasons():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1")
    task_config = Config.configure_task("task", print, [dn_config_1], [])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = scenario_manager._create(scenario_config)
    dn_1 = scenario.dn_1

    assert not dn_1.is_ready_for_reading
    assert not scenario_manager._is_submittable(scenario)
    # Since it is a lazy property, the scenario is not yet in the dictionary
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes

    dn_1.lock_edit()
    assert (_ReadyToRunProperty._submittable_id_datanodes[scenario.id][dn_1.id]
            == {f"DataNode {dn_1.id} is being edited", f"DataNode {dn_1.id} is not written"})

    dn_1.write(10)
    assert scenario_manager._is_submittable(scenario)
    assert scenario.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn_1.id not in _ReadyToRunProperty._datanode_id_submittables


def identity(arg):
    return arg


def __assert_not_submittable_becomes_submittable_when_dn_edited(sequence, manager, dn):
    assert not dn.is_ready_for_reading
    assert not manager._is_submittable(sequence)
    # Since it is a lazy property, the sequence is not yet in the dictionary
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes

    dn.lock_edit()
    assert (_ReadyToRunProperty._submittable_id_datanodes[sequence.id][dn.id]
            == {f"DataNode {dn.id} is being edited", f"DataNode {dn.id} is not written"})
    dn.write("ANY VALUE")
    assert manager._is_submittable(sequence)
    assert sequence.id not in _ReadyToRunProperty._submittable_id_datanodes
    assert dn.id not in _ReadyToRunProperty._datanode_id_submittables


def test_writing_config_sequence_input_remove_reasons():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2")
    dn_config_3 = Config.configure_in_memory_data_node("dn_3")
    task_1_config = Config.configure_task("task_1", identity, [dn_config_1], [dn_config_2])
    task_2_config = Config.configure_task("task_2", identity, [dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("sc", [task_1_config, task_2_config],
                                                sequences={"seq": [task_2_config]})
    scenario = scenario_manager._create(scenario_config)

    manager = _SequenceManagerFactory._build_manager()
    __assert_not_submittable_becomes_submittable_when_dn_edited(scenario.sequences["seq"], manager, scenario.dn_2)


def test_writing_runtime_sequence_input_remove_reasons():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2")
    dn_config_3 = Config.configure_in_memory_data_node("dn_3")
    task_1_config = Config.configure_task("task_1", identity, [dn_config_1], [dn_config_2])
    task_2_config = Config.configure_task("task_2", identity, [dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("sc", [task_1_config, task_2_config])
    scenario = scenario_manager._create(scenario_config)
    scenario.add_sequence("seq", [scenario.tasks["task_2"]])

    manager = _SequenceManagerFactory._build_manager()
    __assert_not_submittable_becomes_submittable_when_dn_edited(scenario.sequences["seq"], manager, scenario.dn_2)


def test_writing_task_input_remove_reasons():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    dn_config_1 = Config.configure_in_memory_data_node("dn_1", 10)
    dn_config_2 = Config.configure_in_memory_data_node("dn_2")
    dn_config_3 = Config.configure_in_memory_data_node("dn_3")
    task_1_config = Config.configure_task("task_1", identity, [dn_config_1], [dn_config_2])
    task_2_config = Config.configure_task("task_2", identity, [dn_config_2], [dn_config_3])
    scenario_config = Config.configure_scenario("sc", [task_1_config, task_2_config])
    scenario = scenario_manager._create(scenario_config)

    manager = _TaskManagerFactory._build_manager()
    __assert_not_submittable_becomes_submittable_when_dn_edited(scenario.tasks["task_2"], manager, scenario.dn_2)
