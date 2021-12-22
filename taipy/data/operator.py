from enum import Enum


class Operator(Enum):
    """
    The operator of filtering of a Data Source.
    """

    EQUAL = 1
    LESSER = 2
    GREATER = 3
