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

from typing import Dict

from .._repository._abstract_converter import _AbstractConverter
from ..common import _utils
from ..task.task import Task
from .sequence import Sequence


class _SequenceConverter(_AbstractConverter):
    _SEQUENCE_MODEL_ID_KEY = "id"
    _SEQUENCE_MODEL_OWNER_ID_KEY = "owner_id"
    _SEQUENCE_MODEL_PARENT_IDS_KEY = "parent_ids"
    _SEQUENCE_MODEL_PROPERTIES_KEY = "properties"
    _SEQUENCE_MODEL_TASKS_KEY = "tasks"
    _SEQUENCE_MODEL_SUBSCRIBERS_KEY = "subscribers"
    _SEQUENCE_MODEL_VERSION_KEY = "version"

    @classmethod
    def _entity_to_model(cls, sequence: Sequence) -> Dict:
        return {
            "id": sequence.id,
            "owner_id": sequence.owner_id,
            "parent_ids": list(sequence._parent_ids),
            "properties": sequence._properties.data,
            "tasks": cls.__to_task_ids(sequence._tasks),
            "subscribers": _utils._fcts_to_dict(sequence._subscribers),
            "version": sequence._version,
        }

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]
