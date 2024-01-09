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

from typing import Union

from .._entity._entity import _Entity
from ..cycle.cycle import Cycle
from ..data.data_node import DataNode
from ..job.job import Job
from ..scenario.scenario import Scenario
from ..sequence.sequence import Sequence
from ..submission.submission import Submission
from ..task.task import Task


def _is_cycle(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Cycle) or (isinstance(entity, str) and entity.startswith(Cycle._ID_PREFIX))


def _is_scenario(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Scenario) or (isinstance(entity, str) and entity.startswith(Scenario._ID_PREFIX))


def _is_sequence(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Sequence) or (isinstance(entity, str) and entity.startswith(Sequence._ID_PREFIX))


def _is_task(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Task) or (isinstance(entity, str) and entity.startswith(Task._ID_PREFIX))


def _is_job(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Job) or (isinstance(entity, str) and entity.startswith(Job._ID_PREFIX))


def _is_data_node(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, DataNode) or (isinstance(entity, str) and entity.startswith(DataNode._ID_PREFIX))


def _is_submission(entity: Union[_Entity, str]) -> bool:
    return isinstance(entity, Submission) or (isinstance(entity, str) and entity.startswith(Submission._ID_PREFIX))
