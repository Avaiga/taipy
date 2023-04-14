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

import pytest

from src.taipy.core.exceptions.exceptions import NonExistingRegistration
from src.taipy.core.notification import EventEntityType, EventOperation, Notifier
from src.taipy.core.notification.event import Event
from src.taipy.core.notification.topic import Topic


def test_register():

    assert len(Notifier._registrations) == 0
    assert len(Notifier._topics_registrations_list) == 0

    register_id_0, register_queue_0 = Notifier.register()
    registration_0 = Notifier._registrations[register_id_0]
    topic_0 = registration_0.topic

    assert isinstance(register_id_0, str) and register_id_0 == registration_0.register_id
    assert isinstance(register_queue_0, SimpleQueue)
    assert len(Notifier._registrations) == 1
    assert len(Notifier._topics_registrations_list.keys()) == 1
    assert len(Notifier._topics_registrations_list[topic_0]) == 1
    assert registration_0.queue == register_queue_0 == Notifier._topics_registrations_list[topic_0][0].queue

    register_id_1, register_queue_1 = Notifier.register()
    registration_1 = Notifier._registrations[register_id_1]
    topic_1 = registration_1.topic

    assert isinstance(register_id_1, str) and register_id_1 == registration_1.register_id
    assert isinstance(register_queue_1, SimpleQueue)
    assert len(Notifier._registrations) == 2
    assert len(Notifier._topics_registrations_list.keys()) == 1
    assert len(Notifier._topics_registrations_list[topic_1]) == 2
    assert registration_1.queue == register_queue_1 == Notifier._topics_registrations_list[topic_1][1].queue

    register_id_2, register_queue_2 = Notifier.register(EventEntityType.SCENARIO)
    registration_2 = Notifier._registrations[register_id_2]
    topic_2 = registration_2.topic

    assert isinstance(register_id_2, str) and register_id_2 == registration_2.register_id
    assert isinstance(register_queue_2, SimpleQueue)
    assert len(Notifier._registrations) == 3
    assert len(Notifier._topics_registrations_list.keys()) == 2
    assert len(Notifier._topics_registrations_list[topic_2]) == 1
    assert registration_2.queue == register_queue_2 == Notifier._topics_registrations_list[topic_2][0].queue

    register_id_3, register_queue_3 = Notifier.register(EventEntityType.SCENARIO, "scenario_id")
    registration_3 = Notifier._registrations[register_id_3]
    topic_3 = registration_3.topic

    assert isinstance(register_id_3, str) and register_id_3 == registration_3.register_id
    assert isinstance(register_queue_3, SimpleQueue)
    assert len(Notifier._registrations) == 4
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert len(Notifier._topics_registrations_list[topic_3]) == 1
    assert registration_3.queue == register_queue_3 == Notifier._topics_registrations_list[topic_3][0].queue

    register_id_4, register_queue_4 = Notifier.register(
        EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"
    )
    registration_4 = Notifier._registrations[register_id_4]
    topic_4 = registration_4.topic

    assert isinstance(register_id_4, str) and register_id_4 == registration_4.register_id
    assert isinstance(register_queue_4, SimpleQueue)
    assert len(Notifier._registrations) == 5
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_4]) == 1
    assert registration_4.queue == register_queue_4 == Notifier._topics_registrations_list[topic_4][0].queue

    register_id_5, register_queue_4 = Notifier.register(EventEntityType.SCENARIO)
    registration_5 = Notifier._registrations[register_id_5]
    topic_5 = registration_5.topic

    assert isinstance(register_id_5, str) and register_id_5 == registration_5.register_id
    assert isinstance(register_queue_4, SimpleQueue)
    assert len(Notifier._registrations) == 6
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_5]) == 2
    assert registration_5.queue == register_queue_4 == Notifier._topics_registrations_list[topic_5][1].queue

    register_id_6, register_queue_6 = Notifier.register()
    assert len(Notifier._registrations) == 7
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_0]) == 3

    Notifier.unregister(register_id_6)
    assert len(Notifier._registrations) == 6
    assert len(Notifier._topics_registrations_list.keys()) == 4
    assert len(Notifier._topics_registrations_list[topic_0]) == 2

    Notifier.unregister(register_id_4)
    assert len(Notifier._registrations) == 5
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert topic_4 not in Notifier._topics_registrations_list.keys()

    Notifier.unregister(register_id_0)
    assert len(Notifier._registrations) == 4
    assert len(Notifier._topics_registrations_list.keys()) == 3
    assert len(Notifier._topics_registrations_list[topic_0]) == 1

    Notifier.unregister(register_id_1)
    assert len(Notifier._registrations) == 3
    assert len(Notifier._topics_registrations_list.keys()) == 2
    assert all(topic not in Notifier._topics_registrations_list.keys() for topic in [topic_0, topic_1])

    Notifier.unregister(register_id_2)
    Notifier.unregister(register_id_3)
    Notifier.unregister(register_id_5)
    assert len(Notifier._registrations) == 0
    assert len(Notifier._topics_registrations_list.keys()) == 0

    with pytest.raises(NonExistingRegistration):
        Notifier.unregister(register_id_0)


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

    assert Notifier.is_matching(Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"), Topic())
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"), Topic(EventEntityType.PIPELINE)
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(
            EventEntityType.PIPELINE,
            "pipeline_id",
        ),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(operation=EventOperation.UPDATE),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"), Topic(attribute_name="tasks")
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.PIPELINE, attribute_name="tasks"),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(operation=EventOperation.UPDATE, attribute_name="tasks"),
    )
    assert Notifier.is_matching(
        Event(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
        Topic(EventEntityType.PIPELINE, "pipeline_id", EventOperation.UPDATE, "tasks"),
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
