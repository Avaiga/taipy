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

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import PipelineId, TaskId


@dataclass
class _PipelineModel:

    id: PipelineId
    parent_id: Optional[str]
    config_id: str
    properties: Dict[str, Any]
    tasks: List[TaskId]
    subscribers: List[Dict]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _PipelineModel(
            id=data["id"],
            config_id=data["config_id"],
            parent_id=data["parent_id"],
            properties=data["properties"],
            tasks=data["tasks"],
            subscribers=data["subscribers"],
        )
