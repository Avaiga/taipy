import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class _TaskModel:

    id: str
    parent_id: Optional[str]
    config_id: str
    input_ids: List[str]
    function_name: str
    function_module: str
    output_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _TaskModel(
            id=data["id"],
            parent_id=data["parent_id"],
            config_id=data["config_id"],
            input_ids=data["input_ids"],
            function_name=data["function_name"],
            function_module=data["function_module"],
            output_ids=data["output_ids"],
        )
