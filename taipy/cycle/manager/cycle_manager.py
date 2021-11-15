import logging
from datetime import datetime
from typing import List, Optional

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency
from taipy.cycle.repository import CycleRepository
from taipy.exceptions.cycle import NonExistingCycle
from taipy.exceptions.repository import ModelNotFound


class CycleManager:
    repository = CycleRepository()

    def create(self, frequency: Frequency, name: str = None, creation_date: datetime = None, **properties):
        cycle = Cycle(frequency, properties, name=name, creation_date=creation_date)
        self.set(cycle)
        return cycle

    def set(self, cycle: Cycle):
        self.repository.save(cycle)

    def get(self, cycle_id: CycleId) -> Optional[Cycle]:
        try:
            cycle = self.repository.load(cycle_id)
            return cycle
        except ModelNotFound:
            logging.error(f"Cycle entity : {cycle_id} does not exist.")
            raise NonExistingCycle(cycle_id)

    def get_or_create(self, frequency: Frequency, creation_date: datetime = None):
        # TODO: return the existing cycle
        creation_date = creation_date if creation_date else datetime.now()
        cycles = self.cycle_exists(frequency=frequency, creation_date=creation_date)
        if len(cycles) > 0:
            return cycles[0]
        else:
            return self.create(frequency=frequency, creation_date=creation_date)

    def cycle_exists(self, frequency: Frequency, creation_date: datetime) -> List[Cycle]:
        cycles_by_frequency = self.get_cycles_by_frequency(frequency)
        cycles_by_creation_date = self.get_cycles_by_creation_date(creation_date)
        return list(set(cycles_by_frequency) & set(cycles_by_creation_date))

    def get_cycles_by_frequency_and_overlapping_date(self, frequency: Frequency, date=datetime) -> List[Cycle]:
        cycles_by_frequency = self.get_cycles_by_frequency(frequency)
        cycles_by_overlapping_date = self.get_cycles_with_overlapping_date(date)
        return list(set(cycles_by_frequency) & set(cycles_by_overlapping_date))

    def get_cycles_by_creation_date(self, creation_date: datetime) -> List[Cycle]:
        return [cycle.creation_date == creation_date and cycle for cycle in self.get_all()]

    def get_cycles_by_frequency(self, frequency: Frequency) -> List[Cycle]:
        return [cycle.frequency == frequency and cycle for cycle in self.get_all()]

    def get_cycles_with_overlapping_date(self, date=datetime) -> List[Cycle]:
        return [cycle.start_date <= date <= cycle.end_date and cycle for cycle in self.get_all()]

    def get_all(self):
        return self.repository.load_all()

    def delete_all(self):
        self.repository.delete_all()

    def delete(self, cycle_id: CycleId):
        self.repository.delete(cycle_id)
