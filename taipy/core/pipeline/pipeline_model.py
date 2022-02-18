import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import Dag, PipelineId


@dataclass
class PipelineModel:
    """
    Class to hold a model of a Pipeline.

    A model refers to the structure of a Pipeline stored in a database.

    Attributes:
        id (PipelineId): identifier of a Pipeline.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        name (str): name of the pipeline.
        properties(dict): List of additional arguments.
    """

    id: PipelineId
    parent_id: Optional[str]
    name: str
    properties: Dict[str, Any]
    datanode_task_edges: Dag
    task_datanode_edges: Dag
    subscribers: List[Dict]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return PipelineModel(
            id=data["id"],
            parent_id=data["parent_id"],
            name=data["name"],
            properties=data["properties"],
            datanode_task_edges=data["datanode_task_edges"],
            task_datanode_edges=data["task_datanode_edges"],
            subscribers=data["subscribers"],
        )
