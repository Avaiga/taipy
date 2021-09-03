from typing import NewType


Dag = NewType("Dag", dict[str, list[str]])
PipelineId = NewType("PipelineId", str)
