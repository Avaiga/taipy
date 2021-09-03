from dataclasses import dataclass

from taipy.pipeline.types import PipelineId, Dag


@dataclass
class PipelineModel:
    id: PipelineId
    name: str
    properties: dict
    source_task_edges: Dag
    task_source_edges: Dag
