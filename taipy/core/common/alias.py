from typing import Dict, List, NewType

PipelineId = NewType("PipelineId", str)
Dag = NewType("Dag", Dict[str, List[str]])
ScenarioId = NewType("ScenarioId", str)
TaskId = NewType("TaskId", str)
JobId = NewType("JobId", str)
CycleId = NewType("CycleId", str)
DataNodeId = NewType("DataNodeId", str)
