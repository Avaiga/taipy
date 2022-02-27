import pathlib
from datetime import datetime
from typing import List

from taipy.core.cycle.cycle import Cycle  # isort:skip
from taipy.core.cycle.cycle_model import CycleModel  # isort:skip
from taipy.core.common.frequency import Frequency  # isort:skip
from taipy.core.repository import FileSystemRepository  # isort:skip
from taipy.core.config.config import Config  # isort:skip


class CycleRepository(FileSystemRepository[CycleModel, Cycle]):
    def __init__(self):
        super().__init__(model=CycleModel, dir_name="cycles")

    def to_model(self, cycle: Cycle) -> CycleModel:
        return CycleModel(
            id=cycle.id,
            name=cycle.name,
            frequency=cycle.frequency,
            creation_date=cycle.creation_date.isoformat(),
            start_date=cycle.start_date.isoformat(),
            end_date=cycle.end_date.isoformat(),
            properties=cycle.properties.data,
        )

    def from_model(self, model: CycleModel) -> Cycle:
        return Cycle(
            id=model.id,
            name=model.name,
            frequency=model.frequency,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            start_date=datetime.fromisoformat(model.start_date),
            end_date=datetime.fromisoformat(model.end_date),
        )

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    def get_cycles_by_frequency_and_start_date(self, frequency: Frequency, start_date: datetime) -> List[Cycle]:
        cycles_by_frequency = self.__get_cycles_by_frequency(frequency)
        cycles_by_start_date = self.__get_cycles_by_start_date(start_date)
        return list(set(cycles_by_frequency) & set(cycles_by_start_date))

    def get_cycles_by_frequency_and_overlapping_date(self, frequency: Frequency, date=datetime) -> List[Cycle]:
        cycles_by_frequency = self.__get_cycles_by_frequency(frequency)
        cycles_by_overlapping_date = self.__get_cycles_with_overlapping_date(date)
        return list(set(cycles_by_frequency) & set(cycles_by_overlapping_date))

    def __get_cycles_by_start_date(self, start_date: datetime) -> List[Cycle]:
        cycles_by_start_date = []
        for cycle in self.load_all():
            if cycle.start_date == start_date:
                cycles_by_start_date.append(cycle)
        return cycles_by_start_date

    def __get_cycles_by_frequency(self, frequency: Frequency) -> List[Cycle]:
        cycles_by_frequency = []
        for cycle in self.load_all():
            if cycle.frequency == frequency:
                cycles_by_frequency.append(cycle)
        return cycles_by_frequency

    def __get_cycles_with_overlapping_date(self, date=datetime) -> List[Cycle]:
        cycles_by_overlapping_date = []
        for cycle in self.load_all():
            if cycle.start_date <= date <= cycle.end_date:
                cycles_by_overlapping_date.append(cycle)
        return cycles_by_overlapping_date
