import calendar
from datetime import datetime, time, timedelta
from typing import Optional

from taipy.core.common._manager import _Manager
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.alias import CycleId
from taipy.core.common.frequency import Frequency
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_repository import CycleRepository
from taipy.core.exceptions.repository import ModelNotFound


class CycleManager(_Manager[Cycle]):
    """
    The Cycle Manager is responsible for managing all the cycle-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting cycles.
    """

    _repository = CycleRepository()
    ENTITY_NAME = Cycle.__name__

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
        cls._set(cycle)
        return cycle

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
        cycles = cls._repository.get_cycles_by_frequency_and_start_date(frequency=frequency, start_date=start_date)
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
