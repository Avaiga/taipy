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

import dataclasses
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ... import Task
from .._version._utils import _version_migration
from ..common import _utils
from ..common._utils import _Subscriber
from ..common.alias import PipelineId, TaskId
from ..exceptions import NonExistingPipeline, NonExistingTask
from ..pipeline.pipeline import Pipeline


@dataclass
class _PipelineModel:
    id: PipelineId
    owner_id: Optional[str]
    parent_ids: List[str]
    config_id: str
    properties: Dict[str, Any]
    tasks: List[TaskId]
    subscribers: List[Dict]
    version: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _PipelineModel(
            id=data["id"],
            config_id=data["config_id"],
            owner_id=data.get("owner_id", data.get("parent_id")),
            parent_ids=data.get("parent_ids", []),
            properties=data["properties"],
            tasks=data["tasks"],
            subscribers=data["subscribers"],
            version=data["version"] if "version" in data.keys() else _version_migration(),
        )

    def _to_entity(self) -> Pipeline:
        try:
            pipeline = Pipeline(
                self.config_id,
                self.properties,
                self.tasks,
                self.id,
                self.owner_id,
                set(self.parent_ids),
                [
                    _Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                    for it in self.subscribers
                ],  # type: ignore
                self.version,
            )
            return pipeline
        except NonExistingTask as err:
            raise err
        except KeyError:
            pipeline_err = NonExistingPipeline(self.id)
            raise pipeline_err

    @classmethod
    def _from_entity(cls, pipeline: Pipeline) -> "_PipelineModel":
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
            _utils._fcts_to_dict(pipeline._subscribers),
            pipeline.version,
        )

    @staticmethod
    def __to_task_ids(tasks):
        return [t.id if isinstance(t, Task) else t for t in tasks]
