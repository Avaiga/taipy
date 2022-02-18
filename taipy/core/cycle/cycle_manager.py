import calendar
import logging
from datetime import datetime, time, timedelta
from typing import Optional

from taipy.core.common.alias import CycleId
from taipy.core.common.frequency import Frequency
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_repository import CycleRepository
from taipy.core.exceptions.cycle import NonExistingCycle
from taipy.core.exceptions.repository import ModelNotFound


class CycleManager:
    """
    The Cycle Manager is responsible for managing all the cycle-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting cycles.
    """

    repository = CycleRepository()

    @classmethod
    def create(
        cls, frequency: Frequency, name: str = None, creation_date: datetime = None, display_name=None, **properties
    ):
        """
        Creates a new cycle.

        Parameters:
            frequency (Frequency): The frequency of the new cycle.
            name (str): The name of the new cycle. Default: `None`.
            creation_date (datetime): The date and time when the cycle is created. Default: `None`.
            display_name (Optional[str]): The display name of the cycle.
            properties (dict[str, str]): other properties. Default: `None`.
        """
        creation_date = creation_date if creation_date else datetime.now()
        start_date = CycleManager.get_start_date_of_cycle(frequency, creation_date)
        end_date = CycleManager.get_end_date_of_cycle(frequency, start_date)
        properties["display_name"] = display_name if display_name else start_date.isoformat()
        cycle = Cycle(
            frequency, properties, creation_date=creation_date, start_date=start_date, end_date=end_date, name=name
        )
        cls.set(cycle)
        return cycle

    @classmethod
    def set(cls, cycle: Cycle):
        """
        Saves or updates a cycle.

        Parameters:
            cycle (Cycle): The cycle to save.
        """
        cls.repository.save(cycle)

    @classmethod
    def get(cls, cycle_id: CycleId, default=None) -> Cycle:
        """
        Gets the cycle corresponding to the identifier given as parameter.

        Parameters:
            cycle_id (CycleId): The identifier of the cycle to retrieve.
            default: Default value to return if no cycle is found. None is returned if no default value is provided.
        """
        try:
            return cls.repository.load(cycle_id)
        except ModelNotFound:
            logging.error(f"Cycle entity: {cycle_id} does not exist.")
            return default

    @classmethod
    def get_or_create(
        cls, frequency: Frequency, creation_date: Optional[datetime] = None, display_name: Optional[str] = None
    ) -> Cycle:
        """
        Returns a cycle with the provided parameters.

        If no cycle already exists with the provided parameter values, a new cycle is created
        and returned.

        Parameters:
            frequency (Frequency): The frequency of the cycle.
            creation_date (Optional[datetime]): The creation date of the cycle. Default value : `None`.
            display_name (Optional[str]): The display name of the cycle.
        Returns:
            Cycle: a cycle that has the indicated parameters. A new cycle may be created.
        """
        creation_date = creation_date if creation_date else datetime.now()
        start_date = CycleManager.get_start_date_of_cycle(frequency, creation_date)
        cycles = cls.repository.get_cycles_by_frequency_and_start_date(frequency=frequency, start_date=start_date)
        if len(cycles) > 0:
            return cycles[0]
        else:
            return cls.create(frequency=frequency, creation_date=creation_date, display_name=display_name)

    @staticmethod
    def get_start_date_of_cycle(frequency: Frequency, creation_date: datetime):
        start_date = creation_date.date()
        start_time = time()
        if frequency == Frequency.DAILY:
            start_date = start_date
        if frequency == Frequency.WEEKLY:
            start_date = start_date - timedelta(days=start_date.weekday())
        if frequency == Frequency.MONTHLY:
            start_date = start_date.replace(day=1)
        if frequency == Frequency.YEARLY:
            start_date = start_date.replace(day=1, month=1)
        return datetime.combine(start_date, start_time)

    @staticmethod
    def get_end_date_of_cycle(frequency: Frequency, start_date: datetime):
        end_date = start_date
        if frequency == Frequency.DAILY:
            end_date = end_date + timedelta(days=1)
        if frequency == Frequency.WEEKLY:
            end_date = end_date + timedelta(7 - end_date.weekday())
        if frequency == Frequency.MONTHLY:
            last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
            end_date = end_date.replace(day=last_day_of_month) + timedelta(days=1)
        if frequency == Frequency.YEARLY:
            end_date = end_date.replace(month=12, day=31) + timedelta(days=1)
        return end_date - timedelta(microseconds=1)

    @classmethod
    def get_all(cls):
        """
        Returns all the existing cycles.
        """
        return cls.repository.load_all()

    @classmethod
    def delete_all(cls):
        """
        Deletes all cycles.
        """
        cls.repository.delete_all()

    @classmethod
    def delete(cls, cycle_id: CycleId):
        """
        Deletes a cycle.

        Parameters:
            cycle_id (str): The identifier of the cycle to be deleted.
        Raises:
            ModelNotFound: if no cycle corresponds to `cycle_id`.
        """
        cls.repository.delete(cycle_id)
