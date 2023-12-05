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

from taipy.core.sequence._sequence_converter import _SequenceConverter
from taipy.core.sequence.sequence import Sequence
from taipy.core.task.task import Task


def test_entity_to_model(sequence):
    sequence_model_1 = _SequenceConverter._entity_to_model(sequence)
    expected_sequence_model_1 = {
        "id": "sequence_id",
        "owner_id": "owner_id",
        "parent_ids": ["parent_id_1", "parent_id_2"],
        "properties": {},
        "tasks": [],
        "subscribers": [],
        "version": "random_version_number",
    }
    sequence_model_1["parent_ids"] = sorted(sequence_model_1["parent_ids"])
    assert sequence_model_1 == expected_sequence_model_1

    task_1 = Task("task_1", {}, print)
    task_2 = Task("task_2", {}, print)
    sequence_2 = Sequence(
        {"name": "sequence_2"},
        [task_1, task_2],
        "SEQUENCE_sq_1_SCENARIO_sc",
        "SCENARIO_sc",
        ["SCENARIO_sc"],
        [],
        "random_version",
    )
    sequence_model_2 = _SequenceConverter._entity_to_model(sequence_2)
    expected_sequence_model_2 = {
        "id": "SEQUENCE_sq_1_SCENARIO_sc",
        "owner_id": "SCENARIO_sc",
        "parent_ids": ["SCENARIO_sc"],
        "properties": {"name": "sequence_2"},
        "tasks": [task_1.id, task_2.id],
        "subscribers": [],
        "version": "random_version",
    }
    assert sequence_model_2 == expected_sequence_model_2
