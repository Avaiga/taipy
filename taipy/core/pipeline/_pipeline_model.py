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
