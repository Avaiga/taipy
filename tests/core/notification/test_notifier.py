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
from src.taipy.core.notification import EventEntityType, EventOperation
from src.taipy.core.notification.event import Event
from src.taipy.core.notification.notifier import Notifier
from src.taipy.core.notification.topic import Topic
from taipy.config import Config, Frequency


def test_register():
    def find_registration_and_topic(registration_id):
        for topic, registrations in Notifier._topics_registrations_list.items():
            for registration in registrations:
                if registration.registration_id == registration_id:
                    return topic, registration

    assert len(Notifier._topics_registrations_list) == 0

    registration_id_0, register_queue_0 = Notifier.register()
    topic_0, registration_0 = find_registration_and_topic(registration_id_0)

    assert isinstance(registration_id_0, str) and registration_id_0 == registration_0.registration_id
    assert isinstance(register_queue_0, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 1
    assert len(Notifier._topics_registrations_list[topic_0]) == 1
    assert registration_0.queue == register_queue_0
    assert register_queue_0 in [registration.queue for registration in Notifier._topics_registrations_list[topic_0]]

    registration_id_1, register_queue_1 = Notifier.register()
    topic_1, registration_1 = find_registration_and_topic(registration_id_1)

    assert isinstance(registration_id_1, str) and registration_id_1 == registration_1.registration_id
    assert isinstance(register_queue_1, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 1
    assert len(Notifier._topics_registrations_list[topic_1]) == 2
    assert registration_1.queue == register_queue_1
    assert register_queue_1 in [registration.queue for registration in Notifier._topics_registrations_list[topic_1]]

    registration_id_2, register_queue_2 = Notifier.register(EventEntityType.SCENARIO)
    topic_2, registration_2 = find_registration_and_topic(registration_id_2)

    assert isinstance(registration_id_2, str) and registration_id_2 == registration_2.registration_id
    assert isinstance(register_queue_2, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 2
    assert len(Notifier._topics_registrations_list[topic_2]) == 1
    assert registration_2.queue == register_queue_2
    assert register_queue_2 in [registration.queue for registration in Notifier._topics_registrations_list[topic_2]]

    registration_id_3, register_queue_3 = Notifier.register(EventEntityType.SCENARIO, "scenario_id")
    topic_3, registration_3 = find_registration_and_topic(registration_id_3)

    assert isinstance(registration_id_3, str) and registration_id_3 == registration_3.registration_id
    assert isinstance(register_queue_3, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert len(Notifier._topics_registrations_list[topic_3]) == 1
    assert registration_3.queue == register_queue_3
    assert register_queue_3 in [registration.queue for registration in Notifier._topics_registrations_list[topic_3]]

    registration_id_4, register_queue_4 = Notifier.register(
        EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"
    )
    topic_4, registration_4 = find_registration_and_topic(registration_id_4)

    assert isinstance(registration_id_4, str) and registration_id_4 == registration_4.registration_id
    assert isinstance(register_queue_4, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_4]) == 1
    assert registration_4.queue == register_queue_4
    assert register_queue_4 in [registration.queue for registration in Notifier._topics_registrations_list[topic_4]]

    registration_id_5, register_queue_5 = Notifier.register(EventEntityType.SCENARIO)
    topic_5, registration_5 = find_registration_and_topic(registration_id_5)

    assert isinstance(registration_id_5, str) and registration_id_5 == registration_5.registration_id
    assert isinstance(register_queue_5, SimpleQueue)
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_5]) == 2
    assert registration_5.queue == register_queue_5
    assert register_queue_5 in [registration.queue for registration in Notifier._topics_registrations_list[topic_5]]

    registration_id_6, register_queue_6 = Notifier.register()
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_0]) == 3

    Notifier.unregister(registration_id_6)
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_0]) == 2

    Notifier.unregister(registration_id_4)
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert topic_4 not in Notifier._topics_registrations_list.keys()

    Notifier.unregister(registration_id_0)
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert len(Notifier._topics_registrations_list[topic_0]) == 1

    Notifier.unregister(registration_id_1)
    assert len(Notifier._topics_registrations_list.keys()) == 2

    print(Notifier._topics_registrations_list.keys())
    assert all(topic not in Notifier._topics_registrations_list.keys() for topic in [topic_0, topic_1])

    Notifier.unregister(registration_id_2)
    Notifier.unregister(registration_id_3)
    Notifier.unregister(registration_id_5)
    assert len(Notifier._topics_registrations_list.keys()) == 0


def test_matching():
    assert Notifier.is_matching(Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION), Topic())
    assert Notifier.is_matching(
        Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION), Topic(EventEntityType.CYCLE)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION), Topic(EventEntityType.CYCLE, "cycle_id")
    )
    assert Notifier.is_matching(
        Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION), Topic(operation=EventOperation.CREATION)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION),
        Topic(EventEntityType.CYCLE, "cycle_id", EventOperation.CREATION),
    )

    assert Notifier.is_matching(Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION), Topic())
    assert Notifier.is_matching(
        Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION), Topic(EventEntityType.SCENARIO)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION),
        Topic(
            EventEntityType.SCENARIO,
            "scenario_id",
        ),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION),
        Topic(operation=EventOperation.SUBMISSION),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION),
        Topic(EventEntityType.SCENARIO, "scenario_id", EventOperation.SUBMISSION),
    )

    assert Notifier.is_matching(Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"), Topic())
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"), Topic(EventEntityType.SEQUENCE)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(
            EventEntityType.SEQUENCE,
            "sequence_id",
        ),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(operation=EventOperation.UPDATE),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"), Topic(attribute_name="tasks")
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.SEQUENCE, attribute_name="tasks"),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(operation=EventOperation.UPDATE, attribute_name="tasks"),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.SEQUENCE, "sequence_id", EventOperation.UPDATE, "tasks"),
    )
    assert Notifier.is_matching(Event(EventEntityType.TASK, "task_id", EventOperation.DELETION), Topic())
    assert Notifier.is_matching(
        Event(EventEntityType.TASK, "task_id", EventOperation.DELETION), Topic(EventEntityType.TASK)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.TASK, "task_id", EventOperation.DELETION),
        Topic(
            EventEntityType.TASK,
            "task_id",
        ),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.TASK, "task_id", EventOperation.DELETION), Topic(operation=EventOperation.DELETION)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.TASK, "task_id", EventOperation.DELETION),
        Topic(EventEntityType.TASK, "task_id", EventOperation.DELETION),
    )

    assert not Notifier.is_matching(
        Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION), Topic(EventEntityType.CYCLE)
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION),
        Topic(EventEntityType.SCENARIO, "scenario_id"),
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.DATA_NODE, "dn_id", EventOperation.CREATION),
        Topic(EventEntityType.TASK, "task_id", EventOperation.CREATION),
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.JOB, "job_id", EventOperation.DELETION),
        Topic(EventEntityType.JOB, "job_id", EventOperation.CREATION),
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.JOB, "job_id", EventOperation.DELETION),
        Topic(EventEntityType.JOB, "job_id_1", EventOperation.DELETION),
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.JOB, "job_id", EventOperation.UPDATE, "status"),
        Topic(EventEntityType.JOB, "job_id", EventOperation.UPDATE, "submit_id"),
    )
    assert not Notifier.is_matching(
        Event(EventEntityType.JOB, "job_id", EventOperation.UPDATE, "status"),
        Topic(operation=EventOperation.UPDATE, attribute_name="submit_id"),
    )


def test_publish_event():
    _, registration_queue = Notifier.register()

    dn_config = Config.configure_data_node("dn_config")
    task_config = Config.configure_task("task_config", print, [dn_config])
    scenario_config = Config.configure_scenario(
        "scenario_config", [task_config], frequency=Frequency.DAILY, flag="test"
    )
    scenario_config.add_sequences({"sequence_config": [task_config]})

    # Test CREATION Event

    scenario = tp.create_scenario(scenario_config)
    cycle = scenario.cycle
    task = scenario.tasks[task_config.id]
    dn = scenario.data_nodes[dn_config.id]
    # NOTE: sequence is created only when accessed via scenario.sequences
    sequence = scenario.sequences["sequence_config"]

    assert registration_queue.qsize() == 6

    published_events = []
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_event_types = [
        EventEntityType.CYCLE,
        EventEntityType.DATA_NODE,
        EventEntityType.TASK,
        EventEntityType.SEQUENCE,
        EventEntityType.SCENARIO,
        EventEntityType.SEQUENCE,
    ]
    expected_event_entity_id = [cycle.id, dn.id, task.id, sequence.id, scenario.id, sequence.id]

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == EventOperation.CREATION
            and event.attribute_name is None
            for i, event in enumerate(published_events)
        ]
    )

    # Test UPDATE Event

    scenario.is_primary = False
    assert registration_queue.qsize() == 1

    tp.set_primary(scenario)
    assert registration_queue.qsize() == 2

    tp.subscribe_scenario(print, None, scenario=scenario)
    assert registration_queue.qsize() == 3

    tp.unsubscribe_scenario(print, None, scenario=scenario)
    assert registration_queue.qsize() == 4

    tp.tag(scenario, "testing")
    assert registration_queue.qsize() == 5

    tp.untag(scenario, "testing")
    assert registration_queue.qsize() == 6

    scenario.properties["flag"] = "production"
    assert registration_queue.qsize() == 7

    scenario.properties.update({"description": "a scenario", "test_mult": True})
    assert registration_queue.qsize() == 9

    scenario.properties.pop("test_mult")
    assert registration_queue.qsize() == 10

    scenario.name = "my_scenario"
    assert registration_queue.qsize() == 11

    cycle.name = "new cycle name"
    assert registration_queue.qsize() == 12

    cycle.properties["valid"] = True
    assert registration_queue.qsize() == 13

    cycle.properties.update({"re_run_periodically": True})
    assert registration_queue.qsize() == 14

    cycle.properties.pop("re_run_periodically")
    assert registration_queue.qsize() == 15

    sequence.properties["name"] = "weather_forecast"
    assert registration_queue.qsize() == 17

    tp.subscribe_sequence(print, None, sequence)
    assert registration_queue.qsize() == 18

    tp.unsubscribe_sequence(print, None, sequence)
    assert registration_queue.qsize() == 19

    task.skippable = True
    assert registration_queue.qsize() == 20

    task.properties["number_of_run"] = 2
    assert registration_queue.qsize() == 21

    task.properties.update({"debug": True})
    assert registration_queue.qsize() == 22

    task.properties.pop("debug")
    assert registration_queue.qsize() == 23

    dn.name = "new datanode name"
    assert registration_queue.qsize() == 24

    dn.properties["sorted"] = True
    assert registration_queue.qsize() == 25

    dn.properties.update({"only_fetch_first_100": True})
    assert registration_queue.qsize() == 26

    dn.properties.pop("only_fetch_first_100")
    assert registration_queue.qsize() == 27

    published_events = []
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_event_types = [
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.CYCLE,
        EventEntityType.CYCLE,
        EventEntityType.CYCLE,
        EventEntityType.CYCLE,
        EventEntityType.SEQUENCE,
        EventEntityType.SEQUENCE,
        EventEntityType.SEQUENCE,
        EventEntityType.SEQUENCE,
        EventEntityType.TASK,
        EventEntityType.TASK,
        EventEntityType.TASK,
        EventEntityType.TASK,
        EventEntityType.DATA_NODE,
        EventEntityType.DATA_NODE,
        EventEntityType.DATA_NODE,
        EventEntityType.DATA_NODE,
    ]
    expected_attribute_names = [
        "is_primary",
        "is_primary",
        "subscribers",
        "subscribers",
        "tags",
        "tags",
        "properties",
        "properties",
        "properties",
        "properties",
        "properties",
        "name",
        "properties",
        "properties",
        "properties",
        None,
        "properties",
        "subscribers",
        "subscribers",
        "skippable",
        "properties",
        "properties",
        "properties",
        "name",
        "properties",
        "properties",
        "properties",
    ]
    expected_event_entity_id = [
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        cycle.id,
        cycle.id,
        cycle.id,
        cycle.id,
        sequence.id,
        sequence.id,
        sequence.id,
        sequence.id,
        task.id,
        task.id,
        task.id,
        task.id,
        dn.id,
        dn.id,
        dn.id,
        dn.id,
    ]

    expected_event_operation_type = [EventOperation.UPDATE] * len(expected_event_types)
    expected_event_operation_type[15] = EventOperation.CREATION

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == expected_event_operation_type[i]
            and event.attribute_name == expected_attribute_names[i]
            for i, event in enumerate(published_events)
        ]
    )

    # Test UPDATE Event in Context Manager

    assert registration_queue.qsize() == 0

    # If multiple entities is in context, the last to enter will be the first to exit
    # So the published event will have the order starting with scenario first and ending with dn
    with dn as d, task as t, sequence as pl, cycle as c, scenario as sc:

        sc.is_primary = True
        assert registration_queue.qsize() == 0

        tp.set_primary(sc)
        assert registration_queue.qsize() == 0

        sc.properties["flag"] = "production"
        assert registration_queue.qsize() == 0

        sc.properties.update({"description": "a scenario"})
        assert registration_queue.qsize() == 0

        sc.properties.pop("description")
        assert registration_queue.qsize() == 0

        sc.name = "my_scenario"
        assert registration_queue.qsize() == 0

        c.name = "another new cycle name"
        assert registration_queue.qsize() == 0

        c.properties["valid"] = True
        assert registration_queue.qsize() == 0

        c.properties.update({"re_run_periodically": True})
        assert registration_queue.qsize() == 0

        pl.properties["name"] = "weather_forecast"
        registration_queue.get()  # creation event due to Sequence was recreated
        assert registration_queue.qsize() == 0

        t.skippable = True
        assert registration_queue.qsize() == 0

        t.properties["number_of_run"] = 2
        assert registration_queue.qsize() == 0

        t.properties.update({"debug": True})
        assert registration_queue.qsize() == 0

        d.name = "another new datanode name"
        assert registration_queue.qsize() == 0

        d.properties["sorted"] = True
        assert registration_queue.qsize() == 0

        d.properties.update({"only_fetch_first_100": True})
        assert registration_queue.qsize() == 0

    published_events = []

    assert registration_queue.qsize() == 16
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_event_types = [
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.SCENARIO,
        EventEntityType.CYCLE,
        EventEntityType.CYCLE,
        EventEntityType.CYCLE,
        EventEntityType.SEQUENCE,
        EventEntityType.TASK,
        EventEntityType.TASK,
        EventEntityType.TASK,
        EventEntityType.DATA_NODE,
        EventEntityType.DATA_NODE,
        EventEntityType.DATA_NODE,
    ]
    expected_attribute_names = [
        "is_primary",
        "is_primary",
        "properties",
        "properties",
        "properties",
        "properties",
        "name",
        "properties",
        "properties",
        "properties",
        "skippable",
        "properties",
        "properties",
        "name",
        "properties",
        "properties",
    ]
    expected_event_entity_id = [
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        scenario.id,
        cycle.id,
        cycle.id,
        cycle.id,
        sequence.id,
        task.id,
        task.id,
        task.id,
        dn.id,
        dn.id,
        dn.id,
    ]

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == EventOperation.UPDATE
            and event.attribute_name == expected_attribute_names[i]
            for i, event in enumerate(published_events)
        ]
    )

    # Test SUBMISSION Event

    job = scenario.submit()[0]

    published_events = []
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_operations = [EventOperation.CREATION, EventOperation.UPDATE, EventOperation.SUBMISSION]
    expected_attribute_names = [None, "status", None]
    expected_event_types = [EventEntityType.JOB, EventEntityType.JOB, EventEntityType.SCENARIO]
    expected_event_entity_id = [job.id, job.id, scenario.id]

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == expected_operations[i]
            and event.attribute_name == expected_attribute_names[i]
            for i, event in enumerate(published_events)
        ]
    )

    # Test DELETION Event

    tp.delete(scenario.id)
    assert registration_queue.qsize() == 7

    published_events = []
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_event_types = [
        EventEntityType.SEQUENCE,
        EventEntityType.CYCLE,
        EventEntityType.SEQUENCE,
        EventEntityType.SCENARIO,
        # EventEntityType.SCENARIO,
        EventEntityType.TASK,
        EventEntityType.JOB,
        EventEntityType.DATA_NODE,
    ]

    expected_event_entity_id = [sequence.id, cycle.id, sequence.id, scenario.id, task.id, job.id, dn.id]
    expected_event_operation_type = [EventOperation.DELETION] * len(expected_event_types)
    expected_event_operation_type[0] = EventOperation.CREATION

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == expected_event_operation_type[i]
            and event.attribute_name is None
            for i, event in enumerate(published_events)
        ]
    )

    scenario = tp.create_scenario(scenario_config)
    cycle = scenario.cycle
    assert registration_queue.qsize() == 5

    # only to clear the queue
    while registration_queue.qsize() != 0:
        registration_queue.get()

    tp.clean_all_entities_by_version()
    assert registration_queue.qsize() == 5

    published_events = []
    while registration_queue.qsize() != 0:
        published_events.append(registration_queue.get())

    expected_event_types = [
        EventEntityType.JOB,
        EventEntityType.CYCLE,
        EventEntityType.SCENARIO,
        EventEntityType.TASK,
        EventEntityType.DATA_NODE,
    ]
    expected_event_entity_id = [None, cycle.id, scenario.id, None, None]

    assert all(
        [
            event.entity_type == expected_event_types[i]
            and event.entity_id == expected_event_entity_id[i]
            and event.operation == EventOperation.DELETION
            and event.attribute_name is None
            for i, event in enumerate(published_events)
        ]
    )
