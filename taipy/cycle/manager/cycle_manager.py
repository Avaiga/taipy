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
    The Cycle Manager is responsible for managing all the cycle-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting cycles.
    """

    repository = CycleRepository()

    def create(self, frequency: Frequency, name: str = None, creation_date: datetime = None, **properties):
        """
        Creates a new cycle.

        Parameters:
            frequency (Frequency): The frequency of the new cycle.
            name (str): The name of the new cycle. Default: `None`.
            creation_date (datetime): The date and time when the cycle is created. Default: `None`.
            properties (dict[str, str]): other properties. Default: `None`.
        """
        cycle = Cycle(frequency, properties, name=name, creation_date=creation_date)
        self.set(cycle)
        return cycle

    def set(self, cycle: Cycle):
        """
        Saves or updates a cycle.

        Parameters:
            cycle (Cycle): The cycle to save.
        """
        self.repository.save(cycle)

    def get(self, cycle_id: CycleId) -> Optional[Cycle]:
        """
        Gets the cycle corresponding to the identifier given as parameter.

        Parameters:
            cycle_id (CycleId): The identifier of the cycle to retrieve.
        Raises:
            ModelNotFound: if no cycle corresponds to `cycle_id`.
        """
        try:
            cycle = self.repository.load(cycle_id)
            return cycle
        except ModelNotFound:
            logging.error(f"Cycle entity: {cycle_id} does not exist.")
            raise NonExistingCycle(cycle_id)

    def get_or_create(self, frequency: Frequency, creation_date: datetime = None) -> Cycle:
        """
        Returns a cycle with the provided parameters.

        If no cycle already exists with the provided parameter values, a new cycle is created
        and returned.

        Parameters:
            frequency (Frequency): The frequency of the cycle.
            creation_date (datetime): The creation date of the cycle. Default value : `None`.

        Returns:
            Cycle: a cycle that has the indicated parameters. A new cycle may be created.
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
        Returns all the existing cycles.
        """
        return self.repository.load_all()

    def delete_all(self):
        """
        Deletes all cycles.
        """
        self.repository.delete_all()

    def delete(self, cycle_id: CycleId):
        """
        Deletes a cycle.

        Parameters:
            cycle_id (str): The identifier of the cycle to be deleted.
        Raises:
            ModelNotFound: if no cycle corresponds to `cycle_id`.
        """
        self.repository.delete(cycle_id)
