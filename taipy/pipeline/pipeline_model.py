from dataclasses import dataclass
from typing import Dict, List, NewType

Dag = NewType("Dag", Dict[str, List[str]])
PipelineId = NewType("PipelineId", str)


@dataclass
class PipelineModel:
    id: PipelineId
    name: str
    properties: dict
    source_task_edges: Dag
    task_source_edges: Dag
