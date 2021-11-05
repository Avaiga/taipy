from enum import Enum


class Status(Enum):
    """
    Class to represent the status of a Job
    """

    SUBMITTED = 1
    BLOCKED = 2
    PENDING = 3
    RUNNING = 4
    CANCELLED = 5
    FAILED = 6
    COMPLETED = 7
