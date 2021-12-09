import logging
from datetime import datetime
from typing import List, Optional

from taipy.common.alias import CycleId
from taipy.cycle.cycle import Cycle
from taipy.cycle.frequency import Frequency
from taipy.cycle.repository import CycleRepository
from taipy.exceptions.cycle import CycleAlreadyExists, NonExistingCycle
from taipy.exceptions.repository import ModelNotFound


class CycleManager:
    """
    Cycle Manager is responsible for all managing cycle related capabilities. In particular, it is exposing
    methods for creating, storing, updating, retrieving, deleting cycle.
    """

    repository = CycleRepository()

    def create(self, frequency: Frequency, name: str = None, creation_date: datetime = None, **properties):
        """
        Creates a new cycle from the provided information (frequency, name, creation date and properties)
        Parameters:
            frequency (Frequency): frequency of the cycle
            name (str): custom name of the cycle. Default: None
            creation_date (datetime): date and time the cycle is created. Default: None
            properties (dict[str, str]): other properties. Default: None
        """
        cycle = Cycle(frequency, properties, name=name, creation_date=creation_date)
        self.set(cycle)
        return cycle

    def set(self, cycle: Cycle):
        """
        Saves or Updates the cycle given as parameter
        Parameters:
            cycle (Cycle): cycle to save.
        """
        self.repository.save(cycle)

    def get(self, cycle_id: CycleId) -> Optional[Cycle]:
        """
        Gets the cycle corresponding to the identifier given as parameter.
        Parameters:
            cycle_id (CycleId): cycle to get.
        Raises:
            ModelNotFound error if no cycle corresponds to cycle_id.
        """
        try:
            cycle = self.repository.load(cycle_id)
            return cycle
        except ModelNotFound:
            logging.error(f"Cycle entity : {cycle_id} does not exist.")
            raise NonExistingCycle(cycle_id)

    def get_or_create(self, frequency: Frequency, creation_date: datetime = None) -> Cycle:
        """
        Returns the cycle created by frequency and creation_date if it already
        exists, or creates and returns a new cycle.
        Parameters:
            frequency (Frequency): creation_date of the cycle.
            creation_date (datetime): creation date of the cycle. Default value : None.
        """
        creation_date = creation_date if creation_date else datetime.now()
        cycles = self.repository.get_cycles_by_frequency_and_creation_date(
            frequency=frequency, creation_date=creation_date
        )
        if len(cycles) > 0:
            return cycles[0]
        else:
            return self.create(frequency=frequency, creation_date=creation_date)

    def get_all(self):
        """
        Returns the list of all existing cycles.
        """
        return self.repository.load_all()

    def delete_all(self):
        """
        Deletes all cycles.
        """
        self.repository.delete_all()

    def delete(self, cycle_id: CycleId):
        """
        Deletes the cycle provided as parameter.
        Parameters:
            cycle_id (str): identifier of the cycle to delete.
        Raises:
            ModelNotFound error if no cycle corresponds to cycle_id.
        """
        self.repository.delete(cycle_id)
