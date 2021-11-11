from datetime import datetime

from taipy.cycle.cycle import Cycle
from taipy.cycle.cycle_model import CycleModel
from taipy.repository import FileSystemRepository


class CycleRepository(FileSystemRepository[CycleModel, Cycle]):
    def __init__(self, dir_name="cycles"):
        super().__init__(model=CycleModel, dir_name=dir_name)

    def to_model(self, cycle: Cycle) -> CycleModel:
        return CycleModel(
            id=cycle.id,
            name=cycle.name,
            frequency=cycle.frequency,
            creation_date=cycle.creation_date.isoformat(),
            start_date=cycle.start_date.isoformat() if cycle.start_date else None,
            end_date=cycle.end_date.isoformat() if cycle.end_date else None,
            properties=cycle.properties,
        )

    def from_model(self, model: CycleModel) -> Cycle:
        return Cycle(
            id=model.id,
            name=model.name,
            frequency=model.frequency,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            start_date=datetime.fromisoformat(model.start_date) if model.start_date else None,
            end_date=datetime.fromisoformat(model.end_date) if model.end_date else None,
        )
