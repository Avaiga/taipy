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


from taipy.common.config.config import Config
from taipy.core.notification.event import EventEntityType, EventOperation
from taipy.core.notification.notifier import Notifier
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from tests.core.notification.test_events_published import RecordingConsumer


def empty_fct(inp):
    return inp


def test_lock_edit_publish_submittable_event():
    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    dn_config_2 = Config.configure_pickle_data_node("dn_2")
    task_config = Config.configure_task("task", empty_fct, [dn_config_1], [dn_config_2])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = _ScenarioManagerFactory._build_manager()._create(scenario_config)
    scenario.add_sequences({"sequence": [scenario.task]})
    dn_1 = scenario.dn_1
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = RecordingConsumer(register_id_0, register_queue_0)

    all_evts.start()
    dn_1.lock_edit()
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 6
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 3
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 1
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 6
    assert snapshot.attr_name_collected["is_submittable"] == 3
    assert snapshot.attr_value_collected["is_submittable"] == [False, False, False]


def test_write_never_written_input_does_not_publish_submittable_event():
    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    dn_config_2 = Config.configure_pickle_data_node("dn_2")
    task_config = Config.configure_task("task", empty_fct, [dn_config_1], [dn_config_2])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = _ScenarioManagerFactory._build_manager()._create(scenario_config)
    scenario.add_sequences({"sequence": [scenario.task]})
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = RecordingConsumer(register_id_0, register_queue_0)

    all_evts.start()
    scenario.dn_1.write(15)
    snapshot = all_evts.capture()

    # Since it is a lazy property, no submittable event is published. Only the data node update events are published.
    assert len(snapshot.collected_events) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 4
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 4


def test_write_never_written_input_publish_submittable_event_if_scenario_in_property():
    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    dn_config_2 = Config.configure_pickle_data_node("dn_2")
    task_config = Config.configure_task("task", empty_fct, [dn_config_1], [dn_config_2])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = _ScenarioManagerFactory._build_manager()._create(scenario_config)
    scenario.add_sequences({"sequence": [scenario.task]})
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = RecordingConsumer(register_id_0, register_queue_0)

    # This makes the dn_1 not ready for 2 reasons. 1. It is not written. 2. It is locked. PLus it makes the scenario,
    # the sequence and the task handled by the property.
    scenario.dn_1.lock_edit()

    all_evts.start()
    scenario.dn_1.write(15)
    snapshot = all_evts.capture()

    # Since it is a lazy property, no submittable event is published. Only the data node update events are published.
    assert len(snapshot.collected_events) == 13
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 7
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 2
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 13
    assert snapshot.attr_name_collected["is_submittable"] == 6
    assert snapshot.attr_value_collected["is_submittable"] == [False, False, False, True, True, True]


def test_write_output_does_not_publish_submittable_event():
    dn_config_1 = Config.configure_pickle_data_node("dn_1", default_data="any value")
    dn_config_2 = Config.configure_pickle_data_node("dn_2")
    task_config = Config.configure_task("task", empty_fct, [dn_config_1], [dn_config_2])
    scenario_config = Config.configure_scenario("sc", [task_config])
    scenario = _ScenarioManagerFactory._build_manager()._create(scenario_config)
    scenario.add_sequences({"sequence": [scenario.task]})
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = RecordingConsumer(register_id_0, register_queue_0)

    all_evts.start()
    scenario.dn_2.write(15)
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 4
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 4
    assert "is_submittable" not in snapshot.attr_name_collected
    assert "is_submittable" not in snapshot.attr_value_collected
    all_evts.stop()
