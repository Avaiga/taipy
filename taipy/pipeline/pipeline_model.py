from dataclasses import dataclass

from taipy.pipeline import PipelineId
from taipy.pipeline.pipeline import Dag


@dataclass
class PipelineModel:
    id: PipelineId
    name: str
    properties: dict
    source_task_edges: Dag
    task_source_edges: Dag
