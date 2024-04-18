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

from __future__ import annotations

from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from taipy import CycleId, DataNodeId, JobId, ScenarioId, SequenceId, SubmissionId, TaskId


class _EntityIds:
    def __init__(self) -> None:
        self.data_node_ids: Set[DataNodeId] = set()
        self.task_ids: Set[TaskId] = set()
        self.scenario_ids: Set[ScenarioId] = set()
        self.sequence_ids: Set[SequenceId] = set()
        self.job_ids: Set[JobId] = set()
        self.cycle_ids: Set[CycleId] = set()
        self.submission_ids: Set[SubmissionId] = set()

    def __add__(self, other: _EntityIds):
        self.data_node_ids.update(other.data_node_ids)
        self.task_ids.update(other.task_ids)
        self.scenario_ids.update(other.scenario_ids)
        self.sequence_ids.update(other.sequence_ids)
        self.job_ids.update(other.job_ids)
        self.cycle_ids.update(other.cycle_ids)
        self.submission_ids.update(other.submission_ids)
        return self

    def __iadd__(self, other: _EntityIds):
        self.__add__(other)
        return self
