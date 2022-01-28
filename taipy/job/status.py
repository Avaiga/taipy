from taipy.common.repr_enum import ReprEnum


class Status(ReprEnum):
    """Enumeration representing the execution status of a Job. The possible values are SUBMITTED, BLOCKED, PENDING,
    RUNNING, CANCELLED, FAILED, COMPLETED
    """

    SUBMITTED = 1
    BLOCKED = 2
    PENDING = 3
    RUNNING = 4
    CANCELLED = 5
    FAILED = 6
    COMPLETED = 7
