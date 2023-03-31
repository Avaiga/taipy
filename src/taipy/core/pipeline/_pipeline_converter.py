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

from .._repository._v2._abstract_converter import _AbstractConverter
from .._version._utils import _migrate_entity
from ..common._utils import _fcts_to_dict, _load_fct, _Subscriber
from ..exceptions import NonExistingPipeline, NonExistingTask
from ..pipeline._pipeline_model import _PipelineModel
from ..pipeline.pipeline import Pipeline
from ..task.task import Task


class _PipelineConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, pipeline: Pipeline) -> _PipelineModel:
        datanode_task_edges = defaultdict(list)
        task_datanode_edges = defaultdict(list)

        for task in pipeline._get_tasks().values():
            task_id = str(task.id)
            for predecessor in task.input.values():
                datanode_task_edges[str(predecessor.id)].append(task_id)
            for successor in task.output.values():
                task_datanode_edges[task_id].append(str(successor.id))
        return _PipelineModel(
            pipeline.id,
            pipeline.owner_id,
            list(pipeline._parent_ids),
            pipeline.config_id,
            pipeline._properties.data,
            cls.__to_task_ids(pipeline._tasks),
            _fcts_to_dict(pipeline._subscribers),
            pipeline.version,
        )

    @classmethod
    def _model_to_entity(cls, model: _PipelineModel) -> Pipeline:
        try:
            pipeline = Pipeline(
                model.config_id,
                model.properties,
                model.tasks,
                model.id,
                model.owner_id,
                set(model.parent_ids),
                [
                    _Subscriber(_load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                    for it in model.subscribers
                ],
                model.version,
            )
            return _migrate_entity(pipeline)
        except NonExistingTask as err:
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(model.id)
            raise pipeline_err

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]
