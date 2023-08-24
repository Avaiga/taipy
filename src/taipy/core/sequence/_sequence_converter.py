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
from collections import defaultdict

from .._repository._abstract_converter import _AbstractConverter
from ..common import _utils
from ..exceptions import NonExistingSequence, NonExistingTask
from ..task.task import Task
from ._sequence_model import _SequenceModel
from .sequence import Sequence


class _SequenceConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, sequence: Sequence) -> _SequenceModel:
        datanode_task_edges = defaultdict(list)
        task_datanode_edges = defaultdict(list)

        for task in sequence._get_tasks().values():
            task_id = str(task.id)
            for predecessor in task.input.values():
                datanode_task_edges[str(predecessor.id)].append(task_id)
            for successor in task.output.values():
                task_datanode_edges[task_id].append(str(successor.id))
        return _SequenceModel(
            sequence.id,
            sequence.owner_id,
            list(sequence._parent_ids),
            sequence._properties.data,
            cls.__to_task_ids(sequence._tasks),
            _utils._fcts_to_dict(sequence._subscribers),
            sequence._version,
        )

    @classmethod
    def _model_to_entity(cls, model: _SequenceModel) -> Sequence:
        try:
            sequence = Sequence(
                model.properties,
                model.tasks,
                model.id,
                model.owner_id,
                set(model.parent_ids),
                [
                    _utils._Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                    for it in model.subscribers
                ],
                model.version,
            )
            return sequence
        except NonExistingTask as err:
            raise err
        except KeyError:
            sequence_err = NonExistingSequence(model.id)
            raise sequence_err

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]
