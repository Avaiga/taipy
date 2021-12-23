from enum import Enum


class Operator(Enum):
    """
    The operator of filtering of a Data Source.
    """

    EQUAL = 1
    NOTEQUAL = 2
    LESSER = 3
    LESSEROREQUAL = 4
    GREATER = 5
    GREATEROREQUAL = 6
