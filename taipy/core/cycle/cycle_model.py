import dataclasses
from dataclasses import dataclass
from typing import Any, Dict

from taipy.core.common.alias import CycleId
from taipy.core.common.frequency import Frequency


@dataclass
class CycleModel:
    id: CycleId
    name: str
    frequency: Frequency
    properties: Dict[str, Any]
    creation_date: str
    start_date: str
    end_date: str

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "frequency": repr(self.frequency)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return CycleModel(
            id=data["id"],
            name=data["name"],
            frequency=Frequency._from_repr(data["frequency"]),
            properties=data["properties"],
            creation_date=data["creation_date"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
