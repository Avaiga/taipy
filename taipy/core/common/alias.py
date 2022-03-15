from typing import NewType

PipelineId = NewType("PipelineId", str)
PipelineId.__doc__ = """Type that holds a `Pipeline^` identifier."""
ScenarioId = NewType("ScenarioId", str)
ScenarioId.__doc__ = """Type that holds a `Scenario^` identifier."""
TaskId = NewType("TaskId", str)
TaskId.__doc__ = """Type that holds a `Task^` identifier."""
JobId = NewType("JobId", str)
JobId.__doc__ = """Type that holds a `Job^` identifier."""
CycleId = NewType("CycleId", str)
CycleId.__doc__ = """Type that holds a `Cycle^` identifier."""
DataNodeId = NewType("DataNodeId", str)
DataNodeId.__doc__ = """Type that holds a `DataNode^` identifier."""
