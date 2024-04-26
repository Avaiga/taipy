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


from taipy.config.config import Config
from taipy.core.notification.event import EventEntityType, EventOperation
from taipy.core.notification.notifier import Notifier
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from tests.core.notification.test_events_published import RecordingConsumer


def empty_fct(inp):
    return inp


def test_published_is_ready_to_run_event():
    scenario_manager = _ScenarioManagerFactory._build_manager()
    assert len(scenario_manager._get_all()) == 0

    dn_config_1 = Config.configure_pickle_data_node("dn_1")
    dn_config_2 = Config.configure_pickle_data_node("dn_2")
    task_config = Config.configure_task("task", empty_fct, [dn_config_1], [dn_config_2])
    scenario_config = Config.configure_scenario("sc", {task_config}, set())
    scenario = scenario_manager._create(scenario_config)
    scenario.add_sequences({"sequence": [scenario.task]})
    dn_1 = scenario.dn_1
    dn_2 = scenario.dn_2

    register_id_0, register_queue_0 = Notifier.register()
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
    all_evts.start()

    dn_1.lock_edit()
    dn_1.write(15)

    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 13
    assert snapshot.entity_type_collected.get(EventEntityType.CYCLE, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 7
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 2
    assert snapshot.operation_collected.get(EventOperation.CREATION, 0) == 0
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 13
    assert snapshot.attr_name_collected["is_submittable"] == 6

    dn_2.write(15)
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.CYCLE, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 0
    assert snapshot.operation_collected.get(EventOperation.CREATION, 0) == 0
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 4
    assert snapshot.attr_name_collected["editor_id"] == 1
    assert snapshot.attr_name_collected["editor_expiration_date"] == 1
    assert snapshot.attr_name_collected["edit_in_progress"] == 1
    assert snapshot.attr_name_collected["last_edit_date"] == 1
    all_evts.stop()
