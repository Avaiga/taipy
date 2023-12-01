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

from src.taipy.config import Config
from src.taipy.config.common.frequency import Frequency
from src.taipy.core import taipy as tp
from src.taipy.core.notification.core_event_consumer import CoreEventConsumerBase
from src.taipy.core.notification.event import Event, EventEntityType, EventOperation
from src.taipy.core.notification.notifier import Notifier
from tests.core.utils import assert_true_after_time


class AllCoreEventConsumerProcessor(CoreEventConsumerBase):
    def __init__(self, registration_id: str, queue: SimpleQueue):
        self.event_collected = 0
        self.event_entity_type_collected: dict = {}
        self.event_operation_collected: dict = {}
        super().__init__(registration_id, queue)

    def process_event(self, event: Event):
        self.event_collected += 1
        self.event_entity_type_collected[event.entity_type] = (
            self.event_entity_type_collected.get(event.entity_type, 0) + 1
        )
        self.event_operation_collected[event.operation] = self.event_operation_collected.get(event.operation, 0) + 1


class ScenarioCoreEventConsumerProcessor(CoreEventConsumerBase):
    def __init__(self, registration_id: str, queue: SimpleQueue):
        self.scenario_event_collected = 0
        self.event_operation_collected: dict = {}
        super().__init__(registration_id, queue)

    def process_event(self, event: Event):
        self.scenario_event_collected += 1
        self.event_operation_collected[event.operation] = self.event_operation_collected.get(event.operation, 0) + 1


class TaskCreationCoreEventConsumerProcessor(CoreEventConsumerBase):
    def __init__(self, registration_id: str, queue: SimpleQueue):
        self.task_event_collected = 0
        self.creation_event_operation_collected = 0
        super().__init__(registration_id, queue)

    def process_event(self, event: Event):
        self.task_event_collected += 1
        self.creation_event_operation_collected += 1


def test_core_event_consumer():
    register_id_0, register_queue_0 = Notifier.register()
    all_evt_csumer_0 = AllCoreEventConsumerProcessor(register_id_0, register_queue_0)

    register_id_1, register_queue_1 = Notifier.register(entity_type=EventEntityType.SCENARIO)
    sc_evt_csumer_1 = ScenarioCoreEventConsumerProcessor(register_id_1, register_queue_1)

    register_id_2, register_queue_2 = Notifier.register(
        entity_type=EventEntityType.TASK, operation=EventOperation.CREATION
    )
    task_creation_evt_csumer_2 = TaskCreationCoreEventConsumerProcessor(register_id_2, register_queue_2)

    all_evt_csumer_0.start()
    sc_evt_csumer_1.start()
    task_creation_evt_csumer_2.start()

    dn_config = Config.configure_data_node("dn_config")
    task_config = Config.configure_task("task_config", print, [dn_config])
    scenario_config = Config.configure_scenario(
        "scenario_config", [task_config], frequency=Frequency.DAILY, sequences={"seq": [task_config]}
    )

    # Create a scenario trigger 5 creation events
    scenario = tp.create_scenario(scenario_config)
    assert_true_after_time(lambda: all_evt_csumer_0.event_collected == 5, time=10)
    assert_true_after_time(lambda: len(all_evt_csumer_0.event_entity_type_collected) == 5, time=10)
    assert_true_after_time(lambda: all_evt_csumer_0.event_operation_collected[EventOperation.CREATION] == 5, time=10)
    assert_true_after_time(lambda: sc_evt_csumer_1.scenario_event_collected == 1, time=10)
    assert_true_after_time(lambda: sc_evt_csumer_1.event_operation_collected[EventOperation.CREATION] == 1, time=10)
    assert_true_after_time(lambda: len(sc_evt_csumer_1.event_operation_collected) == 1, time=10)
    assert_true_after_time(lambda: task_creation_evt_csumer_2.task_event_collected == 1, time=10)
    assert_true_after_time(lambda: task_creation_evt_csumer_2.creation_event_operation_collected == 1, time=10)

    # Delete a scenario trigger 5 update events
    tp.delete(scenario.id)
    assert_true_after_time(lambda: all_evt_csumer_0.event_collected == 10, time=10)
    assert_true_after_time(lambda: len(all_evt_csumer_0.event_entity_type_collected) == 5, time=10)
    assert_true_after_time(lambda: all_evt_csumer_0.event_operation_collected[EventOperation.DELETION] == 5, time=10)
    assert_true_after_time(lambda: sc_evt_csumer_1.scenario_event_collected == 2, time=10)
    assert_true_after_time(lambda: sc_evt_csumer_1.event_operation_collected[EventOperation.DELETION] == 1, time=10)
    assert_true_after_time(lambda: len(sc_evt_csumer_1.event_operation_collected) == 2, time=10)
    assert_true_after_time(lambda: task_creation_evt_csumer_2.task_event_collected == 1, time=10)
    assert_true_after_time(lambda: task_creation_evt_csumer_2.creation_event_operation_collected == 1, time=10)

    all_evt_csumer_0.stop()
    sc_evt_csumer_1.stop()
    task_creation_evt_csumer_2.stop()
