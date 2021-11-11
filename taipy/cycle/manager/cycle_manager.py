import logging
from datetime import datetime
from typing import Optional

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency
from taipy.cycle.repository import CycleRepository
from taipy.exceptions.cycle import NonExistingCycle
from taipy.exceptions.repository import ModelNotFound


class CycleManager:
    repository = CycleRepository()

    def create(self, name: str, frequency: Frequency, **properties):
        cycle = Cycle(name, frequency, properties, creation_date=datetime.now())
        self.set(cycle)
        return cycle

    def set(self, cycle: Cycle):
        self.repository.save(cycle)

    def get(self, cycle_id: CycleId) -> Optional[Cycle]:
        try:
            cycle = self.repository.load(cycle_id)
            return cycle
        except Exception:
            logging.error(f"Cycle entity : {cycle_id} does not exist.")
            raise NonExistingCycle(cycle_id)

    def get_all(self):
        return self.repository.load_all()

    def delete_all(self):
        self.repository.delete_all()

    def delete(self, cycle_id: CycleId):
        self.repository.delete(cycle_id)

    def save(self, cycle: Cycle):
        self.repository.save(cycle)
