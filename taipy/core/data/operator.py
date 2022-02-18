from enum import Enum


class Operator(Enum):
    """
    The operator of filtering of a Data Node.
    """

    EQUAL = 1
    NOT_EQUAL = 2
    LESS_THAN = 3
    LESS_OR_EQUAL = 4
    GREATER_THAN = 5
    GREATER_OR_EQUAL = 6


class JoinOperator(Enum):
    AND = 1
    OR = 2
