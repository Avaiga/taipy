from typing import Dict, List, NewType

Dag = NewType("Dag", Dict[str, List[str]])
PipelineId = NewType("PipelineId", str)
