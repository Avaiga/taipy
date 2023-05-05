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

import pathlib
from collections import defaultdict
from typing import Any, Iterable, List, Optional, Union

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ..common import _utils
from ..common._utils import _Subscriber
from ..exceptions.exceptions import NonExistingPipeline, NonExistingTask
from ..task.task import Task
from ._pipeline_model import _PipelineModel
from .pipeline import Pipeline


class _PipelineRepository(_AbstractRepository[_PipelineModel, Pipeline]):  # type: ignore
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

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
            pipeline.owner_id,
            list(pipeline._parent_ids),
            pipeline.config_id,
            pipeline._properties.data,
            self.__to_task_ids(pipeline._tasks),
            _utils._fcts_to_dict(pipeline._subscribers),
            pipeline.version,
        )

    def _from_model(self, model: _PipelineModel) -> Pipeline:
        try:
            pipeline = Pipeline(
                model.config_id,
                model.properties,
                model.tasks,
                model.id,
                model.owner_id,
                set(model.parent_ids),
                [
                    _Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                    for it in model.subscribers
                ],  # type: ignore
                model.version,
            )
            return pipeline
        except NonExistingTask as err:
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(model.id)
            raise pipeline_err

    def load(self, model_id: str) -> Pipeline:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[Pipeline]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[Pipeline]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: Pipeline):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        return self.repo._delete_by(attribute, value, version_number)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[Pipeline]:
        return self.repo._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(entity_id, folder_path)

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]

    def _get_by_config_id(self, config_id: str) -> List[Pipeline]:
        return self.repo._get_by_config_id(config_id)
