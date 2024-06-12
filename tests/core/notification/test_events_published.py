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

from queue import SimpleQueue
from typing import Any, Dict, List

from taipy.config import Config, Frequency
from taipy.core import taipy as tp
from taipy.core.job.status import Status
from taipy.core.notification.core_event_consumer import CoreEventConsumerBase
from taipy.core.notification.event import Event, EventEntityType, EventOperation
from taipy.core.notification.notifier import Notifier
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory


class Snapshot:
    """
    A captured snapshot of the recording core events consumer.
    """

    def __init__(self) -> None:
        self.collected_events: List[Event] = []
        self.entity_type_collected: Dict[EventEntityType, int] = {}
        self.operation_collected: Dict[EventEntityType, int] = {}
        self.attr_name_collected: Dict[EventEntityType, int] = {}
        self.attr_value_collected: Dict[EventEntityType, List[Any]] = {}

    def capture_event(self, event):
        self.collected_events.append(event)
        self.entity_type_collected[event.entity_type] = self.entity_type_collected.get(event.entity_type, 0) + 1
        self.operation_collected[event.operation] = self.operation_collected.get(event.operation, 0) + 1
        if event.attribute_name:
            self.attr_name_collected[event.attribute_name] = self.attr_name_collected.get(event.attribute_name, 0) + 1
            if self.attr_value_collected.get(event.attribute_name, None):
                self.attr_value_collected[event.attribute_name].append(event.attribute_value)
            else:
                self.attr_value_collected[event.attribute_name] = [event.attribute_value]


class RecordingConsumer(CoreEventConsumerBase):
    """
    A straightforward and no-thread core events consumer that allows to
    capture snapshots of received events.
    """

    def __init__(self, registration_id: str, queue: SimpleQueue):
        super().__init__(registration_id, queue)

    def capture(self) -> Snapshot:
        """
        Capture a snapshot of events received between the previous snapshot
        (or from the start of this consumer).
        """
        snapshot = Snapshot()
        while not self.queue.empty():
            event = self.queue.get()
            snapshot.capture_event(event)
        return snapshot

    def process_event(self, event: Event):
        # Nothing to do
        pass

    def start(self):
        # Nothing to do here
        pass

    def stop(self):
        # Nothing to do here either
        pass


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
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Create a scenario via the manager
    # should only trigger 6 creation events (for cycle, data node(x2), task, sequence and scenario)
    _ScenarioManagerFactory._build_manager()._create(sc_config)
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 6
    assert snapshot.entity_type_collected.get(EventEntityType.CYCLE, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 1
    assert snapshot.operation_collected.get(EventOperation.CREATION, 0) == 6
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
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Get all scenarios does not trigger any event
    tp.get_scenarios()
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 0

    # Get one scenario does not trigger any event
    tp.get(scenario.id)
    snapshot = all_evts.capture()
    assert len(snapshot.collected_events) == 0

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
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
    all_evts.start()

    # Write input manually trigger 4 data node update events
    # for last_edit_date, editor_id, editor_expiration_date and edit_in_progress
    scenario.the_input.write("test")
    snapshot = all_evts.capture()
    assert len(snapshot.collected_events) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 4
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 4
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
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
    all_evts.start()
    # Submit a scenario triggers:
    # 1 scenario submission event
    # 7 dn update events (for last_edit_date, editor_id(x2), editor_expiration_date(x2) and edit_in_progress(x2))
    # 1 job creation event
    # 3 job update events (for status: PENDING, RUNNING and COMPLETED)
    # 1 submission creation event
    # 1 submission update event for jobs
    # 3 submission update events (for status: PENDING, RUNNING and COMPLETED)
    # 1 submission update event for is_completed
    scenario.submit()
    snapshot = all_evts.capture()
    assert len(snapshot.collected_events) == 17
    assert snapshot.entity_type_collected.get(EventEntityType.CYCLE, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 7
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 0
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.JOB, 0) == 4
    assert snapshot.entity_type_collected.get(EventEntityType.SUBMISSION, 0) == 5
    assert snapshot.operation_collected.get(EventOperation.CREATION, 0) == 2
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 14
    assert snapshot.operation_collected.get(EventOperation.SUBMISSION, 0) == 1

    assert snapshot.attr_name_collected["last_edit_date"] == 1
    assert snapshot.attr_name_collected["editor_id"] == 2
    assert snapshot.attr_name_collected["editor_expiration_date"] == 2
    assert snapshot.attr_name_collected["edit_in_progress"] == 2
    assert snapshot.attr_name_collected["status"] == 3
    assert snapshot.attr_name_collected["jobs"] == 1
    assert snapshot.attr_name_collected["submission_status"] == 3

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
    all_evts = RecordingConsumer(register_id_0, register_queue_0)
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
    snapshot = all_evts.capture()

    assert len(snapshot.collected_events) == 8
    assert snapshot.entity_type_collected.get(EventEntityType.CYCLE, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.DATA_NODE, 0) == 2
    assert snapshot.entity_type_collected.get(EventEntityType.TASK, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SEQUENCE, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SCENARIO, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.SUBMISSION, 0) == 1
    assert snapshot.entity_type_collected.get(EventEntityType.JOB, 0) == 1
    assert snapshot.operation_collected.get(EventOperation.UPDATE, 0) == 0
    assert snapshot.operation_collected.get(EventOperation.SUBMISSION, 0) == 0
    assert snapshot.operation_collected.get(EventOperation.DELETION, 0) == 8

    all_evts.stop()


def test_job_events():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    register_id, register_queue = Notifier.register(entity_type=EventEntityType.JOB)
    consumer = RecordingConsumer(register_id, register_queue)
    consumer.start()

    # Create scenario
    scenario = _ScenarioManagerFactory._build_manager()._create(sc_config)
    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 0

    # Submit scenario
    scenario.submit()
    snapshot = consumer.capture()

    # 2 events expected: one for creation, another for status update
    assert len(snapshot.collected_events) == 2
    assert snapshot.collected_events[0].operation == EventOperation.CREATION
    assert snapshot.collected_events[0].entity_type == EventEntityType.JOB
    assert snapshot.collected_events[0].metadata.get("task_config_id") == task_config.id

    assert snapshot.collected_events[1].operation == EventOperation.UPDATE
    assert snapshot.collected_events[1].entity_type == EventEntityType.JOB
    assert snapshot.collected_events[1].metadata.get("task_config_id") == task_config.id
    assert snapshot.collected_events[1].attribute_name == "status"
    assert snapshot.collected_events[1].attribute_value == Status.BLOCKED

    job = tp.get_jobs()[0]

    tp.cancel_job(job)
    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 1
    event = snapshot.collected_events[0]
    assert event.metadata.get("task_config_id") == task_config.id
    assert event.attribute_name == "status"
    assert event.attribute_value == Status.CANCELED

    consumer.stop()


def test_scenario_events():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    register_id, register_queue = Notifier.register(entity_type=EventEntityType.SCENARIO)
    consumer = RecordingConsumer(register_id, register_queue)
    consumer.start()
    scenario = tp.create_scenario(sc_config)

    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 1
    assert snapshot.collected_events[0].operation == EventOperation.CREATION
    assert snapshot.collected_events[0].entity_type == EventEntityType.SCENARIO
    assert snapshot.collected_events[0].metadata.get("config_id") == scenario.config_id

    scenario.submit()
    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 1
    assert snapshot.collected_events[0].operation == EventOperation.SUBMISSION
    assert snapshot.collected_events[0].entity_type == EventEntityType.SCENARIO
    assert snapshot.collected_events[0].metadata.get("config_id") == scenario.config_id

    # Delete scenario
    tp.delete(scenario.id)
    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 1

    assert snapshot.collected_events[0].operation == EventOperation.DELETION
    assert snapshot.collected_events[0].entity_type == EventEntityType.SCENARIO

    consumer.stop()


def test_data_node_events():
    input_config = Config.configure_data_node("the_input")
    output_config = Config.configure_data_node("the_output")
    task_config = Config.configure_task("the_task", identity, input=input_config, output=output_config)
    sc_config = Config.configure_scenario(
        "the_scenario", task_configs=[task_config], frequency=Frequency.DAILY, sequences={"the_seq": [task_config]}
    )
    register_id, register_queue = Notifier.register(entity_type=EventEntityType.DATA_NODE)
    consumer = RecordingConsumer(register_id, register_queue)
    consumer.start()

    scenario = _ScenarioManagerFactory._build_manager()._create(sc_config)

    snapshot = consumer.capture()
    # We expect two creation events since we have two data nodes:
    assert len(snapshot.collected_events) == 2

    assert snapshot.collected_events[0].operation == EventOperation.CREATION
    assert snapshot.collected_events[0].entity_type == EventEntityType.DATA_NODE
    assert snapshot.collected_events[0].metadata.get("config_id") in [output_config.id, input_config.id]

    assert snapshot.collected_events[1].operation == EventOperation.CREATION
    assert snapshot.collected_events[1].entity_type == EventEntityType.DATA_NODE
    assert snapshot.collected_events[1].metadata.get("config_id") in [output_config.id, input_config.id]

    # Delete scenario
    tp.delete(scenario.id)
    snapshot = consumer.capture()
    assert len(snapshot.collected_events) == 2

    assert snapshot.collected_events[0].operation == EventOperation.DELETION
    assert snapshot.collected_events[0].entity_type == EventEntityType.DATA_NODE

    assert snapshot.collected_events[1].operation == EventOperation.DELETION
    assert snapshot.collected_events[1].entity_type == EventEntityType.DATA_NODE

    consumer.stop()
