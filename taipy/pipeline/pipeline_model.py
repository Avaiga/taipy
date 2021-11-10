from dataclasses import dataclass

from dataclasses_json import dataclass_json

from taipy.common.alias import Dag, PipelineId


@dataclass_json
@dataclass
class PipelineModel:
    id: PipelineId
    name: str
    properties: dict
    source_task_edges: Dag
    task_source_edges: Dag
