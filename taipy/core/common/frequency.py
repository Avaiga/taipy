from taipy.core.common._repr_enum import _ReprEnum


class Frequency(_ReprEnum):
    """
    The frequency of a cycle and the recurrence of Scenarios.

    It is implemented as an enumeration. The possible values are DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY.
    """

    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    QUARTERLY = 4
    YEARLY = 5
