from typing import NewType, Dict, List

PipelineId = NewType("PipelineId", str)
Dag = NewType("Dag", Dict[str, List[str]])
ScenarioId = NewType("ScenarioId", str)
TaskId = NewType("TaskId", str)
