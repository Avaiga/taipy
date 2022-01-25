import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TaskModel:
    """Hold the model of a Task.

    A model refers to the structure of a Task stored in a database.
    The tuple `(config_name, parent_id)` forms a unique key.

    Attributes:
        id: Identifier of a Data Node.
        parent_id: Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        config_name: Name of the Data Node Config.
        input: Input data node of the Task, saved as its ID string representation.
        function_name: Name of the task function.
        function_module: Module name of the task function.
        output: Output data node of the Task, saved as its ID string representation.
    """

    id: str
    parent_id: Optional[str]
    config_name: str
    input_ids: List[str]
    function_name: str
    function_module: str
    output_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return TaskModel(
            id=data["id"],
            parent_id=data["parent_id"],
            config_name=data["config_name"],
            input_ids=data["input_ids"],
            function_name=data["function_name"],
            function_module=data["function_module"],
            output_ids=data["output_ids"],
        )
