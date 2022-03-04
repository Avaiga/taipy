import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import Dag, PipelineId, TaskId


@dataclass
class PipelineModel:
    """
    Class to hold a model of a Pipeline.

    A model refers to the structure of a Pipeline stored in a database.

    Attributes:
        id (PipelineId): Identifier of a Pipeline.
        config_id (str): Identifier of the pipeline configuration.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        properties(dict): List of additional arguments.
    """

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
        return PipelineModel(
            id=data["id"],
            config_id=data["config_id"],
            parent_id=data["parent_id"],
            properties=data["properties"],
            tasks=data["tasks"],
            subscribers=data["subscribers"],
        )
