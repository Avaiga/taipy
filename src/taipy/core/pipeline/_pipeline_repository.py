# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pathlib
from collections import defaultdict

from taipy.config.config import Config

from .._repository import _FileSystemRepository
from ..common import _utils
from ..common._utils import Subscriber
from ..exceptions.exceptions import NonExistingPipeline, NonExistingTask
from ..task.task import Task
from ._pipeline_model import _PipelineModel
from .pipeline import Pipeline


class _PipelineRepository(_FileSystemRepository[_PipelineModel, Pipeline]):
    def __init__(self):
        super().__init__(model=_PipelineModel, dir_name="pipelines")

    def _to_model(self, pipeline: Pipeline) -> _PipelineModel:
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
            pipeline.parent_id,
            pipeline.config_id,
            pipeline._properties.data,
            self.__to_task_ids(pipeline._tasks),
            _utils._fcts_to_dict(pipeline._subscribers),
        )

    def _from_model(self, model: _PipelineModel) -> Pipeline:
        try:
            pipeline = Pipeline(
                model.config_id,
                model.properties,
                model.tasks,
                model.id,
                model.parent_id,
                [
                    Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                    for it in model.subscribers
                ],  # type: ignore
            )
            return pipeline
        except NonExistingTask as err:
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(model.id)
            raise pipeline_err

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]
