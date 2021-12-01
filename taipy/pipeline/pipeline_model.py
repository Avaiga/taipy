from dataclasses import dataclass
from typing import Dict, List, Optional

from dataclasses_json import dataclass_json

from taipy.common.alias import Dag, PipelineId


@dataclass_json
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
    properties: dict
    source_task_edges: Dag
    task_source_edges: Dag
    subscribers: List[Dict]
