from enum import Enum


class Operator(Enum):
    """
    The operator of filtering of a Data Source.
    """

    EQUAL = 1
    NOT_EQUAL = 2
    LESS_THAN = 3
    LESS_OR_EQUAL = 4
    GREATER_THAN = 5
    GREATER_OR_EQUAL = 6
    AND = 7
    OR = 8
