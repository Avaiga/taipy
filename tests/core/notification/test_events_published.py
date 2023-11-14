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

from queue import SimpleQueue

from src.taipy.core import taipy as tp
from src.taipy.core.notification.core_event_consumer import CoreEventConsumerBase
from src.taipy.core.notification.event import Event, EventEntityType, EventOperation
from src.taipy.core.notification.notifier import Notifier
from taipy.config import Config, Frequency
from tests.core.utils import assert_true_after_time


class AllCoreEventConsumer(CoreEventConsumerBase):
    def __init__(self, registration_id: str, queue: SimpleQueue):
        self.event_collected = 0
        self.entity_type_collected: dict = {}
        self.operation_collected: dict = {}
        self.attr_name_collected: dict = {}
        super().__init__(registration_id, queue)

    def process_event(self, event: Event):
        self.event_collected += 1
        self.entity_type_collected[event.entity_type] = self.entity_type_collected.get(event.entity_type, 0) + 1
        self.operation_collected[event.operation] = self.operation_collected.get(event.operation, 0) + 1
        if event.attribute_name:
            self.attr_name_collected[event.attribute_name] = self.attr_name_collected.get(event.attribute_name, 0) + 1


def identity(x):
    return x


def test_events_published_for_scenario_creation():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = AllCoreEventConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Create a scenario only trigger 6 creation events (for cycle, data node(x2), task, sequence and scenario)
    tp.create_scenario(sc_config)

    assert_true_after_time(lambda: all_evts.event_collected == 6, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.CYCLE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.TASK] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SEQUENCE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SCENARIO] == 1, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.CREATION] == 6, time=10)
    all_evts.stop()


def test_no_event_published_for_getting_scenario():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    scenario = tp.create_scenario(sc_config)

    register_id_0, register_queue_0 = Notifier.register()
    all_evts = AllCoreEventConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Get all scenarios does not trigger any event
    tp.get_scenarios()
    assert_true_after_time(lambda: all_evts.event_collected == 0, time=10)

    # Get one scenario does not trigger any event
    sc = tp.get(scenario.id)
    assert_true_after_time(lambda: all_evts.event_collected == 0, time=10)

    all_evts.stop()


def test_events_published_for_writing_dn():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    scenario = tp.create_scenario(sc_config)
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = AllCoreEventConsumer(register_id_0, register_queue_0)
    all_evts.start()

    # Write input manually trigger 4 data node update events
    # for last_edit_date, editor_id, editor_expiration_date and edit_in_progress
    scenario.the_input.write("test")
    assert_true_after_time(lambda: all_evts.event_collected == 4, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 4, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.UPDATE] == 4, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["last_edit_date"] == 1, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["editor_id"] == 1, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["editor_expiration_date"] == 1, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["edit_in_progress"] == 1, time=10)
    all_evts.stop()


def test_events_published_for_scenario_submission():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    scenario = tp.create_scenario(sc_config)
    scenario.the_input.write("test")
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = AllCoreEventConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Submit a scenario triggers:
    # 1 scenario submission event
    # 7 dn update events (for last_edit_date, editor_id(x2), editor_expiration_date(x2) and edit_in_progress(x2))
    # 1 job creation event
    # 3 job update events (for status: PENDING, RUNNING and COMPLETED)
    # 1 submission creation event
    # 1 submission update event for jobs
    # 3 submission update events (for status: PENDING, RUNNING and COMPLETED)
    scenario.submit()
    assert_true_after_time(lambda: all_evts.event_collected == 17, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SCENARIO] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 7, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.JOB] == 4, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SUBMISSION] == 5, time=10)

    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.SUBMISSION] == 1, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.CREATION] == 2, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.UPDATE] == 14, time=10)

    assert_true_after_time(lambda: all_evts.attr_name_collected["last_edit_date"] == 1, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["editor_id"] == 2, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["editor_expiration_date"] == 2, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["edit_in_progress"] == 2, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["status"] == 3, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["jobs"] == 1, time=10)
    assert_true_after_time(lambda: all_evts.attr_name_collected["submission_status"] == 3, time=10)
    all_evts.stop()


def test_events_published_for_scenario_deletion():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    scenario = tp.create_scenario(sc_config)
    scenario.the_input.write("test")
    scenario.submit()
    register_id_0, register_queue_0 = Notifier.register()
    all_evts = AllCoreEventConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Delete a scenario trigger 8 deletion events
    # 1 scenario deletion event
    # 1 cycle deletion event
    # 2 dn deletion events (for input and output)
    # 1 task deletion event
    # 1 sequence deletion event
    # 1 job deletion event
    # 1 submission deletion event
    tp.delete(scenario.id)
    assert_true_after_time(lambda: all_evts.event_collected == 8, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.CYCLE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.TASK] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SEQUENCE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SCENARIO] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.JOB] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SUBMISSION] == 1, time=10)

    # Submit a scenario triggers 12 events:
    # 1 scenario submission event
    # 7 data node update events (for last_edit_date, editor_id(x2), editor_expiration_date(x2) and edit_in_progress(x2))
    # 1 job creation event
    # 3 job update events (for status: PENDING, RUNNING and COMPLETED)
    scenario.submit()
    assert_true_after_time(lambda: all_evts.event_collected == 30, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.CYCLE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 13, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.TASK] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SEQUENCE] == 1, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SCENARIO] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.JOB] == 4, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SUBMISSION] == 8, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.CREATION] == 8, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.UPDATE] == 21, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.SUBMISSION] == 1, time=10)

    # Delete a scenario trigger 7 update events
    tp.delete(scenario.id)
    assert_true_after_time(lambda: all_evts.event_collected == 37, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.CYCLE] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.DATA_NODE] == 15, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.TASK] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SEQUENCE] == 2, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SCENARIO] == 3, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.JOB] == 5, time=10)
    assert_true_after_time(lambda: all_evts.entity_type_collected[EventEntityType.SUBMISSION] == 8, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.CREATION] == 8, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.UPDATE] == 21, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.SUBMISSION] == 1, time=10)
    assert_true_after_time(lambda: all_evts.operation_collected[EventOperation.DELETION] == 8, time=10)

    all_evts.stop()
